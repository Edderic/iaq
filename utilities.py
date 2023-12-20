from skimage.io import imread
import pandas as pd
import matplotlib.pyplot as plt

def hmff(column):
    """
    Compute harmonic mean fit factor, which is a conservative way to average
    out fit factors across different exercises.
    """
    denominator = (1 / column).sum()
    numerator = column.notna().sum()

    return numerator / denominator


def bar_plot_exposure_reduction_factors(df, img_func, figsize=None, ylim=None):
    if figsize is None:
        figsize = (8,7)

    if ylim is None:
        ylim = (0, 150)

    fig, ax = plt.subplots(figsize=figsize)
    df.plot.bar(x='protection', y='exposure reduction factor', ax=ax)
    ax.set_title("Exposure reduction factors")

    ax.set_ylim(ylim)

    plt.xticks(rotation=45, ha='right')

    for i, v in df.reset_index().iterrows():
        #import pdb; pdb.set_trace()
        image_url = v['image_url']
        fit_factor = v['exposure reduction factor']
        #print(image_url)
        img = imread(image_url)
        # img_resized = resize(img, (100,100
        ax.text(i - 0.175, 0.1 + fit_factor, str(fit_factor), color='blue', fontweight='bold')

        newax = fig.add_axes(img_func(fit_factor, i), anchor='NE', zorder=1)
        newax.imshow(img)
        newax.axis('off')



    return {
        'fig': fig,
        'ax': ax
    }


def read_csv(csv_path, local_timezone='-00:00'):
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'] + f' {local_timezone}')
    return df.set_index('timestamp')

def read_2_sensors(template, columns=None, breathing_area_designator='1', ambient_area_designator='2'):
    breathing_area_df = read_csv(template.format(breathing_area_designator))
    ambient_area_df = read_csv(template.format(ambient_area_designator))

    if columns is None:
        columns = ['pm1']

    for column in columns:
        breathing_area_df[f'{column} breathing_area'] = breathing_area_df[f'{column}']
        ambient_area_df[f'{column} ambient_area'] = ambient_area_df[f'{column}']

    return {
        'breathing_area_df': breathing_area_df,
        'ambient_area_df': ambient_area_df,
    }

def between(start, end, df):
    return df[
        (df.index > start)
        & (df.index < end)
    ]

def get_fit_factor_between_two_events(
    event_index,
    time_of_interest_1,
    time_of_interest_2,
    graph_window,
    events,
    column_1='pm1',
    column_2='pm1'
):
    denominator = time_of_interest_1[
        (time_of_interest_1.index > events[event_index]['timedelta'] + graph_window['start']) \
        & (time_of_interest_1.index < events[event_index + 1]['timedelta'] + graph_window['start'])
    ][column_1].sum()

    numerator = time_of_interest_2[
        (time_of_interest_2.index > events[event_index]['timedelta'] + graph_window['start']) \
        & (time_of_interest_2.index < events[event_index + 1]['timedelta'] + graph_window['start'])
    ][column_2].sum()

    return numerator / denominator

def get_fit_factors(metadata_and_two_sensors_list, title, breathing_area_column, ambient_column):
    collection = []

    for obj in metadata_and_two_sensors_list:
        metadata = obj['metadata']
        breathing_area_sensor_data = obj['breathing_area_sensor_data']
        ambient_sensor_data = obj['ambient_sensor_data']

        for graph in metadata:
            sensor_1 = between(
                str(graph['window']['start']),
                str(str(graph['window']['end'])),
                breathing_area_sensor_data
            )

            sensor_2 = between(
                str(graph['window']['start']),
                str(str(graph['window']['end'])),
                ambient_sensor_data
            )

            events = graph['events']

            for i in range(len(events) - 1):
                event = events[i]
                collection.append({
                    title: graph['title'],
                    'event': event['event'],
                    'fit_factor': get_fit_factor_between_two_events(
                        i,
                        sensor_1,
                        sensor_2,
                        graph['window'],
                        events,
                        column_1=breathing_area_column,
                        column_2=ambient_column

                    )
                })

    return pd.DataFrame(collection)

def plot_one_graph(
    graph,
    breathing_area_data,
    ambient_data,
    breathing_area_vars,
    ambient_vars,
    func=None,
    ax=None,
    i=None,
    ylabel='Mass concentration (µg/m3)'

):
    """
    Parameters:
        graph: dict
            Has a 'window' dict that has a 'start' and an 'end'
        breathing_area_data: pd.DataFrame
            Corresponds to the sensor meant to collect data in the breathing area (by the nose / mouth).
            DataFrame indexed by datetime. Has the <variable> as a column (e.g. 'pm1')
        ambient_data: pd.DataFrame
            Corresponds to the sensor meant to collect data not in the breathing area (by the nose / mouth).
            This is meant to substitute for the counterfactual "What if we didn't have the device turned on?
            What concentration would the user have breathed in instead?"
            DataFrame indexed by datetime. Has the <variable> as a column (e.g. 'pm1')
        ax: matplotlib.pyplot.axis or matplotlib.axes
            The axis will graph on, or a list of axes.
        i: int
            Integer representing the specific axis will graph on (e.g. ax[i] if ax is a list of matplotlib.pyplot.axis).
        breathing_area_vars: list[str]
            The variables we'll graph from the breathing_area_data dataframe.
        ambient_vars: list[str]
            The variables we'll graph from the ambient_data dataframe.

    """

    if ax is None:
        fig, ax = plt.subplots(1,1)

    breathing_area_df = between(str(graph['window']['start']), str(str(graph['window']['end'])), breathing_area_data)
    ambient = between(str(graph['window']['start']), str(str(graph['window']['end'])), ambient_data)

    axis = ax
    if i is not None:
        axis = ax[i]

    colors_breathing_area = ['red', 'orange', 'yellow', 'green']

    for j, var in enumerate(breathing_area_vars):
        color = colors_breathing_area[j]
        breathing_area_df[[var]].plot(ax=axis, color=color, linestyle='dashed')

    colors_ambient = ['cyan', 'blue', 'purple', 'pink']
    for j, var in enumerate(ambient_vars):
        color = colors_ambient[j]
        ambient[[var]].plot(ax=axis, color=color, linestyle='dashed')

    default_colors = ['red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple', 'pink']

    event_list = []

    for j, event in enumerate(graph['events']):
        if 'color' in event:
            color = event['color']
        else:
            color_index = j % len(default_colors)
            color = default_colors[color_index]

        axis.axvline(event['timedelta'] + graph['window']['start'], color=color)
        event_list.append(event['event'])

    first_to_plot = breathing_area_vars + ambient_vars
    legends = first_to_plot + [e for e in event_list]

    axis.legend(legends)
    axis.set_ylabel(ylabel)
    axis.set_title(graph['title'])

    if func is not None:
        func(axis)


def plot(
    metadata,
    breathing_area_data,
    ambient_data,
    breathing_area_vars,
    ambient_vars,
    func=None,
    row_size=3,
    ylabel=None
):
    fig, ax = plt.subplots(len(metadata),1, figsize=(15, len(metadata) * row_size))

    for i, graph in enumerate(metadata):
        plot_one_graph(
            graph=graph,
            breathing_area_data=breathing_area_data,
            ambient_data=ambient_data,
            breathing_area_vars=breathing_area_vars,
            ambient_vars=ambient_vars,
            ax=ax,
            i=i,
            func=func,
            ylabel=ylabel
        )

    fig.tight_layout()

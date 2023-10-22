import argparse
import textwrap
import os
import json
from datetime import datetime
from pathlib import Path
from time import sleep
from multiprocessing import Process

import pandas as pd
from sensirion_sps030 import Sensirion

from pms.core import SensorReader

import logging
from sensirion_sps030 import Sensirion

def get_args():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """\
            Collect data using PM sensors.

            Example:

            """
            "python collect_data.py"
            + "--filename='some_dir.json'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--sensor_path_1",
        type=str,
        help="File path for sensor 1",
        default="/dev/ttyUSB0",
        required=False
    )

    parser.add_argument(
        "--sensor_path_2",
        type=str,
        help="File path for sensor 2",
        default="/dev/ttyUSB1",
        required=False
    )

    parser.add_argument(
        "--csv_path_1",
        type=str,
        help="CSV path to save data for sensor 1",
        default='~/Developer/iaq/sensor_data_1.csv',
        required=False
    )

    parser.add_argument(
        "--csv_path_2",
        type=str,
        help="CSV path to save data for sensor 2",
        default='~/Developer/iaq/sensor_data_2.csv',
        required=False
    )


    return parser.parse_args()



def get_data(obs):
    return {
        'timestamp': obs.timestamp,
        'pm1': obs.pm1,
        'pm4': obs.pm4,
        'pm25': obs.pm25,
        'pm10': obs.pm10,
        'n05': obs.n05,
        'n1': obs.n1,
        'n25': obs.n25,
        'n4': obs.n4,
        'n10': obs.n10,
        'tps': obs.tps,
    }

def save(data, csv_path):
    """
    Save the data

    Parameters:
        data: dict
        csv_path: str
    """
    # print(csv_path, data)
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame()

    if df.shape[0] == 0:
        df = pd.DataFrame([data])
    else:
        df = pd.concat([df, pd.DataFrame([data])])

    df.to_csv(csv_path, index=False)

def read(sensor_path, csv_path):
    sensirion = Sensirion(
        port=sensor_path,
    )

    while True:
        mess = sensirion.read_measurement()
        data = get_data(mess)
        save(data, csv_path=csv_path)
        sleep(1)


if __name__ == '__main__':
    """
    Read a sensor
    """


    args = get_args()

    p2 = Process(target=read, args=(args.sensor_path_2, args.csv_path_2))
    p2.start()

    read(
        args.sensor_path_1, args.csv_path_1
    )

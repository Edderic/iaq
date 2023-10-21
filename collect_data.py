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
        "--sensor_type",
        type=str,
        help="SPS30",
        default="SPS30",
        required=False
    )

    parser.add_argument(
        "--sensor_path",
        type=str,
        help="File path for sensor 1",
        default="/dev/ttyUSB0",
        required=False
    )

    parser.add_argument(
        "--interval",
        type=int,
        help="Sampling rate (in seconds)",
        default=1,
        required=False
    )

    parser.add_argument(
        "--csv_path",
        type=str,
        help="CSV path to save data for sensor",
        required=True
    )

    return parser.parse_args()



def get_data(obs):
    return {
        'time': obs.time,
        'pm01': obs.pm01,
        'pm04': obs.pm04,
        'pm25': obs.pm25,
        'pm10': obs.pm10,
        'n1_0': obs.n1_0,
        'n2_5': obs.n2_5,
        'n4_0': obs.n4_0,
        'n10_0': obs.n10_0,
        'diam': obs.diam,
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

def read(sensor_type, sensor_path, interval, csv_path):
    reader = SensorReader(sensor_type, sensor_path, interval=interval)

    with reader:
        for obs in reader():
            data = get_data(obs)
            save(data, csv_path)


if __name__ == '__main__':
    """
    Read a sensor
    """

    args = get_args()

    read(
        args.sensor_type, args.sensor_path, args.interval, args.csv_path,
    )

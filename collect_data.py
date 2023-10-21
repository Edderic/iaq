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

    sensirion = Sensirion(
        port=args.sensor_path,
    )

    while True:
        mess = sensirion.read_measurement()
        data = get_data(mess)
        save(data, csv_path=args.csv_path)
        sleep(1)
    # read(
        # args.sensor_type, args.sensor_path, args.interval, args.csv_path,
    # )

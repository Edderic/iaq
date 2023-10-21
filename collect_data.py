import argparse
import textwrap
import os
import json
from datetime import datetime
from pathlib import Path
from time import sleep

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
        "--sensor_type_1",
        type=str,
        help="SPS30",
        default="SPS30",
        required=False
    )

    parser.add_argument(
        "--sensor_type_2",
        type=str,
        help="SPS30",
        default="SPS30",
        required=False
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
        "--interval",
        type=int,
        help="Sampling rate (in seconds)",
        default="1",
        required=False
    )

    parser.add_argument(
        "--csv_path_1",
        type=str,
        help="CSV path to save data for first sensor",
        required=True
    )

    parser.add_argument(
        "--csv_path_2",
        type=str,
        help="CSV path to save data for second sensor",
        required=True
    )

    return parser.parse_args()

def read(reader, csv_path):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        df = pd.DataFrame()

    with reader:
        print_header = True
        for obs in reader():
            data = {
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
            print(csv_path, data)
            if df.shape[0] < 0:
                df = pd.DataFrame([data])
            else:
                df = pd.concat([df, pd.DataFrame(pd.Series(data))])

            if df.shape[0] > 0:
                df.to_csv(args.csv_path_1)

if __name__ == '__main__':
    """
    Read two sensors.
    """

    args = get_args()

    reader_1 = SensorReader(args.sensor_type_1, args.sensor_path_1, interval=args.interval)
    reader_2 = SensorReader(args.sensor_type_2, args.sensor_path_2, interval=args.interval)

    read(reader_1, args.csv_path_1)
    read(reader_2, args.csv_path_2)


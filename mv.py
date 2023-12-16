import subprocess
import argparse
import time

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prefix",
        help="The name that we'll name the two files with.",
    )

    args = parser.parse_args()
    prefix = args.prefix
    commands = [
        [
            'mv', 'sensor_data_1.csv', f'{prefix}_1.csv',
        ],
        [
            'mv', 'sensor_data_2.csv', f'{prefix}_2.csv',
        ],
        [
            'git', 'add', f'{prefix}_1.csv',
        ],
        [
            'git', 'add', f'{prefix}_2.csv',
        ],
        [
            'git', 'commit', '-m', f'"Saving data for {prefix}"',
        ],
    ]

    for command in commands:
        process_1 = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_1, stderr_1 = process_1.communicate()

        print(f"command: {command}")
        print(f"stdout_1: {stdout_1}")
        print(f"stderr_1: {stderr_1}")


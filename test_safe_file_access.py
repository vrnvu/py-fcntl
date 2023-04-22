import argparse
import multiprocessing
import os
import fcntl
import time
import random

def random_sleep_ms(min_sleep_ms, max_sleep_ms):
    sleep_time = random.uniform(min_sleep_ms, max_sleep_ms) / 1000
    time.sleep(sleep_time)


def safe_file_access(file_path):
    lock_file_path = file_path + '.lock'

    with open(lock_file_path, 'w') as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)

        try:
            with open(file_path, 'r+') as f:
                content = f.read().strip()
                if content:
                    value = int(content)
                else:
                    value = 0
                value += 1
                f.seek(0)
                f.write(str(value))
                f.truncate()
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def unsafe_file_access(file_path):
    with open(file_path, 'r+') as f:
        random_sleep_ms(50, 300)
        content = f.read().strip()
        if content:
            value = int(content)
        else:
            value = 0
        value += 1
        f.seek(0)
        f.write(str(value))
        f.truncate()


def test(num_processes, target):
    file_path = 'testfilesafe'
    open(os.path.abspath(file_path), 'a').close()

    processes = []
    for _ in range(num_processes):
        process = multiprocessing.Process(target=target, args=[file_path])
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    with open(file_path, 'r') as f:
        value = f.read().strip()
        assert value == str(num_processes), f"{value} != {num_processes}"



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num_processes", type=int, default=4, help="number of processes")
    parser.add_argument('--mode', type=str, default='unsafe', choices=['safe', 'unsafe'], help='Mode for file access')
    args = parser.parse_args()

    target = None
    if args.mode == 'safe':
        target = safe_file_access
    else:
        target = unsafe_file_access

    test(num_processes=args.num_processes, target=target)


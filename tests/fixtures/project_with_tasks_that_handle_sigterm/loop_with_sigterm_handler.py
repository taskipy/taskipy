import signal
import sys
import time


def main():
    while True:
        time.sleep(0.1)


def sigterm_handler(sig, frame):
    print('Shutdown gracefully with sigterm...')
    sys.exit(123)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, sigterm_handler)
    main()

import signal
import sys
import time


def main():
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("failing gracefully...")


def sigterm_handler(sig, frame):
    print("Shutdown gracefully with sigterm...")
    sys.exit(123)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sigterm_handler)
    main()

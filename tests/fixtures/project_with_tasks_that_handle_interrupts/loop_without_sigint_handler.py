import sys
import time


def main():
    try:
        while True:
            time.sleep(0.1)
    except Exception:
        sys.exit(130)


if __name__ == "__main__":
    main()

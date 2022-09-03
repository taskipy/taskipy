import sys
import time


def main():
    try:
        while True:
            time.sleep(.1)
    except:
        sys.exit(130)

if __name__ == '__main__':
    main()

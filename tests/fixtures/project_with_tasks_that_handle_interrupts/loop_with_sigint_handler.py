import time

def main():
    try:
        while True:
            time.sleep(.1)
    except KeyboardInterrupt:
        print('failing gracefully...')

if __name__ == '__main__':
    main()

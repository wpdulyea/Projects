#!/usr/bin/env python3
__author__ = "William Dulyea"
__email__ = "wpdulyea@yahoo.com"

try:
    from microbit import *

except ImportError as err:
    print(f"Module import failed due to {err}")
    sys.exit(1)

SECONDS = 1
MINUTES = 60
HOURS = 3600
OFF = Image("0000:0000:0000:0000:9999")
On = Image("9999:0000:0000:0000:0000")

display_divisor = SECONDS
on_threshold = 500
off_threshold = on_threshold - 50
on_time = 0
on = False
start_time = 0


if __name__ == "__main__":

    try:
        while True:
            if button_a.was_pressed():
                on_time = 0
                start_time = running_time()
            sensor = pin0.read_analog()
            if not on:
                if sensor > on_threshold:
                    start_time = running_time()
                    on = True
                else:
                    display.show(OFF)
                    sleep(400)
            else:
                on_time = int((running_time() - start_time) / 1000 /
                        display_divisor)
                if sensor < off_threshold:
                    on = False
                else:
                    display.show(ON)
                    sleep(400)
            if on_time < 10:
                display.show(str(on_time))
            else:
                display.scroll(str(on_time))
            sleep(400)

    except Exception as err:
        logger.error(str(err))
        print(format_exc())
        sys.exit()

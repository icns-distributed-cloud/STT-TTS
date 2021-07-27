import threading
import time

from ublox_gps import UbloxGps
import serial

off = 0
class Thread1(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.flag = threading.Event()

    def run(self):
        port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
        gps = UbloxGps(port)

        while not self.flag.is_set():
            try: 
                coords = gps.geo_coords()
                current_lon = coords.lon
                current_lat = coords.lat
                print(current_lon, current_lat)
            except (ValueError, IOError) as err:
                print(err)

            time.sleep(1)
        print("Thread1 said : Thread %s die\n"%self.ident)
        port.close()


def abc():
    global off
    for i in range(0,5):
        print(i)
        time.sleep(1)
    off = 1 

def main():
    try:
        j1 = Thread1()
        j1.start()
        abc()

        if off == 1:
            j1.flag.set()
            j1.join()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()

from ublox_gps import UbloxGps
import serial
import threading
# Can also use SPI here - import spidev
# I2C is not supported

port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
gps = UbloxGps(port)

def run():
  
  try: 
    print("Listenting for UBX Messages.")
    while True:
      try: 
        coords = gps.geo_coords()
        print(coords.lon, coords.lat)
      except (ValueError, IOError) as err:
        print(err)
  
  finally:
    port.close()
'''
if __name__ == '__main__':
  run()
'''
def get_gps():
  try:
    try: 
      coords = gps.geo_coords()
      current_lon = coords.lon
      current_lat = coords.lat
      print(current_lon, current_lat)
    except (ValueError, IOError) as err:
      print(err)
  finally:
    port.close()
  return str(current_lon), str(current_lat)


 
# def continuous_get_gps():
#   # try:
#   try: 
#     coords = gps.geo_coords()
#     global lon = coords.lon
#     global lat = coords.lat
#     print(lon, lat)
#   except (ValueError, IOError) as err:
#     print(err)
#   # finally:
#   #  port.close()
   
#   threading.Timer(1,continuous_get_gps).start() 
#   #return str(current_lon), str(current_lat)
# continuous_get_gps()







#from ublox_gps import UbloxGps
import serial
from ublox_gps import UbloxGps
# Can also use SPI here - import spidev
# I2C is not supported

'''
def run():
  port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
  gps = UbloxGps(port)
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
def get_gps():
  port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
  gps = UbloxGps(port)
  try:
    try:
      coords = gps.geo_coords()
      current_lon = coords.lon
      current_lat = coords.lat
      #print(current_lon, current_lat)
    except (ValueError, IOError)as err:
      print(err)
  finally:
    port.close()
  
  return current_lon, current_lat

#

#lon, lat = get_gps()
#print(lon,lat)
    #except (ValueError, IOError) as err:
      #print(err)
  #finally:
    #port.close()
  #return current_lon, current_lat#127.076779433 , 37.2463380449 
#a,b = get_gps()
#print(a,b)
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






from ublox_gps import UbloxGps
import serial

# Can also use SPI here - import spidev
# I2C is not supported


def run():
  port = serial.Serial('/dev/ttyACM0', baudrate=460800, timeout=1)
  gps = UbloxGps(port)
  
  try: 
    print("Listenting for UBX Messages.")
    with open('gps_data.txt','w') as file:
        i=0
        while True:
            try: 
                coords = gps.geo_coords()
                print(coords.lon, coords.lat)
                if(i == 5) :
                    file.write(f'{coords.lon} {coords.lat}\n')
                    i = 0
                else : i+=1
                
            except (ValueError, IOError) as err:
                print(err)
  
  finally:
    port.close()

run()
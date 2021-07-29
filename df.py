import aigo_destination_route
import playsound
import aigo_destination_speech
import threading


lock = threading.Lock()

command = "스타벅스"
def bb(command):
    lock.acquire()
    try:
        aigo_destination_route.get_route(command)
    finally:
        lock.release()

my_thread = threading.Thread(target=bb, args=(command,))
my_thread.start()

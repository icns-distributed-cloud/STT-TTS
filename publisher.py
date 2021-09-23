import paho.mqtt.publish as publish

msgs = [{'topic': "/detect/car", 'payload': "1"},
        {'topic': "/detect/tl", 'payload': "1"}]

host = "localhost"

if __name__ == '__main__':
    publish.multiple(msgs, hostname=host)

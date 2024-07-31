import time
from servo import Servo
import machine
from machine import Pin
import network
import socket
import ble_simple_peripheral
import bluetooth


n = 0 # initialize position
t = 0.005 # spin increment time
up = 0 # up position
down = 180 # down position
name = 'Switch'


ble = bluetooth.BLE()
peripheral = ble_simple_peripheral.BLESimplePeripheral(ble, name)
led = Pin("LED", Pin.OUT)


def blink(led):
    led.on()
    time.sleep(0.1)
    led.off()
    time.sleep(0.1)

def on_rx(data):
    global n
    for i in range(3):
        blink(led)
    x = str(data)
    x = x[-2]
    print('Turning...')
    servo = Servo(28)
    #servo.write(180)
    try:
        if x == '1':
            if n == up:
                for position in range(up, down):
                    #print(position)
                    led.toggle()
                    servo.write(position)
                    time.sleep(t)
                n = down
            elif n == down:
                for position in reversed(range(up, down)):
                    #print(position)
                    led.toggle()
                    servo.write(position)
                    time.sleep(t)
                n = up
        servo.off()
    except KeyboardInterrupt:
        servo.off()
        led.off()
        #p.off()

#peripheral.on_write(on_rx)

while True:
    if peripheral.is_connected():
        #led.on()
        peripheral.on_write(on_rx)
    else:
        led.off()
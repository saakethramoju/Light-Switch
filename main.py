'''import sys

# ruff: noqa: E402
sys.path.insert(0, '/Users/saakethramramoju/Desktop/Switch')'''

import asyncio
import aioble
import bluetooth
from machine import Pin
#import machine
from servo import Servo
import time

x = 0 # initialize position
t = 0.005 # spin increment time
up = 0 # up position
down = 180 # down position
device_name = 'Light Switch'
led = Pin("LED", Pin.OUT)
servo = Servo(28)

led.off()

# org.bluetooth.service.heart_rate_service
_HEART_RATE_SERVICE = bluetooth.UUID(0x180D)
# org.bluetooth.characteristic.user_control_point
_USER_CONTROL_POINT_UUID = bluetooth.UUID(0x2A9F)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_HEART_RATE_SENSOR = const(832)

service = aioble.Service(_HEART_RATE_SERVICE)
servo_control = aioble.Characteristic(service, _USER_CONTROL_POINT_UUID, read = True, write = True, capture = True)
aioble.register_services(service)

async def blink():
    led = Pin("LED", Pin.OUT)
    for i in range(3):
        led.on()
        await asyncio.sleep(0.5)
        led.off()
        await asyncio.sleep(0.5)

async def scan_devices():
    '''async with aioble.scan(duration_ms=5000, interval_us=30000, window_us=30000, active=True) as scanner: # type: ignore
        async for result in scanner:
            print(result, result.name(), result.rssi, result.services())'''
    '''async with aioble.scan(duration_ms=5000) as scanner: # type: ignore
        async for result in scanner:
            print(result, result.name(), result.rssi, result.services())'''


async def control_task(connection):
    global x
    try:
        with connection.timeout(None):
            while True:
                _, value = await servo_control.written() # type: ignore
                #print(value)
                data = str(value)
                data = data[-2]
                if data == '1':
                    if x == up:
                        print('Turning...')
                        for position in range(up, down):
                            #print(position)
                            led.toggle()
                            servo.write(position)
                            time.sleep(t)
                        x = down
                    elif x == down:
                        print('Turning...')
                        for position in reversed(range(up, down)):
                            #print(position)
                            led.toggle()
                            servo.write(position)
                            time.sleep(t)
                        x = up
                    servo.off()
                    led.off()
    except aioble.DeviceDisconnectedError:
        return

        
async def peripheral_task():
    while True:
        print("Waiting for connection...")
        async with await aioble.advertise(
            250000,
            name=device_name,
            services=[_HEART_RATE_SERVICE],
        ) as connection: # type: ignore
            print("Connection from", connection.device)
            print('Connection successful')
            #servo_control.notify(connection)
            led_task = asyncio.create_task(blink())
            control_task_instance = asyncio.create_task(control_task(connection))
            try:
                print("Waiting for command...")
                await control_task_instance
                await led_task
            except asyncio.CancelledError:
                print("Task cancelled")
            await connection.disconnected()
            print("Disconnected")
            control_task_instance.cancel()

async def main():
    taskA = asyncio.create_task(peripheral_task())
    taskB = asyncio.create_task(scan_devices())
    await asyncio.gather(taskA, taskB)

asyncio.run(main())
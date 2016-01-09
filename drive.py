#!/usr/bin/python

import time, sys
from random import randint
from ev3dev.auto import *

# Configure motors
motors = [LargeMotor(address) for address in (OUTPUT_B, OUTPUT_C)]
assert all([m.connected for m in motors]), \
    "Two large motors should be connected to ports B and C"

# Configure infrared sensor
ir = InfraredSensor()
assert ir.connected

# Configure touch sensor
ts = TouchSensor()
assert ts.connected

# Put the infrared sensor into proximity mode
ir.mode = 'IR-PROX'

def start():
    for m in motors:
        print "starting", m
        m.reset()
        m.run_forever(duty_cycle_sp=75, polarity='normal')

def stop():
    for m in motors:
        print "stopping", m
        m.stop()

def turn():
    power = (1, -1)
    t = randint(250, 1000)

    for m, p in zip(motors, power):
        m.run_timed(duty_cycle_sp=p*75, time_sp=t)

    while any(m.state for m in motors):
        time.sleep(0.1)

def backup():
    # Sound backup alarm.
    Sound.tone([(1000, 500, 500)] * 3)

    # Break and go back
    for m in motors:
        m.stop(stop_command='brake')
        m.run_timed(duty_cycle_sp=-50, time_sp=1500)

    while any(m.state for m in motors):
        time.sleep(0.1)

# Start all motors
start()

btn = Button()
while not btn.any():
    if ts.value():
        # Rear touch sensor pressed, maybe we're stuck, backup
        backup()
        turn()
        start()
        continue

    # Read proximity sensor
    d = ir.value()
    print d

    if d > 70:
        # Full speed
        dc = 90
    elif d > 50:
        # Half speed, obstacle ahead
        dc = 30
    else:
        # Obstacle too close, turn
        stop()
        Sound.speak('Ostacolo rilevato').wait()
        turn()
        start()

    # Adjust motor speed
    for m in motors:
        m.duty_cycle_sp = dc

    time.sleep(0.1)

# Stop all motors
stop()

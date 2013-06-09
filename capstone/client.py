"""
Target generator
Author: David Ernest Lester
Date modified: 04/02/12

Generates random target data
"""

import zmq
import time
import string
import random
import numpy as np
import json

from events import EVENT_KILL, EVENT_NEW_VEHICLE
from hostile import Hostile


def encryption_generator(code_type):
    ascii_value = {
            0: random.randrange(0, 26),
            1: random.randrange(26, 52),
            2: random.randrange(52, 62),
            }[code_type]

    return ascii_value


def main():
    context = zmq.Context()

    # Set up socket to send messages to
    sender = context.socket(zmq.PUSH)
    sender.connect("tcp://localhost:3000")

    # Setup socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://localhost:3001")

    # Setup socket to constantly listen for messages
    waiting_for_message = zmq.Poller()
    waiting_for_message.register(receiver, zmq.POLLIN)

    # Unique id for each client
    code_list = string.ascii_lowercase + string.ascii_uppercase + string.digits

    identification = ''

    for i in range(8):
        digit = encryption_generator(random.randrange(0, 3))
        identification = identification + code_list[digit]

    # Spawns the vehicle a random distance from outside the visible radar
    dist = random.randint(21000, 24000)
    #print "first dist: ", dist

    # Randomly selects a theta between 0 and 2pi
    theta = random.random() * 2 * np.pi
    #print "theta: ", theta

    # Randomly selects a vehicle type: boat, helicopter, or jet
    vehicle_type = random.randint(0, 2)
    #print "Vehicle type: ", vehicle_type

    # Randomly selects phi
    phi = {
            0: 0,
            1: random.random() * np.pi / 6,
            2: random.random() * np.pi / 4,
            }[vehicle_type]
    #print "phi: ", phi

    # Initializing the elevation of the vehicle
    z = {
            0: 0,
            1: dist * np.sin(phi),
            2: dist * np.sin(phi),
        }[vehicle_type]

    # Distance from relative center of radar
    dist = dist * np.cos(phi)
    #print "dist from relative center of radar: ", dist

    # Cordinates of the vehicle
    x = dist * np.cos(theta)
    #print "x coordinate: ", x
    y = dist * np.sin(theta)
    #print "y coordinate: ", y
    #print "z coordinate: ", z

    # Sends the information to the vehicle class
    hostile = Hostile(identification, vehicle_type, x, y, z, 0, 0, 0)

    while True:
        # Keeps track of old time to get change in time
        time_old = time.time()

        # Will generate data every 2 seconds as if a radar sweep
        time.sleep(2)

        # Changes position by a linear factor
        hostile.move_to(hostile.x_mod, hostile.y_mod, 0, time_old)

        # Sends data to the world
        event = {'event': EVENT_NEW_VEHICLE, 'arguments': hostile.to_dict}
        sender.send(json.dumps(event))

        # Push new data to old data
        hostile.old_data(hostile.x, hostile.y, hostile.z)

        # Constantly looking for quit reply from the world
        ready = dict(waiting_for_message.poll(0))

        # If message received and is quit then close socket to world
        if ready.get(receiver) == zmq.POLLIN:
            event = json.loads(receiver.recv())
            if event['id'] == identification:
                if event['event'] & EVENT_KILL:
                    sender.close()
                    receiver.close()
                    exit(1)


if __name__ == '__main__':
    main()

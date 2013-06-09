"""
Server definition
Author: David Ernest Lester
Date modified: 04/02/12

Keeps track of an instance class of the target(s) that pass data
"""

import zmq
import json

from events import EVENT_KILL, EVENT_NEW_VEHICLE
from vehicles import Vehicles

RADAR_ZONE = 20000
WORLD_ZONE = 24000
CONE_ANGLE = 25


def main():
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.bind("tcp://*:3000")

    # Socket to send messages to clients
    client = context.socket(zmq.PUB)
    client.bind("tcp://*:3001")

    # Socket to send messages to ventillator
    combMngSys = context.socket(zmq.REQ)
    combMngSys.connect("tcp://localhost:4001")

    while True:
        event = json.loads(receiver.recv())

        if event['event'] & EVENT_NEW_VEHICLE:
            arguments = event['arguments']
            vehicles = Vehicles(**arguments)
            #print vehicles
        elif event['event'] & EVENT_KILL:
            arguments = event['id']
            event = {'id': arguments, 'event': EVENT_KILL}
            client.send(json.dumps(event))

        # If vehicles enter radar and not in invisible cone send data
        if vehicles.check_distance(RADAR_ZONE, True) and (
                vehicles.invisible_cone(CONE_ANGLE)):

            combMngSys.send(json.dumps(vehicles.package_data()))
            combMngSys.recv()

        # Target(s) entirely out of range quit connection
        elif vehicles.check_distance(WORLD_ZONE, False):
            event = {'id': vehicles.identity, 'event': EVENT_KILL}
            client.send(json.dumps(event))

if __name__ == '__main__':
    main()

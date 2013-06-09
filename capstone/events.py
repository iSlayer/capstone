# Events available
import json
import struct

EVENT_NULL = 0
EVENT_KILL = 1 << 1
EVENT_NEW_VEHICLE = 1 << 2
EVENT_RADAR_OUTPUT = 1 << 3
EVENT_TARGET_LIST = 1 << 4

BASIC_EVENT = {'event': EVENT_NULL}


def create_kill_event(who, d=BASIC_EVENT):
    d['event'] |= EVENT_KILL
    d['id'] = who
    return d


def create_target_list_event(serialized, d=BASIC_EVENT):
    d['event'] |= EVENT_TARGET_LIST
    d['serialized'] = json.dumps(serialized)
    return d


def unpack_target_list_event(d):
    return json.loads(d['serialized'])

radar_struct = struct.Struct('f f f 8s f')


def create_radar_output(bearing, range1, angle, identification, dt, d=BASIC_EVENT):
    d['event'] |= EVENT_RADAR_OUTPUT
    d['data'] = [bearing, range1, angle, identification, dt]
    return d


def unpack_radar_output(d):
    if d: return d['data']

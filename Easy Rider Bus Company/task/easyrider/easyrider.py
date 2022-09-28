import json
import re
import datetime
from datetime import datetime
from contants import *
from collections import Counter


def validate_stop_name(name):
    if not isinstance(bus_stop[STOP_NAME], str) or len(bus_stop[STOP_NAME]) == 0:
        return False

    tokenized_name = re.split('\s+', name)
    if len(tokenized_name) < 2:
        return False
    prefix = tokenized_name[0]
    suffix = tokenized_name[len(tokenized_name) - 1]
    valid_suffixes = ['Road', 'Avenue', 'Boulevard', 'Street']

    if not prefix[0].isupper() or suffix not in valid_suffixes:
        return False
    return True


def validate_a_time(time):
    if not isinstance(time, str) or len(time) == 0:
        return False
    pattern = re.compile(r'^([0-1]\d|2[0-3]):[0-5]\d$')
    return bool(pattern.match(time))


def add_bus_stop(bus):
    bus_stops_dict[bus] = bus_stops_dict[bus] + 1


def validate_start_and_stops():
    for start_stop_key in bus_stop_start_stop_dict:
        stops = bus_stop_start_stop_dict[start_stop_key]
        start = 0
        stop = 0
        if not stops:
            continue
        for element in stops:
            if element == 'S':
                start += 1
            if element == 'F':
                stop += 1
        if start != 1 and stop != 1:
            print("There is no start or end stop for the line: {}".format(start_stop_key))
            return False
        if start != 1:
            print("Invalid number of start stops for line: {}".format(start_stop_key))
            return False
        if stop != 1:
            print("Invalid number of finish stops for line: {}".format(start_stop_key))
            return False
    return True


def create_transfer_stop_list():
    original_list = stop_types.values()
    flatten_list = [element for sublist in original_list for element in sublist]
    res = Counter(flatten_list)
    for stop in res:
        if res[stop] > 1:
            transfer_stops.append(stop)
    transfer_stops.sort()


def reduce_repetive_stops(repetetive_list):
    return sorted(list(set(repetetive_list)))


bus_id = 0
stop_id = 0
stop_name = 0
next_stop = 0
stop_type = 0
a_time = 0
bus_stops_dict = {
    128: 0,
    256: 0,
    512: 0,
    1024: 0
}
bus_stop_start_stop_dict = {
    128: [],
    256: [],
    512: [],
    1024: []
}
stop_types = {
    'S': [],
    'O': [],
    'F': [],
    "": []
}
transfer_stops = []
incorrect_time_stops = {}
incorrect_type_stops = []

buses_dict = json.loads(input())

for i in range(0, len(buses_dict)):
    bus_stop = buses_dict[i]
    bus_stop_start_stop_dict[bus_stop[BUS_ID]].append(bus_stop[STOP_TYPE])
    stop_types[bus_stop[STOP_TYPE]].append(bus_stop[STOP_NAME])

    # if bus_stop[BUS_ID] in incorrect_time_stops.keys():
    #     continue
    for key in bus_stop:
        if key == BUS_ID:
            if not isinstance(bus_stop[BUS_ID], int) \
                    or bus_stop[BUS_ID] not in [128, 256, 512, 1024]:
                bus_id += 1
            else:
                add_bus_stop(bus_stop[BUS_ID])
        if key == STOP_ID:
            if not isinstance(bus_stop[STOP_ID], int):
                stop_id += 1
        if key == STOP_NAME:
            if not validate_stop_name(bus_stop[STOP_NAME]):
                stop_name += 1
        if key == NEXT_STOP:
            if not isinstance(bus_stop[NEXT_STOP], int):
                next_stop += 1
        if key == STOP_TYPE:
            if not isinstance(bus_stop[STOP_TYPE], str) \
                    or bus_stop[STOP_TYPE] not in ['S', 'O', 'F', ""]:
                stop_type += 1
        if key == A_TIME:
            if not validate_a_time(bus_stop[A_TIME]):
                a_time += 1
            if i != 0:
                if bus_stop[BUS_ID] != buses_dict[i-1][BUS_ID]:
                    if bus_stop[STOP_TYPE] == 'O':
                        incorrect_type_stops.append(bus_stop[STOP_NAME])
                if bus_stop[BUS_ID] == buses_dict[i-1][BUS_ID]:
                    prev_stop = datetime.strptime(buses_dict[i-1][A_TIME], '%H:%M')
                    now_stop = datetime.strptime(bus_stop[A_TIME], '%H:%M')
                    if prev_stop >= now_stop:
                        incorrect_time_stops.update({bus_stop[BUS_ID]: bus_stop[STOP_NAME]})
                        break


total_fields = bus_id + stop_id + stop_name + next_stop + stop_type + a_time
# print('Format validation: {} errors'.format(total_fields))
# print('bus_id: {}'.format(bus_id))
# print('stop_id: {}'.format(stop_id))
# print('stop_name: {}'.format(stop_name))
# print('next_stop: {}'.format(next_stop))
# print('stop_type: {}'.format(stop_type))
# print('a_time: {}'.format(a_time))

# print('Line names and number of stops:')
# for key in bus_stops_dict.keys():
#     print('bus_id: {0}, stops: {1}'.format(key, bus_stops_dict[key]))

# if validate_start_and_stops():
#     create_transfer_stop_list()
#     s_stops = reduce_repetive_stops(stop_types['S'])
#     f_stops = reduce_repetive_stops(stop_types['F'])
#     print('Start stops: {0} {1}'.format(len(s_stops), s_stops))
#     print('Transfer stops: {0} {1}'.format(len(transfer_stops), transfer_stops))
#     print('Finish stops: {0} {1}'.format(len(f_stops), f_stops))

# print('Arrival time test:')
# if len(incorrect_time_stops) == 0:
#     print('OK')
# else:
#     for key, value in incorrect_time_stops.items():
#         print('bus_id line {0}: wrong time on station {1}'.format(key, value))

create_transfer_stop_list()
for bus_stop in buses_dict:
    if bus_stop[STOP_NAME] in transfer_stops and bus_stop[STOP_TYPE] == 'O':
        incorrect_type_stops.append(bus_stop[STOP_NAME])


print('On demand stops test:')
if len(incorrect_type_stops) == 0:
    print('OK')
else:
    print('Wrong stop type: {}'.format(sorted(incorrect_type_stops)))

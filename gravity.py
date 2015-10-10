a!/usr/bin/env python
#-*- coding: utf-8 -*-
from pprint import pprint
import math
from sys import exit
import random
import json
import pickle

import pylab as pl

IMG_DIR = os.path.join(os.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

def get_gravity(point1, point2):
    if point1 == point2:
        return 0
    G = 1000000.0
    gravity = G/(abs(point1 - point2) ** 3)
    return gravity

def calculate_moving(cluster):
    points = sorted(cluster.keys())
    moving = dict((p, 0) for p in points)
    for idx, point1 in enumerate(points):
        for idx2, point2 in enumerate(points[idx:]):
            gravity = get_gravity(point1, point2)
            max_point_moving = abs(gravity / min(cluster[point1], cluster[point2]))
            if max_point_moving >= abs(point1 - point2):
                max_point_moving = abs(point1 - point2)

            moving[point1] += min(gravity / cluster[point1], max_point_moving)
            moving[point2] -= min(gravity / cluster[point2], max_point_moving)
    return moving


def group_to_cluster(data):
    cluster = {}
    for i in data:
        if i in cluster:
            cluster[i] += 1
        else:
            cluster[i] = 1
    return cluster


def regroup_cluster(cluster, moving):
    points = sorted(cluster.keys())
    group_points = dict((p, [idx, []]) for idx, p in enumerate(points))

    previous_point = None
    for point in points:
        limits = (min(point + moving[point], point), max(point, point + moving[point]))
        intersections = filter(lambda p: limits[0] <= p <= limits[1], points)

        if previous_point and (previous_point + moving[previous_point]) > point + moving[point]:
            intersections += [previous_point]
        previous_point = point

        group_points[point][1] += intersections
        for i in intersections:
            if i == point:
                continue
            group_points[i][1] = group_points[point][1]

    new_cluster = {}
    for point, new_points in group_points.iteritems():
        new_points = list(set(new_points[1]))
        if len(new_points) == 1:
            key = new_points[0] + moving[new_points[0]]
            value = cluster[new_points[0]]
        else:
            sum_weight = sum([cluster[p] for p in new_points])
            key = sum((p + moving[p]) * cluster[p] for p in new_points) / sum_weight
            value = sum_weight
        new_cluster[key] = value

    pprint(new_cluster)


    return new_cluster



# try:
    # with open('exporter/data_12.pickle','rw') as f:
        # raw_data = pickle.load(f)
# except IOError:
    # with open('exporter/data_12.json','r') as f:
        # raw_data = json.load(f)

        # with open('exporter/data_12.pickle','w+') as f2:
            # pickle.dump(raw_data, f2)

# for spa_id, info in raw_data.iteritems():
    # pprint(info)
    # break

# data = []
# for spa_id, info in raw_data.iteritems():
    # if info['battles']>1000:
        # data.append(float(1) * info['spotted'] / info['wins'] / info['damage_dealt'])

data = [
    5.1, 4.9, 4.7, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8, 5.7,
    5.4, 5.1, 5.7, 5.1, 5.4, 5.1, 4.6, 5.1, 4.8, 5.0, 5.0, 5.2, 5.2, 4.7, 4.8,
    5.4, 5.2, 5.5, 4.9, 5.0, 5.5, 4.9, 4.4, 5.1, 5.0, 4.5, 4.4, 5.0, 5.1, 4.8,
    5.1, 4.6, 5.3, 5.0, 7.0, 6.4, 6.9, 5.5, 6.5, 5.7, 6.3, 4.9, 6.6, 5.2, 5.0,
    5.9, 6.0, 6.1, 5.6, 6.7, 5.6, 5.8, 6.2, 5.6, 5.9, 6.1, 6.3, 6.1, 6.4, 6.6,
    6.8, 6.7, 6.0, 5.7, 5.5, 5.5, 5.8, 6.0, 5.4, 6.0, 6.7, 6.3, 5.6, 5.5, 5.5,
    6.1, 5.8, 5.0, 5.6, 5.7, 5.7, 6.2, 5.1, 5.7, 6.3, 5.8, 7.1, 6.3, 6.5, 7.6,
    4.9, 7.3, 6.7, 7.2, 6.5, 6.4, 6.8, 5.7, 5.8, 6.4, 6.5, 7.7, 7.7, 6.0, 6.9,
    5.6, 7.7, 6.3, 6.7, 7.2, 6.2, 6.1, 6.4, 7.2, 7.4, 7.9, 6.4, 6.3, 6.1, 7.7,
    6.3, 6.4, 6.0, 6.9, 6.7, 6.9, 5.8, 6.8, 6.7, 6.7, 6.3, 6.5, 6.2, 5.9,
]

pl.figure(100)
n, bins, patches = pl.hist(data, facecolor='g', alpha=0.75) #, 50,
pl.grid(True)
pl.savefig('gravity/gist.svg')
pl.close()
exit()
min_point = min(data)
max_point = max(data)
for idx, point in enumerate(data):
    data[idx] = int(1000 * (point - min_point) / (max_point - min_point))

cluster = group_to_cluster(data)

def print_cluster(cluster, iteration=None):
    print '======='
    print 'Nodes: %s' % len(cluster), 'Points: %s' % sum(cluster.values())


    pl.figure(iteration)
    for key in sorted(cluster.keys()):
        pl.plot([key, key], [0, cluster[key]], '#000000')
        pl.axis([0, 1000, 0, 100000])
    pl.savefig(os.path.join(IMG_DIR, 's.svg' % iteration)
    pl.close()


count_without_results = 0
previous_result = len(cluster)
latest_correct_cluster = cluster
iteration = 1
while count_without_results < 15:
    moving = calculate_moving(cluster)
    cluster = regroup_cluster(cluster, moving)
    print_cluster(cluster, iteration)
    iteration += 1
    if previous_result == len(cluster):
        count_without_results += 1
    else:
        count_without_results += 0
        previous_result = len(cluster)
        latest_correct_cluster = cluster
print_cluster(latest_correct_cluster, 0)

# iteration = 1
# while len(cluster) > 7:
    # moving = calculate_moving(cluster)
    # cluster = regroup_cluster(cluster, moving)
    # print_cluster(cluster, iteration)
    # iteration += 1


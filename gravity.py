#!/usr/bin/env python
#-*- coding: utf-8 -*-
from pprint import pprint
import os

import pylab as pl

IMG_DIR = os.path.join(os.dirname(__file__), 'img')
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)


def make_cluster(data, meta=None, save_img=True, make_hist=True):

    if make_hist:
        _make_hist(data)

    _normalize_values(data)
    cluster = group_to_cluster(data)
    cluster = _calculate_cluster(cluster, save_img)

    if save_img:
        print_cluster(cluster, 0)


def _normalize_values(data):
    min_point = min(data)
    max_point = max(data)
    for idx, point in enumerate(data):
        data[idx] = int(1000 * (point - min_point) / (max_point - min_point))


def _calculate_cluster(cluster, save_img):
    count_without_results = 0
    previous_result = len(cluster)
    latest_correct_cluster = cluster
    iteration = 1
    while count_without_results < 15:
        moving = calculate_moving(cluster)
        cluster = regroup_cluster(cluster, moving)
        if save_img:
            print_cluster(cluster, iteration)
        iteration += 1
        if previous_result == len(cluster):
            count_without_results += 1
        else:
            count_without_results += 0
            previous_result = len(cluster)
            latest_correct_cluster = cluster
    return latest_correct_cluster


# iteration = 1
# while len(cluster) > 7:
    # moving = calculate_moving(cluster)
    # cluster = regroup_cluster(cluster, moving)
    # print_cluster(cluster, iteration)
    # iteration += 1


def get_gravity(point1, point2):
    if point1 == point2:
        return 0
    G = 1000000.0
    gravity = G / (abs(point1 - point2) ** 3)
    return gravity


def calculate_moving(cluster):
    points = sorted(cluster.keys())
    moving = dict((p, 0) for p in points)
    for idx, point1 in enumerate(points):
        for _, point2 in enumerate(points[idx:]):
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
        intersections = [p for p in points if limits[0] <= p <= limits[1]]

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


def _make_hist(data):
    pl.figure(100)
    pl.hist(data, facecolor='g', alpha=0.75)
    pl.grid(True)
    pl.savefig(os.path.join(IMG_DIR, 'gist.svg'))
    pl.close()


def print_cluster(cluster, iteration=None):
    print '======='
    print 'Nodes: %s' % len(cluster), 'Points: %s' % sum(cluster.values())

    pl.figure(iteration)
    for key in sorted(cluster.keys()):
        pl.plot([key, key], [0, cluster[key]], '#000000')
        pl.axis([0, 1000, 0, 100000])
    pl.savefig(os.path.join(IMG_DIR, 's.svg' % iteration))
    pl.close()

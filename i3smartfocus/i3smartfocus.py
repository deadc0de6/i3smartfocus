#!/usr/bin/env python3
# author: deadc0de6

"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2020, deadc0de6
i3wm smart focus
"""


import sys
import os
import i3ipc
import math
import tempfile


VERSION = '0.1.2'
# debug mode
DEBUG = False
# allowed direction arguments
DIRECTIONS = ['left', 'right', 'up', 'down']
# shift so that
# "up"/"down" always end up on the left most and
# "left"/"right" always end up on the top most
# in case of equality
SHIFT = 2
# save last focus workspace
PATH = os.path.join(tempfile.gettempdir(), '.i3-last-workspace')


def log(string):
    """write logs to stderr"""
    if not DEBUG:
        return
    sys.stderr.write('{}\n'.format(string))


class Point:

    def __init__(self, x, y):
        """a point"""
        self.x = x
        self.y = y

    def distance(self, other):
        """return the distance to other"""
        x1, y1 = self.x, self.y
        x2, y2 = other.x, other.y
        xs = (x2-x1)**2
        ys = (y2-y1)**2
        return math.sqrt(xs+ys)


class Rect:

    def __init__(self, node):
        """a rectangle"""
        self.point = Point(node.rect.x, node.rect.y)
        self.width = node.rect.width
        self.height = node.rect.height

    def distance(self, other):
        """return distance to other"""
        return self.point.distance(other.point)

    def left_of(self, other):
        """return true if self is left of other"""
        if self.point.x <= other.point.x:
            return True
        return False

    def right_of(self, other):
        """return true if self is right of other"""
        if self.point.x >= other.point.x:
            return True
        return False

    def up_of(self, other):
        """return true if self is up of other"""
        if self.point.y <= other.point.y:
            return True
        return False

    def down_of(self, other):
        """return true if self is down of other"""
        if self.point.y >= other.point.y:
            return True
        return False

    def shift_left(self, nb):
        """shift to the left"""
        self.point.x = self.point.x - nb
        return self

    def shift_up(self, nb):
        """shift up"""
        self.point.y = self.point.y - nb
        return self

    def left(self):
        """shift to the left point"""
        x = self.point.x
        y = self.point.y + (self.height/2)
        self.point = Point(x, y)
        return self

    def right(self):
        """shift to the right point"""
        x = self.point.x + self.width
        y = self.point.y + (self.height/2)
        self.point = Point(x, y)
        return self

    def up(self):
        """shift to the top point"""
        x = self.point.x + (self.width/2)
        y = self.point.y
        self.point = Point(x, y)
        return self

    def down(self):
        """shift to the bottom point"""
        x = self.point.x + (self.width/2)
        y = self.point.y + self.height
        self.point = Point(x, y)
        return self


def save_last_workspace(wsid):
    """save last workspace id to file"""
    try:
        open(PATH, 'w').write(str(wsid))
    except Exception:
        pass


def get_last_workspace():
    """get last workspace id from file"""
    if not os.path.exists(PATH):
        return 0
    try:
        return int(open(PATH, 'r').read())
    except Exception:
        return 0


def workspace_direction(direction):
    """get workspace in direction"""
    cur = i3.get_tree().find_focused().workspace()
    if direction == 'l':
        nodes = workspaces_left(cur)
    elif direction == 'r':
        nodes = workspaces_right(cur)
    elif direction == 'u':
        nodes = workspaces_up(cur)
    elif direction == 'd':
        nodes = workspaces_down(cur)

    node = None
    if not nodes:
        return node

    if len(nodes) > 1:
        # find the focus stack
        lastid = get_last_workspace()
        if lastid in [ws.id for ws in nodes]:
            node = [n for n in nodes if n.id == lastid][0]
    else:
        node = nodes[0]

    return node


def focus_node_direction(ref, direction):
    """focus on the node in direction direction"""
    leaves = ref.workspace().leaves()

    if direction == 'l':
        node = left_one(leaves, ref)
    elif direction == 'r':
        node = right_one(leaves, ref)
    elif direction == 'u':
        node = up_one(leaves, ref)
    elif direction == 'd':
        node = down_one(leaves, ref)

    if not node:
        # check if there's a workspace in that direction
        ws = workspace_direction(direction)
        print_node(ws)
        if ws:
            node = find_window_to_focus_on(ws)
            print_node(node)
    return node


def find_window_to_focus_on(workspace):
    """find the window to fucus on in this workspace"""
    if not workspace:
        return None
    node = workspace
    while True:
        fids = node.focus
        if not fids:
            break
        node = node.find_by_id(fids[0])
    return node


def workspaces_left(ref):
    """return workspace on the left"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for ws in workspaces:
        if ws.id == ref.id:
            continue
        x = ws.rect.x
        if x < ref.rect.x:
            res.append(ws)
    return res


def workspaces_right(ref):
    """return workspace on the right"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for ws in workspaces:
        if ws.id == ref.id:
            continue
        x = ws.rect.x
        if x > ref.rect.x:
            res.append(ws)
    return res


def workspaces_up(ref):
    """return workspace above"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for ws in workspaces:
        if ws.id == ref.id:
            continue
        y = ws.rect.y
        if y > ref.rect.y:
            res.append(ws)
    return res


def workspaces_down(ref):
    """return workspace below"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for ws in workspaces:
        if ws.id == ref.id:
            continue
        y = ws.rect.y
        if y < ref.rect.y:
            res.append(ws)
    return res


def left_one(nodes, ref):
    """return node in nodes left from ref"""
    rect = Rect(ref).left().shift_up(SHIFT)
    distance = 1 << 30
    fnode = None
    print_node(ref)
    for node in nodes:
        if not node:
            continue
        if node.id == ref.id:
            continue
        other = Rect(node).right()
        print_node(node)
        if other.left_of(rect):
            d = other.distance(rect)
            if d < distance:
                distance = d
                fnode = node
    return fnode


def right_one(nodes, ref):
    """return node in nodes right from ref"""
    rect = Rect(ref).right().shift_up(SHIFT)
    distance = 1 << 30
    fnode = None
    for node in nodes:
        if not node:
            continue
        if node.id == ref.id:
            continue
        other = Rect(node).left()
        if other.right_of(rect):
            d = other.distance(rect)
            if d < distance:
                distance = d
                fnode = node
    return fnode


def up_one(nodes, ref):
    """return node in nodes top from ref"""
    rect = Rect(ref).up().shift_left(SHIFT)
    distance = 1 << 30
    fnode = None
    for node in nodes:
        if not node:
            continue
        if node.id == ref.id:
            continue
        other = Rect(node).down()
        if other.up_of(rect):
            d = other.distance(rect)
            if d < distance:
                distance = d
                fnode = node
    return fnode


def down_one(nodes, ref):
    """return node in nodes down from ref"""
    rect = Rect(ref).down().shift_left(SHIFT)
    distance = 1 << 30
    fnode = None
    for node in nodes:
        if not node:
            continue
        if node.id == ref.id:
            continue
        other = Rect(node).up()
        if other.down_of(rect):
            d = other.distance(rect)
            if d < distance:
                distance = d
                fnode = node
    return fnode


def print_node(node):
    """print node info"""
    if not node:
        return
    if not DEBUG:
        return
    log('node:')
    log('\ttype: {}'.format(node.type))
    log('\tid: {}'.format(node.id))
    log('\tclass: {}'.format(node.window_class))
    log('\tname: {}'.format(node.name))
    log('\tlayout: {}'.format(node.layout))
    log('\torientation: {}'.format(node.orientation))
    log('\tx, y: {}, {}'.format(node.rect.x, node.rect.y))
    log('\tworkspace: {}'.format(node.workspace().id))
    log('\tstack: {}'.format(node.focus))


def usage():
    """print usage and quit"""
    print('usage: {} <left|right|up|down>'.format(sys.argv[0]))
    sys.exit(1)


if __name__ == '__main__':

    if len(sys.argv) < 1:
        usage()

    direction = sys.argv[1]
    if direction not in DIRECTIONS:
        usage()

    i3 = i3ipc.Connection()
    focused = i3.get_tree().find_focused()
    node = focus_node_direction(focused, direction[0])

    if node:
        if node.workspace().id != focused.workspace().id:
            save_last_workspace(focused.workspace().id)
        node.command('focus')

    sys.exit(0)

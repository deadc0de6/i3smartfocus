#!/usr/bin/env python3
# author: deadc0de6
#
# pylint: disable=E0012

"""
author: deadc0de6 (https://github.com/deadc0de6)
Copyright (c) 2020, deadc0de6
i3wm smart focus
"""


import sys
import os
import math
import tempfile
import i3ipc


VERSION = '0.1.3'
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
    sys.stderr.write(f'{string}\n')


# pylint: disable=R0903
class Point:
    """a point"""

    def __init__(self, xpos, ypos):
        """a point"""
        self.xval = xpos
        self.yval = ypos

    def distance(self, other):
        """return the distance to other"""
        xval1, yval1 = self.xval, self.yval
        xval2, yval2 = other.xval, other.yval
        xvals = (xval2-xval1)**2
        yvals = (yval2-yval1)**2
        return math.sqrt(xvals+yvals)


class Rect:
    """a rectangle"""

    def __init__(self, thenode):
        """a rectangle"""
        self.point = Point(thenode.rect.x, thenode.rect.y)
        self.width = thenode.rect.width
        self.height = thenode.rect.height

    def distance(self, other):
        """return distance to other"""
        return self.point.distance(other.point)

    def left_of(self, other):
        """return true if self is left of other"""
        if self.point.xval <= other.point.xval:
            return True
        return False

    def right_of(self, other):
        """return true if self is right of other"""
        if self.point.xval >= other.point.xval:
            return True
        return False

    def up_of(self, other):
        """return true if self is up of other"""
        if self.point.yval <= other.point.yval:
            return True
        return False

    def down_of(self, other):
        """return true if self is down of other"""
        if self.point.yval >= other.point.yval:
            return True
        return False

    def shift_left(self, count):
        """shift to the left"""
        self.point.xval = self.point.xval - count
        return self

    def shift_up(self, count):
        """shift up"""
        self.point.yval = self.point.yval - count
        return self

    def left(self):
        """shift to the left point"""
        xval = self.point.xval
        yval = self.point.yval + (self.height/2)
        self.point = Point(xval, yval)
        return self

    def right(self):
        """shift to the right point"""
        xval = self.point.xval + self.width
        yval = self.point.yval + (self.height/2)
        self.point = Point(xval, yval)
        return self

    def updir(self):
        """shift to the top point"""
        xval = self.point.xval + (self.width/2)
        yval = self.point.yval
        self.point = Point(xval, yval)
        return self

    def down(self):
        """shift to the bottom point"""
        xval = self.point.xval + (self.width/2)
        yval = self.point.yval + self.height
        self.point = Point(xval, yval)
        return self


def save_last_workspace(wsid):
    """save last workspace id to file"""
    try:
        with open(PATH, 'w', encoding='utf-8') as file:
            file.write(str(wsid))
    except Exception:  # pylint: disable=W0718,W0703
        pass


def get_last_workspace():
    """get last workspace id from file"""
    if not os.path.exists(PATH):
        return 0
    try:
        with open(PATH, 'r', encoding='utf-8') as file:
            val = file.read()
        return int(val)
    except Exception:  # pylint: disable=W0718,W0703
        return 0


def workspace_direction(where):
    """get workspace in direction"""
    cur = i3.get_tree().find_focused().workspace()
    if where == 'l':
        nodes = workspaces_left(cur)
    elif where == 'r':
        nodes = workspaces_right(cur)
    elif where == 'u':
        nodes = workspaces_up(cur)
    elif where == 'd':
        nodes = workspaces_down(cur)

    thenode = None
    if not nodes:
        return thenode

    if len(nodes) > 1:
        # find the focus stack
        lastid = get_last_workspace()
        if lastid in [ws.id for ws in nodes]:
            thenode = [n for n in nodes if n.id == lastid][0]
    else:
        thenode = nodes[0]

    return thenode


def focus_node_direction(ref, where):
    """focus on the node in direction direction"""
    leaves = ref.workspace().leaves()

    if where == 'l':
        thenode = left_one(leaves, ref)
    elif where == 'r':
        thenode = right_one(leaves, ref)
    elif where == 'u':
        thenode = up_one(leaves, ref)
    elif where == 'd':
        thenode = down_one(leaves, ref)

    if not thenode:
        # check if there's a workspace in that direction
        workspace = workspace_direction(where)
        print_node(workspace)
        if workspace:
            thenode = find_window_to_focus_on(workspace)
            print_node(thenode)
    return thenode


def find_window_to_focus_on(workspace):
    """find the window to fucus on in this workspace"""
    if not workspace:
        return None
    thenode = workspace
    while True:
        fids = thenode.focus
        if not fids:
            break
        thenode = thenode.find_by_id(fids[0])
    return thenode


def workspaces_left(ref):
    """return workspace on the left"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for workspace in workspaces:
        if workspace.id == ref.id:
            continue
        xval = workspace.rect.x
        if xval < ref.rect.x:
            res.append(workspace)
    return res


def workspaces_right(ref):
    """return workspace on the right"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for workspace in workspaces:
        if workspace.id == ref.id:
            continue
        xval = workspace.rect.x
        if xval > ref.rect.x:
            res.append(workspace)
    return res


def workspaces_up(ref):
    """return workspace above"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for workspace in workspaces:
        if workspace.id == ref.id:
            continue
        yval = workspace.rect.y
        if yval > ref.rect.y:
            res.append(workspace)
    return res


def workspaces_down(ref):
    """return workspace below"""
    res = []
    workspaces = i3.get_tree().workspaces()
    for workspace in workspaces:
        if workspace.id == ref.id:
            continue
        yval = workspace.rect.y
        if yval < ref.rect.y:
            res.append(workspace)
    return res


def left_one(nodes, ref):
    """return node in nodes left from ref"""
    rect = Rect(ref).left().shift_up(SHIFT)
    distance = 1 << 30
    fnode = None
    print_node(ref)
    for anode in nodes:
        if not anode:
            continue
        if anode.id == ref.id:
            continue
        other = Rect(anode).right()
        print_node(anode)
        if other.left_of(rect):
            dist = other.distance(rect)
            if dist < distance:
                distance = dist
                fnode = anode
    return fnode


def right_one(nodes, ref):
    """return node in nodes right from ref"""
    rect = Rect(ref).right().shift_up(SHIFT)
    distance = 1 << 30
    fnode = None
    for anode in nodes:
        if not anode:
            continue
        if anode.id == ref.id:
            continue
        other = Rect(anode).left()
        if other.right_of(rect):
            dist = other.distance(rect)
            if dist < distance:
                distance = dist
                fnode = anode
    return fnode


def up_one(nodes, ref):
    """return node in nodes top from ref"""
    rect = Rect(ref).updir().shift_left(SHIFT)
    distance = 1 << 30
    fnode = None
    for anode in nodes:
        if not anode:
            continue
        if anode.id == ref.id:
            continue
        other = Rect(anode).down()
        if other.up_of(rect):
            dist = other.distance(rect)
            if dist < distance:
                distance = dist
                fnode = anode
    return fnode


def down_one(nodes, ref):
    """return node in nodes down from ref"""
    rect = Rect(ref).down().shift_left(SHIFT)
    distance = 1 << 30
    fnode = None
    for anode in nodes:
        if not anode:
            continue
        if anode.id == ref.id:
            continue
        other = Rect(anode).updir()
        if other.down_of(rect):
            dist = other.distance(rect)
            if dist < distance:
                distance = dist
                fnode = anode
    return fnode


def print_node(anode):
    """print node info"""
    if not anode:
        return
    if not DEBUG:
        return
    log('node:')
    log(f'\ttype: {anode.type}')
    log(f'\tid: {anode.id}')
    log(f'\tclass: {anode.window_class}')
    log(f'\tname: {anode.name}')
    log(f'\tlayout: {anode.layout}')
    log(f'\torientation: {anode.orientation}')
    log(f'\tx, y: {anode.rect.x}, {anode.rect.y}')
    log(f'\tworkspace: {anode.workspace().id}')
    log(f'\tstack: {anode.focus}')


def usage():
    """print usage and quit"""
    print(f'usage: {sys.argv[0]} <left|right|up|down>')
    sys.exit(1)


if __name__ == '__main__':

    if len(sys.argv) < 1:
        usage()

    DIRECTION = sys.argv[1]
    if DIRECTION not in DIRECTIONS:
        usage()

    i3 = i3ipc.Connection()
    focused = i3.get_tree().find_focused()
    node = focus_node_direction(focused, DIRECTION[0])

    if node:
        if node.workspace().id != focused.workspace().id:
            save_last_workspace(focused.workspace().id)
        node.command('focus')

    sys.exit(0)

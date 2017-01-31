from enum import Enum


class ActionType(Enum):
    ADD_CONFIG = 1
    REMOVE_CONFIG = 2
    RESTORE_CONFIG = 3
    ADD_PKG = 4
    REMOVE_PKG = 5
    RESTORE_PKG = 6


class Result:
    action_type = None
    group = None
    arg = None

    def __init__(self, action_type, group, arg):
        self.action_type = action_type
        self.group = group
        self.arg = arg

    def __str__(self):
        return '{ action_type: %s; group: %s; arg: %s }' % (self.action_type, self.group, self.arg)

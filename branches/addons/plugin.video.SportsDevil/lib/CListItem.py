# -*- coding: latin-1 -*-

from string import *
import sys


class CListItem:
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

    def getInfo(self, key):
        if self.infos_names.__contains__(key):
            return self.infos_values[self.infos_names.index(key)]
        return None

    def setInfo(self, key, value):
        if self.infos_names.__contains__(key):
            self.infos_values[self.infos_names.index(key)] = value
        else:
            self.infos_names.append(key)
            self.infos_values.append(value)
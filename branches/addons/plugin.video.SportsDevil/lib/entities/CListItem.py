import string

class CListItem(object):
    
    def __init__(self):
        self.infos_names = []
        self.infos_values = []

    def __getitem__(self, key):
        return self.getInfo(key)

    def __setitem__(self, key, value):
        self.setInfo(key, value)

    def getInfo(self, key):
        if self.infos_names.__contains__(key):
            return self.infos_values[self.infos_names.index(key)]
        return None

    def setInfo(self, key, value):
        if key in self.infos_names:
            self.infos_values[self.infos_names.index(key)] = value
        else:
            self.infos_names.append(key)
            self.infos_values.append(value)

    def merge(self, item):
        for info_name in item.infos_names:
            if not self[info_name]:
                self[info_name] = item[info_name]

    def __str__(self):
        txt = ''
        for info_name in self.infos_names:
            txt += string.ljust(info_name,15) +':\t' + self[info_name] + '\n'
        return txt
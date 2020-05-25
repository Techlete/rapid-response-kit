# -*- coding: future_fstrings -*-
from collections import OrderedDict


class AlreadyRegistered(Exception):
    pass


class Registry(object):
    def __init__(self):
        self.registry = OrderedDict()

    def register(self, app_id, name, link):
        if app_id in self.registry:
            raise AlreadyRegistered

        print(f"Registering {name} at {link}")
        self.registry[app_id] = {
            'name': name,
            'link': link,
        }

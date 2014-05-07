__author__ = 'kristian'

class Assets(object):
     def __init__(self):
         self.__assets = 0

    def get_egg(self):
        return self.__egg

    def set_egg(self, egg):
        self.__egg = egg

    egg = property(get_egg, set_egg)

#!/usr/bin/python2.5


""" Common data.
"""


import struct

unpack = lambda fmt, *args: struct.unpack(fmt.encode('utf-8'), *args)
pack = lambda fmt, *args: struct.pack(fmt.encode('utf-8'), *args)


class Word(object):
    """ Representation of single word.
    """

    def __init__(self, value=None, meaning=None):
        self.value = value
        self.meaning = meaning

    def read(self, fp):
        """ Reads word from file.
        """

        value_length = unpack('!L', fp.read(4))[0]
        meaning_length = unpack('!L', fp.read(4))[0]

        self.value = fp.read(value_length).decode('utf-8')
        self.meaning = fp.read(meaning_length).decode('utf-8')

    def write(self, fp):
        """ Writes word to file.
        """

        value = self.value.encode('utf-8')
        meaning = self.meaning.encode('utf-8')

        fp.write(pack('!L', len(value)))
        fp.write(pack('!L', len(meaning)))

        fp.write(value)
        fp.write(meaning)

#!/usr/bin/python2.5


""" Dictionary for mobile phone.
"""


from common import Word, unpack


class Node(object):
    """ Node of dictionary.
    """

    def __init__(self, fp, address):

        self.address = address
        self.fp = fp

        fp.seek(address)

        children_count, = unpack('!L', fp.read(4))
        word_count, = unpack('!L', fp.read(4))
        self.word_count, = unpack('!L', fp.read(4))

        self.addresses = {}
        for i in range(children_count):
            way, address = unpack('!BL', fp.read(5))
            self.addresses[way] = address

        self.words = []
        for i in range(word_count):
            word = Word()
            word.read(fp)
            self.words.append(word)

    def __getitem__(self, way):
        address = self.addresses[way]
        return Node(self.fp, address)

    def get_words(self, count):
        """ Returns no more than ``count`` words.
        """

        if count <= 0:
            return []

        words = self.words
        count -= len(words)
        for address in self.addresses.values():
            result = Node(self.fp, address).get_words(count)
            words += result
            count -= len(result)
            if count <= 0:
                break

        return words


class Dict(object):
    """ Dictionary object.
    """

    def __init__(self, file_name):

        self.fp = open(file_name, 'rb')

        self.ways = self.read_ways(self.fp)
        self.root = Node(self.fp, self.fp.tell())

    def read_ways(self, fp):
        """ Reads ways from file.
        """

        ways_count = unpack('!L', fp.read(4))[0]

        ways = {}

        for i in range(ways_count):
            letter = unpack('!4s', fp.read(4))[0].decode(
                    'utf-8').replace('\0', '')

            way = []
            part = unpack('!B', fp.read(1))[0]
            while part & 0x80:
                way.append(part & 0x7f)
                part = unpack('!B', fp.read(1))[0]
            way.append(part)

            ways[letter] = way

        return ways

    def search(self, query):
        """ Searches for query in dict.
        """

        node = self.root

        for symbol in query:
            try:
                for part in self.ways[symbol]:
                    node = node[part]
            except KeyError:
                node = None
        return node

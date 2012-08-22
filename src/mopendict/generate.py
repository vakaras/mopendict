#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


""" Generates dict files for MOpenDict.
"""


from __future__ import unicode_literals

import os
import struct
import re

import icu

from common import Word, unpack, pack


WAYS_LIST = [
        ('1 ,.-/\'&`~!’*^<>',         [1,],),
        ('2aąäāàbcčćAĄÄĀÀBCČĆÅ',      [2,],),
        ('3deęėéèēfDEĘĖÉÈĒF',         [3,],),
        ('4ghiįīïGHIĮĪÏ',             [4,],),
        ('5jklJKLł',                  [5,],),
        ('6mnńoöóōMNŃOÖÓŌ',           [6,],),
        ('7pqrsšPQRSŠ',               [7,],),
        ('ßẞ',                        [7, 7,],),
        ('8tuųūüvTUŲŪÜV',             [8,],),
        ('9wxyzžźWXYZŽŹ',             [9,],),
        ]


def get_ways():
    """ Generates ways mapping.
    """

    ways = {}

    for letters, way in WAYS_LIST:
        for letter in letters:
            ways[letter] = way

    return ways


def write_ways(fp, ways):
    """ Dumps ways to a file.
    """

    fp.write(pack('!L', len(ways)))

    for letter, way in ways.items():

        fp.write(pack('!4s', letter.encode('utf-8')))

        for i, part in enumerate(way):
            if i + 1 < len(way):
                fp.write(pack('!B', 0x80 | part))
            else:
                fp.write(pack('!B', part))


class WriteNode(object):
    """ Dict tree node.
    """

    def __init__(self):

        self.address = None
        self.words = []

        self.addresses = {}             # Addresses of children nodes.
        self.children_nodes = {}

    def add_word(self, word):
        """ Adds word to word list.
        """

        self.words.append(word)

    def add_child(self, way, node):
        """ Adds child node.
        """

        self.children_nodes[way] = node

    def write(self, fp):
        """ Recursively writes node into file.
        """

        self.address = fp.tell()

        fp.write(pack('!L', len(self.children_nodes)))
        fp.write(pack('!L', len(self.words)))
        fp.write(pack('!L', 0xDEADBABA))
                                        # Placeholder for word count.

        ways = []
        for way in self.children_nodes:
            ways.append(way)
            fp.write(pack('!BL', way, 0xDEADBABA))
                                        # Placeholder for address.

        for word in self.words:
            word.write(fp)

        words_count = len(self.words)

        for child in self.children_nodes.values():
            words_count += child.write(fp)

        end_position = fp.tell()

        fp.seek(self.address + 8)
        fp.write(pack('!L', words_count))

        for i, way in enumerate(ways):
            fp.seek(self.address + 12 + 5 * i + 1)
            fp.write(pack('!L', self.children_nodes[way].address))

        fp.seek(end_position)

        return words_count



def write():
    """ Writes dictionary to file.
    """

    fp = open('bla.dict', 'wb')

    write_ways(fp, get_ways())
    word = Word('Labas', 'Ačiū')
    word.write(fp)

    root = WriteNode()
    child = WriteNode()
    child.add_word(word)
    root.add_child(3, child)
    root.write(fp)

    fp.close()


def read():
    """ Reads dictionary from file.
    """

    fp = open('bla.dict', 'rb')

    ways = read_ways(fp)

    word = Word()
    word.read(fp)

    root = ReadNode(fp, fp.tell())
    child = root[3]

    fp.close()


def create(input_file, output_file):
    """ Creates dict file.
    """

    # Construct tree.
    ways = get_ways()

    root = WriteNode()

    for i, row in enumerate(open(input_file, 'rb')):
        try:

            value, meaning = row.decode('utf-8').split(u'=', 1)

            def add(value, meaning):
                node = root
                for letter in value:
                    for part in ways[letter]:
                        try:
                            node = node.children_nodes[part]
                        except KeyError:
                            child = WriteNode()
                            node.add_child(part, child)
                            node = node.children_nodes[part]
                node.add_word(Word(value, meaning))

            add(value, meaning)
        except KeyError as e:
            print i, e.message
        except:
            print '{0}: --->{1}<---'.format(i, row.decode('utf-8'))
            raise

    # Write data.
    fout = open(output_file, 'wb')

    write_ways(fout, ways)
    root.write(fout)


def clean(infilename, outfilename, localename):
    """ Cleans dwa file.
    """
    lines = set()
    for line in open(infilename):
        line = line.decode('utf-8')[:-1]
        if not line.startswith('#'):
            lines.add(line)

    with open(outfilename, 'wb') as fout:
        collator = icu.Collator.createInstance(icu.Locale(localename))
        collator.setStrength(collator.SECONDARY)
        write = lambda v, m: fout.write(
                u'{0}={1}\n'.format(v, m).encode('utf-8'))
        slines = [
                (bytes(collator.getCollationKey(line).getByteArray()), line)
                for line in lines
                ]
        for key, line in sorted(slines):
            values, meaning = line.split('=', 1)
            for value in values.replace(';', ',').split(','):
                if len(value) > 20:
                    print 'long word:', value
                value = value.replace('|', '')
                match = re.match(r'(.*)\((.*)\)(.*)', value, re.UNICODE)
                if match:
                    groups = match.groups()
                    write(groups[0] + groups[2], meaning)
                    write(''.join(groups), meaning)
                else:
                    write(value, meaning)


def generate(args):
    """ This script cleans dwa file and creates dict file for it.
    """
    input_name, locale_name = args
    base_name = os.path.splitext(input_name)[0]
    clean_name = base_name + '.clean.dwa'
    output_name = base_name + '.mdict'
    clean(input_name, clean_name, locale_name)
    create(clean_name, output_name)


def convert(args):
    """ This scripts cleans dwa file and creates DictDB for GoldenDict.

    Requires dictdlib library::

        sudo apt-get install python-dictdlib
    """
    input_name, locale_name = args
    base_name = os.path.splitext(input_name)[0]
    output_name = base_name
    clean_name = base_name + '.clean.dwa'
    clean(input_name, clean_name, locale_name)

    from dictdlib import DictDB
    db = DictDB(output_name.decode('utf-8'), mode='write')
    with open(clean_name) as fin:
        for i, line in enumerate(fin):
            try:
                word, meaning = line.decode('utf-8')[:-1].split('=', 1)
                match = re.match(r'(.*)(\w*)(\d*)', word, re.UNICODE)
                db.addentry(
                        meaning.encode('utf-8'),
                        [match.groups()[0].encode('utf-8')])
            except:
                print i, line
                raise
    db.finish()

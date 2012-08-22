#!/usr/bin/python2.7
# -*- encoding: utf-8 -*-


"""
Script, which downloads words from http://www.vokieciu-lietuviu.com.

http://www.vokieciu-lietuviu.com/A/
http://www.vokieciu-lietuviu.com/A/10/
http://www.vokieciu-lietuviu.com/A-Bombe/
"""


import time

from mechanize import Browser


class Downloader(object):
    """ Downloads all words.
    """

    def __init__(self):

        self.browser = Browser()
        self.browser.set_handle_robots(False)
        self.words = open('tmp.dict', 'ab')

    def parse_word(self, url):
        """ Downloads word description.
        """

        print 'Parsing:', url
        page = self.browser.follow_link(tag="a", url=url).read()
        page = self.browser.follow_link(text_regex=r'taisyti').read()

        self.browser.back()
        self.browser.back()

        word, meaning = page.split('<textarea')
        word = word.split('<h2>')[-1].split('</h2>')[0]
        meaning = meaning.split('>', 1)[1]
        meaning = meaning.split('</textarea>')[0]

        for search, replace in [
                ('\n', '',),
                #('\x8d', u'\u2013\u0308'.encode('utf-8'),),
                ]:
            word = word.replace(search, replace)
            meaning = meaning.replace(search, replace)

        self.words.write(word)
        self.words.write('=')
        self.words.write(meaning)
        self.words.write('\n')

    def parse_page(self, url):
        """ Downloads all words from single page.
        """

        print 'Parsing:', url
        page = self.browser.open(url).read()

        page = page.split('<table cellpadding="6"><tr valign="top"><td>')[1]
        page = page.split('</td></tr></table>')[0]
        page = page.replace('</td>\n<td>', '')

        open('tmp.html', 'wb').write(page)

        for a in page.split('\n'):
            try:
                word_url = a.split('\"')[1]
            except IndexError:
                continue
            oldurl = self.browser.geturl()
            try:
                self.parse_word(word_url)
            except Exception as e:
                print "Error:", e
                self.browser.open(oldurl)

        time.sleep(10)

    def parse_letter(self, url):
        """ Downloads all words from given letter page.
        """

        print 'Parsing:', url

        page = self.browser.open(url).read()
        page = page.split('</a></p></td></tr></table>')[0]
        open('tmp.html', 'wb').write(page)
        try:
            pages_count = int(page.split('\">')[-1])
        except ValueError:
            pages_count = 1

        for i in range(pages_count):
            self.parse_page(url + str(i + 1) + '/')

        time.sleep(60)

    def parse(self, url, skip):
        """ Downloads all words from given url.
        """

        page = self.browser.open(url).read()
        page = page.split('bgcolor="#FFD780" colspan="2">')[1]
        page = page.split('</td></tr><tr>', 1)[0]

        for i, a in enumerate(page.split(' | ')):
            if i < skip:
                continue
            letter_url = a.split('\"')[1]
            self.words.write('#LETTER ({1}):{0}\n'.format(letter_url, i))
            self.parse_letter(url + letter_url)


def main(args):
    """ This script downloads words from website to dwa file.
    :param url: Website root.
    :param skip: How many letters to skip.
    """
    url, skip = args
    print 'URL:', url
    print 'SKIP:', skip
    downloader = Downloader()
    downloader.parse(url, int(skip))


if __name__ == '__main__':
    args = ['http://www.vokieciu-lietuviu.com/', 0]
    main(args)

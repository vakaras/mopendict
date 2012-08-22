#!/usr/bin/python2.5
# -*- coding: utf-8 -*-


""" Info:

Layout: file:///home/vakaras/Atsiuntimai/Nokia/devenv/PythonForS60/doc/s60/node16.html
App: file:///home/vakaras/Atsiuntimai/Nokia/devenv/PythonForS60/doc/s60/node19.html
ListBox: file:///home/vakaras/Atsiuntimai/Nokia/devenv/PythonForS60/doc/s60/node22.html

http://blog.terzza.com/tradesmans60-pys60-example-app/
http://www.mobilenin.com/pys60/info_ how_to_build_an_pys60_app.htm
http://croozeus.com/blogs/?p=215
http://fosshelp.blogspot.com/2010/01/pys60-tutorial-canvas.html

Bandymai surasti formos naudojimo pavyzdį:
http://duckduckgo.com/?q=python+s60+appuifw+example+form+
http://www.mobilenin.com/pys60/info_tabs_forms.htm
http://www.developer.nokia.com/Community/Discussion/showthread.php?104701-s60-python-form
http://lfdm.net/thesis/index.php/2007/03/26/46-use-of-form
http://www.developer.nokia.com/Community/Wiki/How_to_use_layout_in_Python_for_S60
http://postneo.com/talks/pycon2006/
http://postneo.com/2005/04/05/useful-python-for-series-60-app-dict2go


python ensymble.py py2sis \
        --appname="MOpenDict"\
        --shortcaption="MOpenDict"\
        --caption="MOpenDict"\
        modict/gui.py

"""


import sys
import os


sys.path.append('C:\\Data\\python')


import appuifw
import e32
import sysinfo
import key_codes
import textwrap

from mopendict import Dict


DICTS_DIR = 'E:\\Dictionaries'


class DictApp(object):
    """ Dict application.
    """

    def __init__(self, app):
        """

        +   ``query`` -- search query, a list of digits stored as
            unicode strings.
        +   ``canvas`` -- screen.
        +   ``results`` -- list of search results.
        +   ``shown_count`` -- how many items are shown.
        +   ``results_count`` -- how many items matches query.
        +   ``result_shown`` -- which result is shown now. (None, if none.)

        """

        self.query = []
        self.query_match = -1
        self.screen_w, self.screen_h = sysinfo.display_pixels()
        self.app = app
        self.canvas = appuifw.Canvas(
                event_callback=self.handle_event,
                redraw_callback=self.handle_redraw,
                )
        self.app.body = self.canvas
        self.canvas.dictionary = self

        self.results = []
        self.active_result = None

        self.key_numbers = dict([
            (getattr(key_codes, 'EScancode' + str(i)), unicode(i))
            for i in range(10)
            ])

        self.dictionary = Dict(os.path.join(DICTS_DIR, 'de.dict'))


    def handle_redraw(self, rect=None):
        """ Handles redraw.
        """

        if not hasattr(self, 'results'):
            print 'Skipped.'
            return

        line_spacing = 5
        text_size = 20

        self.canvas.clear()
        x = 5
        y = text_size + line_spacing

        # Print query.
        self.canvas.text(
                (x, y),
                u''.join(
                    [u'(', unicode(self.query_match), u') '] + self.query),
                0x008000,
                font=(u'Nokia Hindi S60', text_size, appuifw.STYLE_BOLD))

        for i, result in enumerate(self.results):
            if i == self.active_result:
                font_style = appuifw.STYLE_BOLD | appuifw.STYLE_UNDERLINE
            else:
                font_style = 0
            y += text_size + line_spacing
            self.canvas.text(
                    (x, y),
                    result.value,
                    0x008000,
                    font=(u'Nokia Hindi S60', text_size, font_style))
        print 'worked', self.active_result

    def show_description(self):
        """ Paints word description.
        """

        if self.active_result is None:
            return

        result = self.results[self.active_result]
        line_spacing = 5
        text_size = 12

        self.canvas.clear()
        x = 5
        y = text_size + line_spacing

        self.canvas.text(
                (x, y), result.value, 0x008000,
                font=(u'Nokia Hindi S60', text_size, appuifw.STYLE_BOLD))

        for i, line in enumerate(textwrap.wrap(result.meaning, width=40)):
            y += text_size + line_spacing
            self.canvas.text(
                    (x, y), line, 0x008000,
                    font=(u'Nokia Hindi S60', text_size, 0))

    def handle_event(self, event):
        """ Handles event.
        """

        if event['type'] != appuifw.EEventKeyDown:
            return

        print 'Result length:', len(self.results)

        if event['scancode'] == key_codes.EScancodeLeftArrow:
            pass
            # TODO: Load previous dictionary.
        if event['scancode'] == key_codes.EScancodeRightArrow:
            pass
            # TODO: Load next dictionary.
        if event['scancode'] == key_codes.EScancodeStar:
            self.query = []
        if event['scancode'] == key_codes.EScancodeSelect:
            self.show_description()
            return
        if event['scancode'] == key_codes.EScancodeUpArrow:
            if self.active_result is not None:
                self.active_result = max(0, self.active_result - 1)
        if event['scancode'] == key_codes.EScancodeDownArrow:
            if self.active_result is not None:
                self.active_result = min(
                        len(self.results) - 1, self.active_result + 1)

        if event['scancode'] == key_codes.EScancodeBackspace:
            self.handle_number_press(u'c')
        try:
            number = self.key_numbers[event['scancode']]
        except KeyError:
            pass
        else:
            self.handle_number_press(number)

        self.handle_redraw()
        print 'Called redraw.'

    def handle_number_press(self, number):
        """ Search for an item. -1 means, that "c" key was pressed.
        """

        if number == u'c':
            try:
                self.query.pop()
            except IndexError:
                pass
        else:
            self.query.append(number)

        result = self.dictionary.search(self.query)
        self.results = result.get_words(10)
        self.query_match = result.word_count

        if self.results:
            self.active_result = 0
        else:
            self.active_result = None


if __name__ == '__main__':

    app_lock = e32.Ao_lock()
    appuifw.app.exit_key_handler = app_lock.signal

    appuifw.app.screen = 'full'
    dict_app = DictApp(appuifw.app)
    app_lock.wait()
    print 'Post mortem:', dict_app.results

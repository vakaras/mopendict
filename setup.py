#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup


setup(
        name=u'mopendict'.encode('utf-8'),
        version='0.1',
        author=u'Vytautas Astrauskas'.encode('utf-8'),
        author_email=u'vastrauskas@gmail.com'.encode('utf-8'),
        packages=['mopendict',],
        package_dir={'': 'src'},
        #package_data={'mopendict': []},
                                        # List of data files to be included 
                                        # into package.
        requires=[
            'distribute',
            ],
        install_requires=[              # Dependencies for the package.
            'mechanize',
            'PyICU',
            ],
        scripts=[],                     # List of python script files.
        #data_files=[('/etc/init.d', ['init-script'])]
                                        # List of files, which have to
                                        # be installed into specific 
                                        # locations.
        #url='',                        # Home page.
        #download_url='',               # Page from which package could
                                        # be downloaded.
        description=u'mopendict'.encode('utf-8'),
        long_description=(
            open('README.rst').read()+open('CHANGES.txt').read()),
        # Full list of classifiers could be found at:
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        entry_points = {
            'console_scripts': [
                'download = mopendict.download:main',
                'generate = mopendict.generate:generate',
                'convert = mopendict.generate:convert',
                ]
            },
        classifiers=[
            'Development Status :: 1 - Planning',
            #'Environment :: Console',
            #'Framework :: Django',
            'Intended Audience :: Developers',
            (
                'License :: OSI Approved :: '
                'GNU Library or Lesser General Public License (LGPL)'),
            #'Natural Language :: Lithuanian',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            (
                'Topic :: Software Development :: Libraries :: '
                'Python Modules'),
            ],
        license='LGPL'
        )

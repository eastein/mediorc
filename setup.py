#!/usr/bin/env python

from distutils.core import setup

setup(name='mediorc',
      version='0.1.0',
      description='Mediorc IRC Bot Helpers Library',
      author='Eric Stein',
      author_email='toba@des.truct.org',
      url='https://github.com/eastein/mediorc/',
      packages=['mediorc', 'mediorc_dns'],
      install_requires=['dnspython'] # I'd like to require python-irclib properly in the dependencies but it's broken on PyPi right now.
     )

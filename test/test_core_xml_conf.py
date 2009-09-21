#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pigeoncide.
#
#  Pigeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pigeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest
from core.conf import *
from core.xml_conf import *
from core.util import read_file
import os

XML_TEST_FILENAME = 'test/test_core_xml_conf_test_file.xml'
XML_TEMP_FILENAME = 'test/test_core_xml_conf_temp_file.xml'

class TestXmlConfWrite (unittest.TestCase):

    def test_write (self):
        conf = ConfNode ('test')
        conf.get_path ('a').value = 1
        conf.get_path ('b.c').value = 2
        conf.get_path ('b.d').value = 3

        xml = XmlConfBackend (XML_TEMP_FILENAME)
        conf.set_backend (xml)

        conf.save ()

        self.assertEqual (read_file (XML_TEST_FILENAME),
                          read_file (XML_TEMP_FILENAME))

        os.remove (XML_TEMP_FILENAME)

class TestXmlConfRead (unittest.TestCase):

    def setUp (self):
        self.conf = ConfNode ()
        self.xml = XmlConfBackend (XML_TEST_FILENAME)
        self.conf.set_backend (self.xml)

    def test_read (self):
        self.conf.load ()

        self.assertEqual (self.conf.get_name (), 'test')
        self.assertEqual (self.conf.get_path ('a').value, 1)
        self.assertEqual (self.conf.get_path ('b.c').value, 2)
        self.assertEqual (self.conf.get_path ('b.d').value, 3)

    def test_read_default (self):
        self.conf.get_child ('a').value = 10
        self.conf.load (False)

        self.assertEqual (self.conf.get_name (), 'test')
        self.assertEqual (self.conf.get_path ('a').value, 10)
        self.assertEqual (self.conf.get_path ('b.c').value, 2)
        self.assertEqual (self.conf.get_path ('b.d').value, 3)


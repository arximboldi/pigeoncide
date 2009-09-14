#
#  Copyright (C) 2009 Juan Pedro Bolivar Puente, Alberto Villegas Erce
#  
#  This file is part of Pidgeoncide.
#
#  Pidgeoncide is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#  
#  Pidgeoncide is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

from core.tree import *

class TestAutoTree (unittest.TestCase):

    class ValueTree (AutoTree):
        def __init__ (self, default = None):
            AutoTree.__init__ (self)
            self.value = default

    class CountingTree (AutoTree):
        def __init__ (self):
            AutoTree.__init__ (self)
            self.childs = 0
        def _on_new_child (self, child):
            self.childs += 1
        def _on_remove_child (self, child):
            self.childs -= 1

    def setUp (self):
        self._tree_1 = TestAutoTree.ValueTree ()
        self._tree_1.get_child ('a').value = 1
        self._tree_1.get_path ('a.b.c').value = 2

    def tearDown (self):
        self._tree_1 = None

    def test_01 (self):
        child_1 = self._tree_1.get_child ('a')
        child_2 = self._tree_1.get_path ('a.b.c')

        self.assertEqual (child_1.value, 1)
        self.assertEqual (child_2.value, 2)
        self.assertEqual (child_2.get_path_name (), '.a.b.c')

        child_1.rename ('d')
        self.assertEqual (child_2.get_path_name (), '.d.b.c')
    
    def test_02 (self):
        child = self._tree_1.get_path ('a.b')
        self._tree_1.get_child ('d').adopt (child, 'b')

        self.assertEqual (self._tree_1.get_path ('a.b.c').value, None)
        self.assertEqual (self._tree_1.get_path ('d.b.c').value, 2)

    def test_03 (self):
        tree = TestAutoTree.CountingTree ();

        tree.get_child ('a')
        self.assertEqual (tree.childs, 1)
        tree.get_child ('b')
        self.assertEqual (tree.childs, 2)
        tree.get_child ('a')
        self.assertEqual (tree.childs, 2)
        tree.remove ('a')
        self.assertEqual (tree.childs, 1)
        tree.remove ('b')
        self.assertEqual (tree.childs, 0)


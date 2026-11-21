#
#  Copyright (C) 2010 Juan Pedro Bolivar Puente, Alberto Villegas Erce
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

"""
Where the game finds its files.
"""

import os

from base.util import IN_BROWSER

# The web build preloads data/ and src/core/sha/ under this directory of the
# page's in-memory file system. Frozen modules have no usable __file__.
WEB_ROOT = '/pigeoncide'

# The source tree and installed copies keep data/ next to src/.
GAME_DIR = WEB_ROOT if IN_BROWSER else os.path.normpath (
    os.path.join (os.path.dirname (os.path.abspath (__file__)),
                  os.pardir, os.pardir))

DATA_DIR = os.path.join (GAME_DIR, 'data')
SHADER_DIR = os.path.join (GAME_DIR, 'src', 'core', 'sha')

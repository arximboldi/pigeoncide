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

from test.base_arg_parser import *
from test.base_tree import *
from test.base_sender import *
from test.base_connection import * 
from test.base_signal import *
from test.base_meta import *
from test.base_observer import *
from test.base_observer_old import *
from test.base_conf import *
from test.base_xml_conf import *
from test.base_singleton import *
from test.base_log import *
from test.base_event import *
from test.base_changer import *

from test.core_task import *
from test.core_state import *


if __name__ == '__main__':
    unittest.main ()

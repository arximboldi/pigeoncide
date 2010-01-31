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

from base.conf import GlobalConf

    
DEFAULT_PLAYER0_KEYS = [
    ('on_move_forward'  , 'panda-w'),
    ('on_move_backward' , 'panda-s'),
    ('on_strafe_left'   , 'panda-a'),
    ('on_strafe_right'  , 'panda-d'),
    ('on_steer_left'    , 'panda-k'),
    ('on_steer_right'   , 'panda-l'),
    ('on_throw_weapon'  , 'panda-r'),
    ('on_place_stick'   , 'panda-q'),
    ('on_feed'          , 'panda-f'),
    ('on_jump'          , 'panda-space'),
    ('on_run'           , 'panda-c'),
    ('on_hit'           , 'panda-e')
    ]

def load_game_defaults ():
    cfg = GlobalConf ().path('game.player0.keys')
    for act, key in DEFAULT_PLAYER0_KEYS:
        cfg.child (act).default (key)
        
    GlobalConf ().path ('game.shader').default (True)

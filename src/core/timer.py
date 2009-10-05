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

import sys
import time
import base.log

precise_clock = time.clock if sys.platform=='win32' else time.time

_log = base.log.get_log (__name__)

class TimerBase (object):

    def reset ():
        pass

    @property
    def delta (self):
        pass

    @property
    def elapsed (self):
        pass

    @property
    def frames (self):
        pass
    
    def loop (self, func):
        self.tick ()
        while func (self):
            self.tick ()

    def tick (self):
        pass

class Timer (TimerBase):

    def __init__ (self):
        self._fps = 0  # frames per second
        self._rate = 0  # ticks per frame
        self.reset ()
        
    def reset (self):
        self._frame_count = 0        # frames since last delay
        self._total_frame_count = 0  # frames since last resert

        self._delta = 0                  # time between last two sleeps
        self._start_time = precise_clock ()  # start time
        self._time_count = 0.0  # time since last reset
        self._last_time  = 0.0 # time since last delay

    @property
    def frames (self):
        return self._total_frame_count

    @property
    def delta (self):
        return self._delta

    @property
    def elapsed (self):
        return self._time_count

    def _get_fps (self):
        return self._fps

    def _set_fps (self, val):
        self._fps = val
        if self._fps > 0:
            self._rate = 2.0 / float (self._fps)
        
    def tick (self):
        self._total_frame_count += 1
        
        if self._fps > 0:
            _log.debug ('Ticking with FPS limit.')
            
            self._total_frame_count += 1
            self._frame_count += 1
            self._target_time = self._last_time + self._frame_count * self._rate

            self._update_ticks ()
            
            if self._time_count < self._target_time:
                time.sleep (self._target_time - self._time_count)                
            else:
                self._last_time = self._time_count
                self._frame_count = 0
        else:
            _log.debug ('Ticking normally.')
            self._update_ticks ()

    def _update_ticks (self):
        newtime = precise_clock () - self._start_time
        self._delta = newtime - self._time_count
        self._time_count = newtime
    
    fps = property (_get_fps, _set_fps)


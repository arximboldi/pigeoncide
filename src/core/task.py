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

from base.util import *
from weakref import proxy
from error import *
from base.log import *
from base import util
import math


_log = get_log (__name__)


class TaskError (CoreError):
    pass


killed  = 0
running = 1
paused  = 2

class Task (object):

    def __init__ (self, *a, **k):
        super (Task, self).__init__ (*a, **k)
        self._state = running
        self._next  = []
        self._task_manager = None

    def do_update (self, timer):
        pass

    def add_next (self, task):
        self._next.append (task)
        return task
    
    def update (self, timer):
        if self._state == running:
            self.do_update (timer)
        return self._state
    
    def pause (self):
        if self._state != killed:
            self._state = paused

    def resume (self):
        if self._state != killed:
            self._state = running

    def toggle_pause (self):
        if self._state != killed:
            self._state = running if self._state == paused else paused
    
    def restart (self):
        self._state = running

    def kill  (self):
        self._state = killed
        if self._task_manager:
            for task in self._next:
                self._task_manager.add (task)
        
    def is_paused (self):
        return self._state == paused

    def is_killed (self):
        return self._state == killed

    @property
    def state (self):
        return self._state

    @property
    def parent_task (self):
        return self._task_manager
    
    def _set_parent (self, manager):
        if self._task_manager and manager:
            raise TaskError ("Already attached to: " + str (self._task_manager))
        self._task_manager = manager


class FuncTask (Task):

    def __init__ (self, func = None, *a, **k):
        assert func != None
        super (FuncTask, self).__init__ (*a, **k)
        self._set_func (func)
        
    def _set_func (self, func):
        if func.func_code.co_argcount < 1:
            self._orig = func
            self._func = lambda t: func ()
        else:
            self._orig = self._func = func

    def _get_func (self):
        return self._orig
    
    def do_update (self, timer):
        super (FuncTask, self).do_update (timer)
        action = self._func (timer)
        if not action or action == killed:
            self.kill ()
        elif action == paused:
            self.pause ()

    func = property (_get_func, _set_func)


def totask (task):
    if not isinstance (task, Task):
        if not callable (task):
            raise TaskError ('You can add either tasks or callables.')
        task = FuncTask (func = task)    
    return task


class TaskGroup (Task):

    auto_kill = True
    
    def __init__ (self, *tasks, **k):
        super (TaskGroup, self).__init__ (**k)
        self._tasks = []
        for task in tasks:
            self.add (task)

    def __del__ (self):
        self.clear ()
    
    def clear (self):
        for t in self._tasks:
            t._set_parent (None)
        self._tasks = []
        
    def do_update (self, timer):
        super (TaskGroup, self).do_update (timer)
        for task in self._tasks:
            task.update (timer)
        self._tasks = remove_if (Task.is_killed, self._tasks)

        if self.auto_kill and not self._tasks:
            self.kill ()
    
    def add (self, task):
        task = totask (task)
        task._set_parent (self)
        self._tasks.append (task)
        return task

    def remove (self, task):
        self._tasks.remove (task)
        task._set_parent (None)

    def find (self, func):
        for task in self._tasks:
            if isinstance (task, FuncTask) and \
               task.func == func:
                return task

    @property
    def count (self):
        return len (self._tasks)


class WaitTask (Task):

    def __init__ (self, time = 0., *a, **k):
        super (WaitTask, self).__init__ (*a, **k)
        self.remaining = time
                
    def do_update (self, timer):
        super (WaitTask, self).do_update (timer)
        self.remaining -= timer.delta
        if self.remaining <= 0:
            self.kill ()
            self.remaining = 0


class TimerTask (WaitTask):

    def do_update (self, timer):
        super (TimerTask, self).do_update (timer)
        if self.remaining == 0:
            self.on_finish ()
        else:
            self.on_tick ()
    
    def on_tick (self):
        pass

    def on_finish (self):
        pass


class FadeTask (Task):

    def __init__ (self,
                  func = nop,
                  duration = 1.0,
                  loop = False,
                  init = False,
                  *a, **k):
        super (FadeTask, self).__init__ (*a, **k)
        self.func      = func
        self.curr      = 0.
        self.loop      = loop
        self.duration = duration

        if init: 
            func (0.0)

    def do_update (self, timer):
        super (FadeTask, self).do_update (timer)
        self.func (self.curr / self.duration)
        self.curr += timer.delta / self.duration

        if self.curr >= self.duration:
            if self.loop:
                self.curr -= self.duration
            else:
                self.curr = self.duration
                self.kill ()
                self.func (self.curr)


def sequence (fst, *tasks):
    task  = totask (fst)
    tasks = map (totask, tasks)

    for nxt in tasks:
        task = task.add_next (nxt)

    return fst

parallel = TaskGroup

wait = WaitTask

fade = FadeTask

def invfade (f, *a, **k):
    return fade (lambda x: f (1.0 - x), *a, **k)

def linear (f, min, max, *a, **k):
    return fade (lambda x: f (util.linear (min, max, x)), *a, **k)

def sinusoid (f, min = 0.0, max = 1.0, *a, **k):
    return fade (
        lambda x: f (min + (max - min) * math.sin (x * math.pi / 2.)), *a, **k)

def run (func):
    return FuncTask (lambda t: None if func () else None)

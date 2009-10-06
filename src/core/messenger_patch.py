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

from direct.showbase.Messenger import Messenger

from base.meta import *
from base.log import get_log

_log = get_log (__name__)


@monkeypatch_extend (Messenger, '__init__')
def messenger_init (self):
    _log.debug ('Building messenger')
    self._patch_forwarders = []
    self._patch_event_queues = {}


@monkeypatch (Messenger)
def _patch_add_forwarder (self, forwarder):
    self._patch_forwarders.append (forwarder)


@monkeypatch (Messenger)
def _patch_del_forwarder (self, forwarder):
    self._patch_forwarders.remove (forwarder)


@monkeypatch_extend (Messenger)
def send (self, orig_event, sent_args=[], task_chain=None):
    event = 'panda_' + orig_event
    self.lock.acquire()
    try:
        if task_chain:
            from direct.task.TaskManagerGlobal import taskMgr

            queue = self._patch_event_queues [task_chain]
            queue.append ((event, sent_args))
            if len (queue) == 1:
                taskMgr.add (self._patch_task_chain_forward,
                             name = '_patch_Messenger-%s' % (task_chain),
                             extraArgs = [task_chain],
                             taskChain = task_chain,
                             appendTask = True)
        else:
            self._patch_forward (event, sent_args)
    finally:
        self.lock.release()


@monkeypatch (Messenger)
def _patch_forward (self, event, sent_args=[]):
    _log.debug ('Forwarding panda event: ' + event)
    for f in self._patch_forwarders:
        f.notify (event, *sent_args)


@monkeypatch (Messenger)
def _patch_task_chain_forward (self, task_chain, task):
    while True:
        self.lock.acquire ()
        try:
            queue = self._patch_event_queues.get (task_chain, None)
            if queue:
                event_tuple = queue.pop (0)
            if not queue and queue is not None:
                del self.__patch_event_queues [task_chain]
            if not event_tuple:
                return task.done
                
            self.__patch_forward (*event_tuple)
        finally:
            self.lock.release ()
    assert False, 'Should not reach!'
    return task.done

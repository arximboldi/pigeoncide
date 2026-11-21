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


# Parameter names must match Messenger.send, since monkeypatch_extend passes
# the caller's keyword arguments to both functions.
@monkeypatch_extend (Messenger)
def send (self, event, sentArgs=[], taskChain=None):
    event = 'panda-' + event
    self.lock.acquire()
    try:
        if taskChain:
            from direct.task.TaskManagerGlobal import taskMgr

            queue = self._patch_event_queues.setdefault (taskChain, [])
            queue.append ((event, sentArgs))
            if len (queue) == 1:
                taskMgr.add (self._patch_task_chain_forward,
                             name = '_patch_Messenger-%s' % (taskChain),
                             extraArgs = [taskChain],
                             taskChain = taskChain,
                             appendTask = True)
        else:
            self._patch_forward (event, sentArgs)
    finally:
        self.lock.release()


@monkeypatch (Messenger)
def _patch_forward (self, event, sentArgs=[]):
    # _log.debug ('Forwarding panda event: ' + event)
    for f in self._patch_forwarders:
        f.receive (event, *sentArgs)


@monkeypatch (Messenger)
def _patch_task_chain_forward (self, taskChain, task):
    # Drains the queue in send order, like Messenger.__taskChainDispatch.
    while True:
        event_tuple = None
        self.lock.acquire ()
        try:
            queue = self._patch_event_queues.get (taskChain, None)
            if queue:
                event_tuple = queue.pop (0)
            if not queue and queue is not None:
                del self._patch_event_queues [taskChain]
            if not event_tuple:
                return task.done

            self._patch_forward (*event_tuple)
        finally:
            self.lock.release ()

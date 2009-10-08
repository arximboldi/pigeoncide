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

import new

from signal import *
from meta import *
from connection import *

class Naming:
    SUBJECT_CLASS_POSTFIX  = 'Subject'
    LISTENER_CLASS_POSTFIX = 'Listener'

def make_observer (signals,
                   prefix = 'Some',
                   subject_doc = '',
                   listener_doc = '',
                   default_ret = None,
                   use_signals = True,
                   names = Naming):
    
    listener = type (
        prefix + names.LISTENER_CLASS_POSTFIX,
        (Receiver,),
        { '__doc__' : listener_doc
        , 'SIGNALS' : signals
        , 'DEFAULT_RETURN' : default_ret
        })

    _extend_observer_class (listener, _listener_make_signal)
    
    subject = type (
        prefix + names.LISTENER_CLASS_POSTFIX,
        (Sender,),
        { '__doc__' : subject_doc
        , 'SIGNALS' : signals
        , 'DEFAULT_RETURN' : default_ret
        })

    _extend_observer_class (subject,
                            _signal_subject_make_signal if use_signals else
                            _subject_make_signal)

    return subject, listener

def _extend_observer_class (cls, build_signal_fn):
    for message in cls.SIGNALS:
        method = build_signal_fn (cls, message)
        method.__name__ = message
        if isinstance (cls.SIGNALS, dict):
            method.__doc__ = cls.SIGNALS [message]
        setattr (cls, message, method)

def _listener_make_signal (cls, name):
    return lambda self, *a, **k: cls.DEFAULT_RETURN
    
def _subject_make_signal (cls, name):
    return lambda self, *a, **k: self.send (name, a, k)

def _signal_subject_make_signal (cls, name):
    func = lambda *a, **k: None
    func.__name__ = name
    return signal (func)


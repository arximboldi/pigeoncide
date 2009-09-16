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

from signal import *

class Naming:
    SUBJECT_CLASS_POSTFIX  = 'Subject'
    LISTENER_CLASS_POSTFIX = 'Listener'

    SIGNAL_PREFIX          = 'on_'
    SLOT_PREFIX            = '_slot_'
    HANDLER_PREFIX         = 'handle_'

    DISCONNECT_FUNCTION    = 'disconnect'
    ADD_LISTENER_FUNCTION  = 'add_listener'
    DEL_LISTENER_FUNCTION  = 'del_listener'

def make_observer (cls_lexeme, signals,
                   sub_doc = '', lst_doc = '',
                   defret = None, names = Naming):
    return make_observer_with (observer, cls_lexeme, signals,
                               lst_doc, sub_doc, defret, names)

def make_clever_observer (cls_lexeme, signals,
                          lst_doc = '', sub_doc = '',
                          defret = None, names = Naming):
    return make_observer_with (clever_observer, cls_lexeme, signals,
                               lst_doc, sub_doc, defret, names)
    
def make_observer_with (observer_func, cls_lexeme, signals,
                        sub_doc = '', lst_doc = '',
                        defret = None, names = Naming):
    sub_cls = type (cls_lexeme + names.SUBJECT_CLASS_POSTFIX,
                    (object,), {'__doc__': sub_doc})
    lst_cls = type (cls_lexeme + names.LISTENER_CLASS_POSTFIX,
                    (object,), {'__doc__': lst_doc})

    return observer_func (sub_cls, lst_cls, signals, defret, names)
    

def clever_observer (subject_cls, listener_cls, signals,
                     defret = None, names = Naming):
    setup_subject_clever_class (subject_cls, signals)
    setup_listener_clever_class (listener_cls, signals, defret)

    return subject_cls, listener_cls

def observer (subject_cls, listener_cls, signals,
              defret = None, names = Naming):
    setup_subject_class (subject_cls, signals, names)
    setup_listener_class (listener_cls, signals, defret, names)

    return subject_cls, listener_cls

def clever_listener (cls, signals, defret = None, names = Naming):
    def init (self):
        for sig in signals:
            setattr (self, names.SLOT_PREFIX + sig, CleverSlot (
                getattr (self, names.HANDLER_PREFIX + sig)))
    def disconnect (self):
        for sig in signals:
            getattr (self, names.SLOT_PREFIX + sig).disconnect ()

    listener (cls, signals, defret)
    setattr (cls, '__init__', init)
    setattr (cls, names.DISCONNECT_FUNCTION, disconnect)

    return cls

def clever_subject (cls, signals, names = Naming):
    def init (self):
        for sig in signals:
            setattr (self, names.SIGNAL_PREFIX + sig, Signal ())

    def add_listener (self, listener):
        for sig in signals:
            getattr (self, names.SIGNAL_PREFIX + sig).connect (
                getattr (listener, names.HANDLER_PREFIX + sig))

    def del_listener (self, listener):
        for sig in signals:
            getattr (self, names.SIGNAL_PREFIX + sig).disconnect (
                getattr (listener, names.SLOT_PREFIX + sig))
    
    setattr (cls, '__init__', init)
    setattr (cls, names.ADD_LISTENER_FUNCTION, add_listener)
    setattr (cls, names.ADD_LISTENER_FUNCTION, del_listener)

    return cls

def listener (cls, signals, defret = None, names = Naming):
    def empty_method (self, *args, **kw):
        return defret
    for sig in signals:
        setattr (cls, names.HANDLER_PREFIX + sig, empty_method)

    return cls

def subject (cls, signals, names = Naming):
    def init (self):
        for sig in signals:
            setattr (self, names.SIGNAL_PREFIX + sig, Signal ())

    def add_listener (self, listener):
        for sig in signals:
            getattr (self, names.SIGNAL_PREFIX + sig).connect (
                getattr (listener, names.HANDLER_PREFIX + sig))

    def del_listener (self, listener):
        for sig in signals:
            getattr (self, names.SIGNAL_PREFIX + sig).disconnect_func (
                getattr (listener, names.HANDLER_PREFIX + sig))
    
    setattr (cls, '__init__', init)
    setattr (cls, names.ADD_LISTENER_FUNCTION, add_listener)
    setattr (cls, names.DEL_LISTENER_FUNCTION, del_listener)

    return cls

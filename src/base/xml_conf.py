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

from util import flip_dict
from conf import NullBackend, ConfNode, ConfError
from log import *

from xml.sax import make_parser, SAXException
from xml.sax.handler import ContentHandler

XML_CONF_TYPES = { "int"     : int,
                   "string"  : str,
                   "float"   : float,
                   "default" : str }

XML_CONF_TYPES_INV = flip_dict (XML_CONF_TYPES)

class XmlConfError (ConfError):
    pass

class XmlConfBackend (NullBackend):

    def __init__ (self, fname,
                  update_on_change = False,
                  update_on_nudge  = False):
        self.save_on_change = update_on_change
        self.save_on_nudge  = update_on_nudge
        self.file_name = fname
        
    def _do_load (self, node, overwrite):
        setter = ConfNode.set_value if overwrite else ConfNode.default
        reader = XmlSaxConfParser (node, setter)

        parser = make_parser ()
        parser.setContentHandler (reader)

        try:
            fh = open (self.file_name, 'r')
        except IOError, e:
            raise XmlConfError ('Could not open config file. ' +
                                'If this is the first time you ' +
                                'run the application it might be created later.',
                                LOG_WARNING)
        
        parser.parse (fh)
        fh.close ()
        
    def _do_save (self, node):
        fh = open (self.file_name, 'w')
        writer = XmlConfWriter (fh)
        writer.write (node)
        fh.close ()

    def _handle_conf_change (self, node):
        if self.save_on_change:
            self._do_save (node)

    def _handle_conf_nudge (self, node):
        if self.save_on_nudge:
            self._do_save (node)

class XmlConfWriter:
    def __init__ (self, fh):
        self._fh = fh
        self._depth = 0
        
    def write (self, node):
        self._write_node (node, 'config')
        
    def _write_node (self, node, node_tag):
        indent = ' ' * self._depth * 2 
        self._fh.write (indent + '<' + node_tag)

        if node.get_name ():
            self._fh.write (' name="' + node.get_name() + '"')
        if node.value:
            self._fh.write (' type="' + XML_CONF_TYPES_INV [node.value.__class__] + '"')
            self._fh.write (' value="' + str (node.value) + '"')
                    
        childs = node.childs ()
        if len (childs) > 0:
            self._fh.write ('>\n')

            self._depth += 1
            for child in childs:
                self._write_node (child, 'node')
            self._depth -= 1
            
            self._fh.write (indent + '</' + node_tag + '>\n')
        else:
            self._fh.write ('/>\n')
        
class XmlSaxConfParser (ContentHandler):

    def __init__ (self, conf_node = None, setter = ConfNode.set_value):
        self._curr_node = conf_node if conf_node else ConfNode ()
        self._curr_type = None
        self._depth = 0
        self._setter = setter

    def conf_node (self):
        return self._curr_node
    
    def startElement (self, name, attrs):
        self.dispatch_element ('_start_element_', name, attrs)
        self._depth += 1
        
    def endElement (self, name):
        self.dispatch_element ('_end_element_', name, {})
        self._depth -= 1
        
    def characters (self, chars):
        pass
    
    def dispatch_element (self, prev, name, attrs):
        attr = prev + name
        if hasattr (self, attr):
            getattr (self, attr) (name, attrs)
        else:
            raise XmlConfError ('Unknown node: ' + name)

    def _start_element_config (self, name, attrs):
        if self._depth != 0:
            raise XmlConfError ('Unexpected \'config\' tag')
        self._curr_node.rename (attrs ['name'])
        self._fill_node (attrs)
        
    def _end_element_config (self, name, attrs):
        pass
    
    def _start_element_node (self, name, attrs):
        if self._depth < 1:
            raise XmlConfError ('Unexpected \'node\' tag')
        self._curr_node = self._curr_node.child (attrs ['name'])
        self._fill_node (attrs)
        
    def _end_element_node (self, name, attrs):
        self._curr_node = self._curr_node.parent ()

    def _fill_node (self, attrs):
        try:
            self._curr_type = XML_CONF_TYPES [attrs ['type']]
        except KeyError:
            self._curr_type = XML_CONF_TYPES ['default']

        try:
            self._setter (self._curr_node, self._curr_type (attrs ['value']))
        except KeyError:
            pass
        

#!/usr/bin/env python

import gi
gi.require_version('Gtk', '3.0')

# Events

def add_event(button):
  print("add_event")
  return False

def remove_event(button):
  print("remove_event")
  return False

def delete_event(widget, event, data=None):
  Gtk.main_quit()
  return False

from gi.repository import Gtk, Pango

builder = Gtk.Builder()
builder.add_from_file("connmonitor.glade")

window = builder.get_object("window1")
window.connect("delete_event", delete_event)

addB    = builder.get_object("addB")
addB.connect("clicked", add_event)

removeB = builder.get_object("removeB")
removeB.connect("clicked", remove_event)


window.show()

Gtk.main()


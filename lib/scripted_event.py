import pygame
import os

from pygame.locals import *

from locals import *

import data

from util import dir_from_str

from log import log_message

from variables import variables

class Scripted_event_element:
  def __init__(self, event_type, text="", orientation=RIGHT, animation=""):
    self.event_type = event_type
    self.finished = False
    self.text = text
    self.orientation = orientation
    self.animation = animation

class Scripted_event:
  def __init__(self, trigger_type, times = 1):
    self.trigger_type = trigger_type
    self.elements = []
    self.counter = -1
    self.last_dir = RIGHT
    self.repeated = 0
    self.times = times
  
  def add_element(self, text):
    values  = text.split(" ", 1)
    etype = values[0].strip()
    if etype == "dialogue":
      element = Scripted_event_element(etype, values[1].strip())
    elif etype == "player":
      values = values[1].split()
      if values[0] == "orientation":
        self.last_dir = dir_from_str(values[1])
        element = Scripted_event_element(etype, values[0], self.last_dir)
      if values[0] == "animation":
        element = Scripted_event_element(etype, values[0], self.last_dir, values[1])
    else:
      element = Scripted_event_element(etype)
    
    self.elements.append(element)
  
  def next_element(self):
    if self.repeated == self.times:
      #The event has repeated enough times
      return Scripted_event_element("end")

    #Returning one element
    self.counter += 1

    if self.counter < len(self.elements):
      return self.elements[self.counter]

    else:
      #Event finished
      self.repeated += 1
      self.counter = -1
      return Scripted_event_element("end")

"""
Game main module.

Contains the entry point used by the run_game.py script.
The actual gameplay code is in game.py.
"""

import os
import sys

from pygame.locals import *
import pygame

from .locals import *
from . import data
from . import game
from .util import Score, parse_config, write_config, write_log, apply_fullscreen_setting
from .variables import variables
from .log import error_message
from .mainmenu import Mainmenu
from .world import World
from .sound import play_sound


def main():
    # Parsing level from parameters and parsing main config:
    
    parse_config()
    variables["devmode"] = False
    
    level_name = None
    world_index = 0
    world = World(world_index)
    user_supplied_level = False
    
    if len(sys.argv) > 1:
        getlevel = False
        badarg = False
        for arg in sys.argv:
            if getlevel:
                level_name = arg
                user_supplied_level = True
                end_trigger = END_NEXT_LEVEL
                menu_choice = MENU_QUIT
                getlevel = False
            elif arg == "-l":
                getlevel = True
            elif arg == "-dev":
                variables["devmode"] = True
                variables["verbose"] = True
            elif arg == "-v":
                variables["verbose"] = True
            else:
                badarg = arg
        
        if badarg:
            error_message('Unrecognized command line parameter: %r' % badarg)
        if getlevel:
            error_message("Incorrect command line parameters")

    #Initializing pygame and screen

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    caption = "Which way is up?"
    if (variables["devmode"]):
        caption = caption + " - developer mode"
    pygame.display.set_caption(caption)

    apply_fullscreen_setting(screen)

    if (pygame.joystick.get_count() > 0):
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        joystick = None

    score = Score(0)

    done = False

    if not user_supplied_level:
        if (variables["unlocked" + WORLDS[0]] == 0):
            # Nothing unlocked, go straight to the game
            end_trigger = END_NEXT_LEVEL
            menu_choice = MENU_QUIT
            level_name = world.get_level()
        else:
            # Go to the menu first
            end_trigger = END_MENU
            menu_choice = 0

    bgscreen = None

    #Menu and level changing loop, actual game code is in game.py:

    while not done:
        if end_trigger == END_NEXT_LEVEL:
            if user_supplied_level:
                end_trigger = game.run(screen, level_name, world.level_index, score, joystick)
                if end_trigger == END_NEXT_LEVEL:
                    user_supplied_level = False
                    end_trigger = END_WIN
            else:
                end_trigger = game.run(screen, level_name, world.level_index, score, joystick)
                if end_trigger == END_NEXT_LEVEL:
                    if world.is_next_level():
                        level_name = world.get_level()
                    else:
                        end_trigger = END_WIN
                elif end_trigger == END_QUIT:
                    display_bg("quit", screen)
                    end_trigger = END_MENU
                    bgscreen = screen.copy()
        if end_trigger == END_LOSE:
            display_bg("lose", screen)
            end_trigger = END_MENU
            menu_choice = world.level_index - 1
            bgscreen = screen.copy()
        elif end_trigger == END_WIN:
            display_bg("victory", screen)
            end_trigger = END_MENU
            menu_choice = 0
            bgscreen = screen.copy()
        elif end_trigger == END_QUIT or end_trigger == END_HARD_QUIT:
            done = True
        elif end_trigger == END_MENU:
            prev_score = score.score
            prev_time = score.time
            prev_levels = score.levels
            score = Score(0)
            if prev_score != 0:
                menu = Mainmenu(screen, prev_score, world, bgscreen, prev_time, prev_levels)
            else:
                menu = Mainmenu(screen, None, world, bgscreen)
            menu_choice = menu.run(menu_choice)
            if menu_choice == MENU_QUIT:
                end_trigger = END_QUIT
            elif menu_choice == MENU_SOUND:
                variables["sound"] = not variables["sound"]
                end_trigger = END_MENU
            elif menu_choice == MENU_DIALOGUE:
                variables["dialogue"] = not variables["dialogue"]
                end_trigger = END_MENU
            elif menu_choice == MENU_FULLSCREEN:
                variables["fullscreen"] = not variables["fullscreen"]
                end_trigger = END_MENU
                apply_fullscreen_setting(screen)
            elif menu_choice == MENU_CHARACTER:
                cur_char = variables['character'] + 1
                if cur_char >= len(CHARACTERS):
                    cur_char = 0
                variables['character'] = cur_char
                end_trigger = END_MENU
            elif menu_choice == MENU_WORLD:
                world_index += 1
                if world_index >= len(WORLDS):
                    world_index = 0
                world = World(world_index)
                end_trigger = END_MENU
            else:
                level_name = world.get_level(menu_choice)
                end_trigger = END_NEXT_LEVEL

    write_config()
    write_log()


def display_bg(key, screen):
    bg_image = pygame.image.load(data.picpath("bg", key))
    rect = bg_image.get_rect()
    screen.blit(bg_image, rect)
    return

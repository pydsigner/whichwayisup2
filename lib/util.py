"""
This module contains generic utility and helper functions.
The comments give a basic idea of each function's purpose.
This module is mostly included in Skellington Plus.
"""

import json
import os
import codecs
import datetime

import pygame
from pygame.locals import *

from locals import *
import data
from sound import play_sound
from variables import variables
from log import error_message, log_message


class Score:
    def __init__(self, score, life = PLAYER_LIFE, time = 0, levels = 0):
        self.score = score
        self.life = life
        self.time = time
        self.levels = levels
        return


class Util:
    pygame.font.init()
    smallfont = pygame.font.Font(data.filepath(os.path.join('misc', 'Vera.ttf')), FONT_SIZE)
    cached_text_images = {}
    cached_images = {}
    cached_images['key_z'] = pygame.image.load(data.picpath('key', 'z'))
    cached_images['key_p'] = pygame.image.load(data.picpath('key', 'p'))
    cached_images['health_bar_fill'] = pygame.image.load(data.picpath('health_bar', 'fill'))
    cached_images['health_bar_empty'] = pygame.image.load(data.picpath('health_bar', 'empty'))
    fade_state = FADE_STATE_BLACK
    blackscreen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))


def get_config_path():
    """
    This function returns a path for saving config in the user's home directory.
    It's compatible with both UNIX-likes (environment variable HOME) and 
    Windows (environment variable APPDATA).
    Prints error messages if unsuccesful, and reverts to a 'saves' directory
    under the data directory instead.
    """
    path_name = ''
    try:
        path_name = os.path.join(os.environ['HOME'], '.' + GAME_NAME_SHORT)
    except KeyError:
        error_message('Couldn\'t find environment variable HOME, reverting to APPDATA. This is normal under Windows.')
        try:
            path_name = os.path.join(os.environ['APPDATA'], GAME_NAME_SHORT)
        except KeyError:
            error_message('Couldn\'t get environment variable for home directory, using data directory instead.')
            path_name = data.filepath('saves')
    if not os.path.exists(path_name):
        os.mkdir(path_name)
    return path_name


def parse_config():
    """
    This parses a config file stored in the location given by get_config_path().
    The parsed values are stored in the variables class of the variables module.
    """
    for world in WORLDS:
        variables['unlocked' + world] = 0
        variables['hiscore' + world] = 0
        variables['besttime' + world] = 0
    variables['sound'] = True
    variables['dialogue'] = True
    variables['verbose'] = False
    variables['fullscreen'] = False
    variables['character'] = 0
    
    file_path = os.path.join(get_config_path(), 'config.txt')
    try:
        conffile = codecs.open(file_path, 'r', 'utf_8')
        for line in conffile:
            line = line.strip()
            if line == '':
                continue
            
            values = line.split('\t')
            if values[0] == 'unlocked':
                variables.vdict['unlocked' + values[1]] = int(values[2])
            elif values[0] == 'hiscore':
                variables.vdict['hiscore' + values[1]] = int(values[2])
            elif values[0] == 'besttime':
                variables.vdict['besttime' + values[1]] = int(values[2])
            elif values[0] == 'sound':
                variables.vdict['sound'] = str_to_bool(values[1])
            elif values[0] == 'dialogue':
                variables.vdict['dialogue'] = str_to_bool(values[1])
            elif values[0] == 'fullscreen':
                variables.vdict['fullscreen'] = str_to_bool(values[1])
            elif values[0] == 'character':
                variables.vdict['character'] = int(values[1])
    
    except Exception:
        if write_config():
            log_message('Created configuration file to ' + file_path)



def write_config():
    """
    Writes the config stored in the variables class to the configuration file.
    Prints an error message if unsuccesful.
    """
    file_path = os.path.join(get_config_path(), 'config.txt')
    try:
        conffile = codecs.open(file_path, 'w', 'utf_8')
        for world in WORLDS:
            print >> conffile, 'unlocked\t%(world)s\t%(unlocked)s' % {'world': world, 'unlocked': variables.vdict['unlocked' + world]}
            print >> conffile, 'hiscore\t%(world)s\t%(hiscore)s' % {'world': world, 'hiscore': variables.vdict['hiscore' + world]}
            print >> conffile, 'besttime\t%(world)s\t%(besttime)s' % {'world': world, 'besttime': variables.vdict['besttime' + world]}
        print >> conffile, 'sound\t%s' % bool_to_str(variables.vdict['sound'])
        print >> conffile, 'dialogue\t%s' % bool_to_str(variables.vdict['dialogue'])
        print >> conffile, 'fullscreen\t%s' % bool_to_str(variables.vdict['fullscreen'])
        print >> conffile, 'character\t%s' % variables.vdict['character']
    except Exception:
        error_message('Could not write configuration file to ' + file_path)
        return False
    return True


#Writes the message log to disk.
def write_log():
    file_path = os.path.join(get_config_path(), 'log.txt')
    old_log = ''
    if os.path.exists(file_path):
        conffile = open(file_path)
        count = 0
        for line in conffile:
            old_log = old_log + line
            count += 1
            if count > MAX_OLD_LOG_LINES:
                break
    if variables.vdict.has_key('log'):
        try:
            conffile = codecs.open(file_path, 'w', 'utf_8')
            print >> conffile, 'Log updated ' + str(datetime.date.today())
            print >> conffile, variables.vdict['log']
            print >> conffile, ''
            print >> conffile, old_log
        except:
            error_message('Could not write log file to ' + file_path)
            return False
    return True


def str_to_bool(string):
    string = string.strip().lower()
    return (string == 'true' or string == '1' or string == 'on')


def bool_to_str(boolean):
    return 'on' if boolean else 'off'


def render_text(string, color=COLOR_GUI, bgcolor=COLOR_GUI_BG):
    """
    This function renders fancy-looking text and handles caching of text images.
    Returns a pygame surface containing the rendered text.
    The text is rendered with slight edges to make it look more readable on a
    colorful background.

    The constant colors can be found from locals.py.
    """
    if Util.cached_text_images.has_key(string + str(color) + str(bgcolor)):
        final_image = Util.cached_text_images[string + str(color) + str(bgcolor)]
    else:
        text_image_bg = Util.smallfont.render(string, True, bgcolor)
        text_image_fg = Util.smallfont.render(string, True, color)
        rect = text_image_bg.get_rect()
        final_image = pygame.Surface((rect.width + 2, rect.height + 2), SRCALPHA)

        final_image.fill((0,0,0,0))

        final_image.blit(text_image_bg, rect)
        final_image.blit(text_image_bg, (1,0))
        final_image.blit(text_image_bg, (2,0))

        final_image.blit(text_image_bg, (0,2))
        final_image.blit(text_image_bg, (1,2))
        final_image.blit(text_image_bg, (2,2))

        final_image.blit(text_image_fg, (1,1))
        Util.cached_text_images[string + str(color) + str(bgcolor)] = final_image
    return final_image


def render_text_dialogue(screen, string, phase, key='z'):
    """
    This function renders text partially.
    For fancy dialogue display.
    The phase value is the amount of characters shown.
    -1 phase means that the whole string is visible.
    """
    if phase == -1:
        phase = len(string)

    rendered_string = string[0:phase]
    string_image = render_text(rendered_string)
    string_rect = string_image.get_rect()
    string_rect.centerx = SCREEN_WIDTH / 2
    string_rect.centery = SCREEN_HEIGHT / 2

    if key == 'p':
        skip_image = Util.cached_images['key_p']
    else:
        skip_image = Util.cached_images['key_z']

    skip_rect = skip_image.get_rect()
    skip_rect.centerx = SCREEN_WIDTH / 2
    skip_rect.top = string_rect.bottom + 5

    bg_rect = pygame.Rect(string_rect.left - 10, string_rect.top - 5, string_rect.width + 20, string_rect.height + skip_rect.height + 15)
    bg_image = pygame.Surface((bg_rect.width, bg_rect.height))  
    bg_image.set_alpha(FADE_STATE_HALF)

    screen.blit(bg_image, bg_rect)
    screen.blit(string_image, string_rect)
    screen.blit(skip_image, skip_rect)

    if phase < len(string):
        phase += 1
        play_sound('click')
    else:
        return -1

    return phase


def cycle_clockwise(orientation):
    orientation += 1
    if orientation > 3:
        orientation = 0
    return orientation


def cycle_counter_clockwise(orientation):
    orientation -= 1
    if orientation < 0:
        orientation = 3
    return orientation


def get_direction(orientation):
    if orientation == RIGHT:
        return (1, 0)
    if orientation == LEFT:
        return (-1, 0)
    if orientation == UP:
        return (0, -1)
    if orientation == DOWN:
        return (0, 1)
    return (0, 0)


def dir_from_str(string):
    return {'LEFT': LEFT, 'RIGHT': RIGHT, 'UP': UP, 'DOWN': DOWN}[string]


def str_from_dir(direction):
    return {LEFT: 'LEFT', RIGHT: 'RIGHT', UP: 'UP', DOWN: 'DOWN'}[direction]


def fade_to_black(screen, fade_target):
    """
    This function fades the screen to black.
    Both fade-in and fade-out.
    Returns true if the fading has finished.
    fade_target should be an integer (0-255)
    * 255 = FADE_STATE_BLACK : The display is all black
    * 0 = FADE_STATE_NONE : The display is not faded at all
    """
    if Util.fade_state > fade_target:
        Util.fade_state += int(255 / (FPS * FADE_IN))
        if Util.fade_state < fade_target:
            Util.fade_state = fade_target
    if Util.fade_state < fade_target:
        Util.fade_state -= -int(255 / (FPS * FADE_OUT))
        if Util.fade_state > fade_target:
            Util.fade_state = fade_target
    if Util.fade_state > FADE_STATE_NONE:
        Util.blackscreen.set_alpha(Util.fade_state)
        screen.blit(Util.blackscreen, screen.get_rect())
    return (Util.fade_state == fade_target)


def apply_fullscreen_setting(screen):
    """
    Applies the fullscreen setting stored in variables to the screen.
    screen is a pygame standard surface.
    Contents of the screen should not be affected.
    """
    mode = 0
    if variables.vdict['fullscreen']:
        mode ^= FULLSCREEN
    tmp = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT)).convert()
    tmp.blit(screen,(0,0))
    screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT),mode)
    screen.blit(tmp,(0,0))
    pygame.display.flip()


def get_edges(r):
    d = {}
    d[LEFT] = pygame.Rect(r.topleft, (0, r.height))
    d[RIGHT] = pygame.Rect(r.topright, (0, r.height))
    d[UP] = pygame.Rect(r.topleft, (r.width, 0))
    d[DOWN] = pygame.Rect(r.bottomleft, (r.width, 0))
    return d


def all_collided(r, other_rects):
    for rect in other_rects:
        if not r.colliderect(rect):
            return False
    return True

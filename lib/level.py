import os
import codecs

import pytmx
import pygame
from pygame.locals import *

from .locals import *
from .data import levelpath, filepath
from .util import dir_from_str, all_collided, get_edges
from .log import error_message, log_message
from .tile import Tile
from .spikes import Spikes
from .item import Item
from .player import Player
from .spider import Spider
from .blob import Blob
from .scripted_event import Scripted_event
from .animation import Animation
from .trigger import Trigger
from .visibleobject import tile_coords_to_screen_coords


class Change:
    def __init__(self, tile_change, coords):
        self.tile_change = tile_change
        self.coords = coords


class UnknownTileException(Exception):
    pass


def get_tile_type(path):
    base = os.path.basename(path)
    for keyword in TILE_TYPE_MAP:
        if keyword in base:
            return TILE_TYPE_MAP[keyword]
    raise UnknownTileException(path)


class Level:
    def __init__(self, screen, character, level_name="w0-l0"):
        self.screen = screen
        self.image = None
        self.flipping = False
        self.flipcounter = 0
        self.set = "brown"  #The default tileset, can be changed through level configuration

        self.tiles = []
        self.objects = []

        self.scripted_events = []

        self.cached_ground_check = {}

        self.dust_color = COLOR_DUST["brown"]

        self.level_name = level_name

        self.orientation = 0

        conffile = codecs.open(levelpath(self.level_name), "r", "utf_8")

        tiley = 0
        values = []

        trigger = False
        current_event = None

        parse_tiles = False

        for line in conffile:

            if parse_tiles:
                if tiley < FULL_TILES_VER:
                    tilex = 0
                    while tilex < FULL_TILES_VER:
                        if (line[tilex] == "W") or (line[tilex] == "B") or (line[tilex] == "S"):
                            self.add_tile(line[tilex], (tilex, tiley))
                        tilex += 1
                    tiley += 1
                    continue
                else:
                    parse_tiles = False
                    continue

            elif line.strip() != "":
                    values = line.split()

                    #Parsing special commands

                    if trigger:
                        if values[0] == "end" and values[1] == "trigger":
                            trigger = False
                        else:
                            current_event.add_element(line)
                        continue

                    elif values[0] == "trigger":
                        trigger = True
                        current_event = Scripted_event(values[1], int(values[2]))
                        self.scripted_events.append(current_event)
                        continue

                    elif values[0] == "set":
                        # Original tileset declaration
                        self.set = values[1]
                        continue

                    elif values[0] == "tiles":
                        # Original tilemap header
                        if len(values) == 1:
                            parse_tiles = True
                            continue

                        # Parse a TMX
                        path = filepath(line.split(None, 1)[1].strip())
                        tmx = pytmx.pytmx.TiledMap(path)
                        for x, y, image in tmx.layers[0].tiles():
                            tile_type = get_tile_type(image[0])
                            self.add_tile(tile_type, (x, y))
                        self.set = tmx.tilesets[0].name
                        continue


                    #Parsing objects
                    x, y = tile_coords_to_screen_coords(values[1], values[2])

                    if values[0] == "player":
                        self.player = Player(self.screen, character, x, y)

                    elif values[0] == "spider":
                        self.objects.append(Spider( self.screen, x, y, dir_from_str(values[3]) ))

                    elif values[0] == "blob":
                        self.objects.append(Blob(self.screen, x, y, self.player))

                    elif values[0] == "lever":
                        trigger_type = TRIGGER_FLIP
                        if values[4] == "TRIGGER_FLIP":
                            trigger_type = TRIGGER_FLIP
                        self.objects.append( Item(self.screen, x, y, self.set, values[0], int(values[3]), trigger_type) )

                    else:
                        try:
                            self.objects.append(Item(self.screen, x, y, self.set, values[0]))
                        except:
                            error_message("Couldn't add object '" + values[0] + "'")

        self.dust_color = COLOR_DUST[self.set]

        self.bg_animations = {}
        self.bg_animations["default"] = Animation(self.set + "_background", "static")
        self.current_animation = "default"
        self.rect = (self.bg_animations[self.current_animation].update_and_get_image()).get_rect()
        self.rect.centerx = SCREEN_WIDTH / 2
        self.rect.centery = SCREEN_HEIGHT / 2

        self.reset_active_tiles()
        return

    def update(self):
        return_trigger = None
        if self.flipping:
            self.flipcounter += 1
            if self.flipcounter > FLIP_FRAMES:
                self.flipcounter = 0
                self.flipping = False
                self.reset_active_tiles()
                return_trigger = TRIGGER_FLIPPED
                self.image = None
            for t in self.tiles:
                t.update()
        return return_trigger

    def reset_active_tiles(self):
        self.active_tiles = []
        for t in self.tiles:
            if (t.x > 0 and t.y > 0):
                self.active_tiles.append(t)
        return

    def get_objects(self):
        return self.objects

    def get_player(self):
        return self.player

    def get_scripted_events(self):
        return self.scripted_events

    #Renders the background and the tiles
    def render(self):
        if self.flipping or self.image == None or self.edited:
            self.image = pygame.Surface((self.rect.width, self.rect.height))
            bg = self.bg_animations[self.current_animation].update_and_get_image()
            self.image.blit(bg, self.rect)
            for t in self.tiles:
                t.render(self.image)
            self.edited = False

        #Blits the cached background
        self.screen.blit(self.image, self.rect)
        return

    #Starts the flipping of the level
    def flip(self, flip_direction = CLOCKWISE):
        if self.flipping:
            return
        else:
            self.cached_ground_check = {}
            self.flipping = True
            if (flip_direction == CLOCKWISE):
                self.orientation += 1
            if (flip_direction == COUNTER_CLOCKWISE):
                self.orientation -= 1
            for t in self.tiles:
                t.flip(flip_direction)
            return

    #Triggers an object in the position specified
    def trigger(self, x, y):
        for o in self.objects:
            if o.rect.collidepoint(x, y):
                if o.itemclass == "lever":
                    trigg = o.activate()
                    if trigg != None:
                        return trigg
        return None


    #Gives an object from the level (also removes it from the level)
    def pick_up(self, x, y):
        for o in self.objects:
            if o.rect.collidepoint(x, y):
                if o.pickable:
                    self.objects.remove(o)
                    return o
        return None


    #Checks the point for solid ground
    def ground_check(self, x, y):
        if (x, y) in self.cached_ground_check:
            return self.cached_ground_check[(x, y)]
        else:
            if x > SCREEN_WIDTH or y > SCREEN_HEIGHT or x < 0 or y < 0:
                return True
            for t in self.active_tiles:
                if t.rect.collidepoint(x, y):
                    self.cached_ground_check[(x, y)] = True
                    return True
            self.cached_ground_check[(x, y)] = False
            return False

    #This functions tests (approximately) if a rect collides with another and from which direction.
    #It's one of the most performance-heavy functions in the game, and thus should be optimized.
    #indexing: right left bottom top
    def collide(self, rect, dy, dx):
        collision = {RIGHT: None, LEFT: None, DOWN: None, UP: None, DAMAGE: 0}
        rcopy = rect.copy()
        # Hack to avoid jitter
        rcopy.height += 1
        rcopy.width += 1

        for t in self.active_tiles:
            if not t.is_aligned():
                # Sometimes collisions were misdetected just after the level
                # was flipped, so this is an extra check to avoid that.
                # Should look into the order things are done when
                # flipping to fix the problem properly
                continue

            overlap = t.rect.clip(rcopy)
            if not overlap:
              continue

            tx, ty = t.tilex, t.tiley

            edges = get_edges(t.rect)
            right_edge = edges[RIGHT]
            left_edge = edges[LEFT]
            bottom_edge = edges[DOWN]
            top_edge = edges[UP]

            # Edges are of the tile, so we invert to get the orientation as
            # pertaining to the passed rect
            col_top = rcopy.colliderect(bottom_edge) and not self.find_tile(tx, ty + 1)
            col_bottom = rcopy.colliderect(top_edge) and not self.find_tile(tx, ty - 1)
            col_left = rcopy.colliderect(right_edge) and not self.find_tile(tx + 1, ty)
            col_right = rcopy.colliderect(left_edge) and not self.find_tile(tx - 1, ty)

            col_hside = col_top or col_bottom
            col_vside = col_left or col_right

            can_hcol = not col_hside or not dy or overlap.width < overlap.height
            if dx > 0 and col_right and can_hcol:
                collision[RIGHT] = t.rect.left
            elif dx < 0 and col_left and can_hcol:
                collision[LEFT] = t.rect.right

            can_vcol = not col_vside or not dx or overlap.width >= overlap.height
            if dy >= 0 and col_bottom and can_vcol:
                collision[DOWN] = t.rect.top
                if t.itemclass == "spikes":
                    collision[DAMAGE] = 5
                else:
                    collision[DAMAGE] = 0
            elif dy < 0 and col_top and can_vcol:
                collision[UP] = t.rect.bottom

        return collision


    def change(self, change):
        """
        Apply a change to the level data according to a Change class object.
        """
        if change == None:
            return

        log_message("Made change %s to coords %s, %s" % (
                     change.tile_change, change.coords[0], change.coords[1])
                    )

        if (change.tile_change == "remove"):
            self.remove_tile(change.coords)

        elif change.tile_change in "WBS":
            self.remove_tile(change.coords)
            change.coords = (change.coords[0] + FULL_TILES_HOR - TILES_HOR,
                             change.coords[1] + FULL_TILES_VER - TILES_VER)
            self.add_tile(change.tile_change, change.coords)
            self.reset_active_tiles()

    def remove_tile(self, coords):
        """
        Remove a tile from the level with coordinates relative to the corner of
        the area currently visible.
        """
        for t in self.active_tiles:
            if t.rect.collidepoint(coords[0] * TILE_DIM + TILE_DIM / 2,
                                   coords[1]*TILE_DIM + TILE_DIM / 2):
                self.active_tiles.remove(t)
                self.tiles.remove(t)
                self.edited = True


    def add_tile(self, tile_type, coords):
        """
        Add a tile to the level with absolute coordinates in the current
        rotation state.
        """
        new_tile = None
        if tile_type == "W":
            new_tile = Tile(self.screen, coords[0], coords[1], self.set)
        elif tile_type == "B":
            new_tile = Tile(self.screen, coords[0], coords[1], self.set, "bars")
        elif tile_type == "S":
            new_tile = Spikes(self.screen, coords[0], coords[1], self.set)
        if new_tile != None:
            self.tiles.append(new_tile)
        self.edited = True

    def find_tile(self, tilex, tiley):
        for t in self.tiles:
            if t.tilex == tilex and t.tiley == tiley:
                return t

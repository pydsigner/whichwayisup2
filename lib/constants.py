ACTION_BOX_X, ACTION_BOX_Y = 13, 13

PHYSICS_RESOLUTION = 100
PHYSICS_FPS = 120

VIEW_RESOLUTIONS = {
    100: {
        'tiles': 100,
        'scale': 1
    },
    40: {
        'tiles': 40,
        'scale': 1
    }
}

# Applies only to standard-FPS games
VIEW_FRAMERATES = (PHYSICS_FPS, PHYSICS_FPS // 2, PHYSICS_FPS // 3, 
                   PHYSICS_FPS // 4)

# In 120fps frames; adjusted for non-standard framerates
FLIP_FRAMES = 150
FLIP_DELAY = 75


FADE_IN = -0.7
FADE_NONE = 0
FADE_OUT = 0.7
FADE_STATE_BLACK = 255
FADE_STATE_HALF = 128
FADE_STATE_NONE = 0

import argparse
import pathlib

import desper
import corso.model as corso
import sdl2

import corsoab
from . import graphics
from . import desktop
from . import game
from .log import logger

# Detect whether we are on bonnet
BONNET_DETECTED = True
try:
    from . import bonnet
except Exception:
    BONNET_DETECTED = False
    pass

LAYOUT_START_X = 32
LAYOUT_START_Y = 0
LAYOUT_X_CELL_OFFSET = 1
LAYOUT_Y_CELL_OFFSET = 1


def base_game_world_transformer(handle: desper.WorldHandle,
                                world: desper.World):
    """Instantiate game world basics (common to all platforms)."""
    world.add_processor(desper.CoroutineProcessor())
    world.add_processor(graphics.RenderLoopProcessor())
    world.add_processor(graphics.TimeProcessor())

    world.create_entity(graphics.ScreenSurfaceHandler())

    marble_surface = desper.resource_map['sprites/marble1']
    marble_width = marble_surface.contents.w
    marble_height = marble_surface.contents.h

    starting_state = corso.Corso()
    grid = [[0 for _ in range(starting_state.width)]
            for _ in range(starting_state.height)]
    for row in range(starting_state.height):
        for column in range(starting_state.width):
            grid[row][column] = world.create_entity(
                desper.Transform2D((LAYOUT_START_X + row
                                    * (marble_width + LAYOUT_X_CELL_OFFSET),
                                    LAYOUT_START_Y + column
                                    * (marble_height + LAYOUT_Y_CELL_OFFSET))))

    # Add visual cursors
    hor_cursor_surface = desper.resource_map['sprites/hor_cursor']
    hor_cursor_x_offset = (marble_width - hor_cursor_surface.contents.w) // 2
    # Top
    world.create_entity(hor_cursor_surface,
                        desper.Transform2D(),
                        game.CursorHandler(grid, (hor_cursor_x_offset,
                                                  -LAYOUT_Y_CELL_OFFSET)))
    # Bottom
    world.create_entity(hor_cursor_surface,
                        desper.Transform2D(),
                        game.CursorHandler(grid, (hor_cursor_x_offset,
                                                  LAYOUT_Y_CELL_OFFSET
                                                  + marble_height)))

    # Init game loop
    player1 = game.UserPlayer()
    player2 = game.UserPlayer()
    world.create_entity(player1)
    world.create_entity(player2)

    world.create_entity(game.GameHandler(grid, starting_state,
                                         (player1, player2)))


class Args:
    """Custom argument namespace for corso bonnet CLI."""
    desktop: bool = False


if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('-d', action='store_true', dest='desktop')

    args = parser.parse_args(namespace=Args())

    # Actual initialization
    sdl2.SDL_Init(0)

    # In the end, we are on bonnet only if it is actually detected
    on_bonnet = BONNET_DETECTED and not args.desktop
    # Warn the user of unexpected situations
    if not args.desktop and not BONNET_DETECTED:
        logger.warning('No bonnet detected, falling back to desktop mode. Use '
                       'option "-d" to hide this warning.')
    if args.desktop and BONNET_DETECTED:
        logger.warning('Desktop mode was forced, but a bonnet is detected. '
                       'Is this what you wanted? If you intend to run '
                       'on bonnet, remove option "-d".')

    if not on_bonnet:       # Only create a window on desktop
        window = sdl2.SDL_CreateWindow(b'Corso on adafruit bonnet',
                                       sdl2.SDL_WINDOWPOS_UNDEFINED,
                                       sdl2.SDL_WINDOWPOS_UNDEFINED,
                                       corsoab.BONNET_WIDTH,
                                       corsoab.BONNET_HEIGHT,
                                       0)
        corsoab.window = window

    directory_populator = desper.DirectoryResourcePopulator(
        pathlib.Path(__file__).absolute().parents[1] / 'resources',
        trim_extensions=True)

    directory_populator.add_rule('sprites', graphics.SurfaceHandle)
    directory_populator(desper.resource_map)

    desper.resource_map['worlds/game'] = desper.WorldHandle()
    desper.resource_map.get('worlds/game').transform_functions.append(
        base_game_world_transformer)

    # Platform specific world transformer
    platform_specific_transformer = desktop.game_world_transformer
    if on_bonnet:
        platform_specific_transformer = bonnet.game_world_transformer

    desper.resource_map.get('worlds/game').transform_functions.append(
            platform_specific_transformer)

    desper.default_loop.switch(desper.resource_map.get('worlds/game'))
    try:
        desper.default_loop.loop()
    except desper.Quit:
        pass

    if not on_bonnet:       # Window exists on desktop only
        sdl2.SDL_DestroyWindow(window)

    sdl2.SDL_Quit()

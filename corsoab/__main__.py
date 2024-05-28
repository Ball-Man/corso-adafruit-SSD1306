import pathlib

import desper
import sdl2

import corsoab
from . import graphics


def base_game_world_transformer(handle: desper.WorldHandle,
                                world: desper.World):
    """Instantiate game world basics (common to all platforms)."""
    world.add_processor(graphics.RenderLoopProcessor())

    world.create_entity(graphics.ScreenSurfaceHandler())

    world.create_entity(desper.Transform2D((0, 0)),
                        desper.resource_map['sprites/test_sprite'])


def desktop_game_world_transformer(handle: desper.WorldHandle,
                                   world: desper.World):
    """Instantiate game world (desktop specific)."""
    world.add_processor(graphics.RenderLoopProcessor())

    world.create_entity(graphics.RenderHandler())

    world.create_entity(
        graphics.ScreenSurface(),
        sdl2.SDL_GetWindowSurface(corsoab.window))


if __name__ == '__main__':
    sdl2.SDL_Init(0)

    window = sdl2.SDL_CreateWindow(b'Corso on adafruit bonnet',
                                   sdl2.SDL_WINDOWPOS_UNDEFINED,
                                   sdl2.SDL_WINDOWPOS_UNDEFINED,
                                   corsoab.BONNET_WIDTH, corsoab.BONNET_HEIGHT,
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
    desper.resource_map.get('worlds/game').transform_functions.append(
        desktop_game_world_transformer)

    desper.default_loop.switch(desper.resource_map.get('worlds/game'))
    try:
        desper.default_loop.loop()
    except desper.Quit:
        pass

    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

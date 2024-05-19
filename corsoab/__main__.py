import pathlib

import desper
import sdl2

import corsoab
from . import graphics


def game_world_transformer(handle: desper.WorldHandle, world: desper.World):
    """Instantiate game world."""
    print('game transformer')


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
        game_world_transformer)

    desper.default_loop.switch(desper.resource_map.get('worlds/game'))
    desper.default_loop.loop()

    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

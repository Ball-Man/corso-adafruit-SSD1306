import pathlib

import desper
import sdl2

from . import graphics


if __name__ == '__main__':
    sdl2.SDL_Init(0)

    directory_populator = desper.DirectoryResourcePopulator(
        pathlib.Path(__file__).absolute().parents[1] / 'resources',
        trim_extensions=True)

    directory_populator.add_rule('sprites', graphics.SurfaceHandle)
    directory_populator(desper.resource_map)

    print(desper.resource_map['sprites/test_sprite'])

    sdl2.SDL_Quit()

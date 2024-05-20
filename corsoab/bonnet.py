import ctypes

import desper
import busio
import board
import adafruit_ssd1306
import sdl2

import corsoab
from . import graphics

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
display = adafruit_ssd1306.SSD1306_I2C(corsoab.BONNET_WIDTH,
                                       corsoab.BONNET_HEIGHT, i2c)


def fill_display(display, surface):
    pixels = ctypes.cast(surface.contents.pixels,
                         ctypes.POINTER(ctypes.c_uint8))
    for y in range(corsoab.BONNET_HEIGHT):
        for x in range(corsoab.BONNET_WIDTH):
            display.pixel(x, y, pixels[128 * y + x] & 1)


@desper.event_handler('render')
class RenderHandler(desper.Controller):
    """Actually render screen to bonnet, on ``render`` event."""

    def render(self):
        screen_surface_entity, _ = self.world.get(graphics.ScreenSurface)[0]
        screen_surface = self.world.get_component(screen_surface_entity,
                                                  graphics.LP_SDL_Surface)

        fill_display(display, screen_surface)
        display.show()


def game_world_transformer(handle: desper.WorldHandle, world: desper.World):
    """Instantiate game world."""
    world.add_processor(graphics.RenderLoopProcessor())

    world.create_entity(graphics.ScreenSurfaceHandler(),
                        RenderHandler())

    world.create_entity(
        graphics.ScreenSurface(),
        sdl2.SDL_CreateRGBSurfaceWithFormat(0, corsoab.BONNET_WIDTH,
                                            corsoab.BONNET_HEIGHT, 1,
                                            sdl2.SDL_PIXELFORMAT_RGB332))

    world.create_entity(desper.Transform2D((0, 0)),
                        desper.resource_map['sprites/test_sprite'])

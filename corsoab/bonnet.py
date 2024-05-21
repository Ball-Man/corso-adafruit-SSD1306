import ctypes
import enum

import desper
import busio
import board
import adafruit_ssd1306
import sdl2
from digitalio import DigitalInOut, Direction, Pull

import corsoab
from . import graphics

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
display = adafruit_ssd1306.SSD1306_I2C(corsoab.BONNET_WIDTH,
                                       corsoab.BONNET_HEIGHT, i2c)

_BUTTON_A_DIGITAL = DigitalInOut(board.D5)
_BUTTON_A_DIGITAL.direction = Direction.INPUT
_BUTTON_A_DIGITAL.pull = Pull.UP

_BUTTON_B_DIGITAL = DigitalInOut(board.D6)
_BUTTON_B_DIGITAL.direction = Direction.INPUT
_BUTTON_B_DIGITAL.pull = Pull.UP

_BUTTON_L_DIGITAL = DigitalInOut(board.D27)
_BUTTON_L_DIGITAL.direction = Direction.INPUT
_BUTTON_L_DIGITAL.pull = Pull.UP

_BUTTON_R_DIGITAL = DigitalInOut(board.D23)
_BUTTON_R_DIGITAL.direction = Direction.INPUT
_BUTTON_R_DIGITAL.pull = Pull.UP

_BUTTON_U_DIGITAL = DigitalInOut(board.D17)
_BUTTON_U_DIGITAL.direction = Direction.INPUT
_BUTTON_U_DIGITAL.pull = Pull.UP

_BUTTON_D_DIGITAL = DigitalInOut(board.D22)
_BUTTON_D_DIGITAL.direction = Direction.INPUT
_BUTTON_D_DIGITAL.pull = Pull.UP

_BUTTON_C_DIGITAL = DigitalInOut(board.D4)
_BUTTON_C_DIGITAL.direction = Direction.INPUT
_BUTTON_C_DIGITAL.pull = Pull.UP


class Button(enum.Enum):
    """Bonnet buttons enumeration."""
    A = enum.auto()
    B = enum.auto()
    L = enum.auto()
    R = enum.auto()
    U = enum.auto()
    D = enum.auto()
    C = enum.auto()


_BUTTONS = {
    Button.A: _BUTTON_A_DIGITAL,
    Button.B: _BUTTON_B_DIGITAL,
    Button.L: _BUTTON_L_DIGITAL,
    Button.R: _BUTTON_R_DIGITAL,
    Button.U: _BUTTON_U_DIGITAL,
    Button.D: _BUTTON_D_DIGITAL,
    Button.C: _BUTTON_C_DIGITAL,
}


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
    world.add_processor(InputProcessor())

    world.create_entity(graphics.ScreenSurfaceHandler(),
                        RenderHandler())

    world.create_entity(
        graphics.ScreenSurface(),
        sdl2.SDL_CreateRGBSurfaceWithFormat(0, corsoab.BONNET_WIDTH,
                                            corsoab.BONNET_HEIGHT, 1,
                                            sdl2.SDL_PIXELFORMAT_RGB332))

    world.create_entity(desper.Transform2D((0, 0)),
                        desper.resource_map['sprites/test_sprite'])

    world.create_entity(QuitButtonHandler(Button.B))


@desper.event_handler('on_bonnet_button_press')
class QuitButtonHandler:
    """Quit if the given button is pressed."""

    def __init__(self, button):
        self.button = button

    def on_bonnet_button_press(self, button):
        """Handle event: quit if the designated button is pressed."""
        if button == self.button:
            display.poweroff()
            desper.quit_loop()


class InputProcessor(desper.Processor):
    """Handle input events."""
    _button_states = {}

    def process(self, dt):
        for button, digital in _BUTTONS.items():
            # Detect down-up edge
            button_value = not digital.value
            if not self._button_states.get(button) and button_value:
                self.world.dispatch('on_bonnet_button_press', button)

            self._button_states[button] = button_value

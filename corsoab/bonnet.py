import ctypes
import enum

import desper
import busio
import board
import adafruit_ssd1306
import sdl2
from digitalio import DigitalInOut, Direction, Pull

from . import graphics

# Create the I2C interface.
i2c = busio.I2C(board.SCL, board.SDA)
# Create the SSD1306 OLED class.
display = adafruit_ssd1306.SSD1306_I2C(graphics.BONNET_WIDTH,
                                       graphics.BONNET_HEIGHT, i2c)

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


_BONNET_TO_SDL_MAP = {
    Button.A: sdl2.SDL_SCANCODE_RETURN,
    Button.B: sdl2.SDL_SCANCODE_ESCAPE,
    Button.L: sdl2.SDL_SCANCODE_LEFT,
    Button.R: sdl2.SDL_SCANCODE_RIGHT,
    Button.U: sdl2.SDL_SCANCODE_UP,
    Button.D: sdl2.SDL_SCANCODE_DOWN,
    Button.C: sdl2.SDL_SCANCODE_DELETE,
}


def fill_display(display, surface):
    pixels = ctypes.cast(surface.contents.pixels,
                         ctypes.POINTER(ctypes.c_uint8))
    for y in range(graphics.BONNET_HEIGHT):
        for x in range(graphics.BONNET_WIDTH):
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


@desper.event_handler('on_dirty_render')
class DirtyRenderLoopProcessor(desper.Processor):
    """Dispatch ``update_screen_surface``, ``render`` events, if needed.

    This implementation only updates and flips the screen if during the
    frame a change is notified through the ``on_dirty_render`` event.
    Since the game is extremely static, with nothing changes for entire
    seconds, this is a lot of computation saved on the bonnet.
    Not flipping the screen at all may be problematic on desktop
    systems, let's keep it on the bonnet for the moment.

    Could be potentially improved with more fine-grained dirty
    rectangles.
    """
    _dirty = False

    def on_dirty_render(self):
        """Store a dirty "bit" for this frame."""
        self._dirty = True

    def process(self, dt):
        if not self._dirty:
            return

        self.world.dispatch('update_screen_surface')
        self.world.dispatch('render')

        self._dirty = False


def game_world_transformer(handle: desper.WorldHandle, world: desper.World):
    """Instantiate game world (bonnet specific)."""
    world.add_processor(InputProcessor())
    world.add_processor(DirtyRenderLoopProcessor())
    world.create_entity(BonnetToSDLKeys())

    world.create_entity(RenderHandler())

    world.create_entity(QuitButtonHandler(Button.C))

    # Notify a change to render during the game's first frame
    world.dispatch('on_dirty_render')


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


@desper.event_handler('on_bonnet_button_press')
class BonnetToSDLKeys(desper.Controller):
    """Map all bonnet button events to SDL keys."""

    def on_bonnet_button_press(self, button):
        """Dispatch the corresponding SDL key down event."""
        self.world.dispatch('on_key_down', _BONNET_TO_SDL_MAP[button])

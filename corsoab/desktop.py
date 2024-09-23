"""Desktop specific implementations."""
import ctypes

import desper
import sdl2

import corsoab
from . import graphics
from . import desktop


class InputProcessor(desper.Processor):
    """Handle input events."""
    _button_states = {}

    def process(self, dt):
        event = sdl2.SDL_Event()

        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_KEYDOWN and not event.key.repeat:
                self.world.dispatch('on_key_down', event.key.keysym.scancode)
            elif event.type == sdl2.SDL_QUIT:
                desper.quit_loop()


@desper.event_handler('on_key_down')
class KeyLogger:
    """Log key downs for debug purposes."""

    def on_key_down(self, key):
        """Handle key down: log."""
        print('key down:', key)


@desper.event_handler('render')
class RenderHandler(desper.Controller):
    """Actually render screen on ``render`` event."""

    def render(self):
        # Retrieve necessary surfaces (window, game screen)
        screen_surface_entity, _ = self.world.get(graphics.ScreenSurface)[0]
        screen_surface = self.world.get_component(screen_surface_entity,
                                                  graphics.LP_SDL_Surface)
        window_surface = sdl2.SDL_GetWindowSurface(corsoab.window)

        # Update window surface
        sdl2.SDL_BlitScaled(screen_surface, None, window_surface, None)
        sdl2.SDL_UpdateWindowSurface(corsoab.window)


def game_world_transformer(handle: desper.WorldHandle,
                           world: desper.World):
    """Instantiate game world (desktop specific)."""
    world.add_processor(graphics.RenderLoopProcessor())
    world.add_processor(desktop.InputProcessor())

    world.create_entity(RenderHandler())

    # world.create_entity(desktop.KeyLogger())

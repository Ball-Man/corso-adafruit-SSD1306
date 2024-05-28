"""Desktop specific implementations."""
import ctypes

import desper
import sdl2


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

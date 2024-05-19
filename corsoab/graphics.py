"""Graphics rendering powered by SDL."""
import ctypes

import desper
import sdl2

LP_SDL_Surface = ctypes.POINTER(sdl2.SDL_Surface)


class SurfaceHandle(desper.Handle):
    """Handle for SDL surfaces."""

    def __init__(self, filename):
        self.filename = filename

    def load(self) -> LP_SDL_Surface:
        return sdl2.SDL_LoadBMP(self.filename.encode())

    def clear(self):
        if self._cached:
            sdl2.SDL_FreeSurface(self._cache)
        super().clear()

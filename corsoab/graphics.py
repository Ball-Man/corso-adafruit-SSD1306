"""Graphics rendering powered by SDL."""
import ctypes

import desper
import sdl2

from . import BONNET_WIDTH, BONNET_HEIGHT

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


class ScreenSurface:
    """ID component: identify the screen surface."""


@desper.event_handler('update_screen_surface')
class ScreenSurfaceHandler(desper.Controller):
    """Render world on the screen surface on ``update_screen_surface`` event.

    This renders all everything through CPU/RAM on a surface
    identified by the :class:`ScreenSurface` component. The surface is
    not directly rendered to the screen. This is done to provide
    compatibility with the adafruit bonnet rendering implementation.
    """

    def update_screen_surface(self):
        screen_surface_entity, _ = self.world.get(ScreenSurface)[0]
        screen_surface = self.world.get_component(screen_surface_entity,
                                                  LP_SDL_Surface)
        sdl2.SDL_FillRect(screen_surface, sdl2.SDL_Rect(0, 0, BONNET_WIDTH,
                                                        BONNET_HEIGHT), 0)

        for entity, surface in self.world.get(LP_SDL_Surface):
            if entity == screen_surface_entity:
                continue

            transform: desper.Transform2D = self.world.get_component(
                entity, desper.Transform2D)

            sdl2.SDL_BlitSurface(
                surface, None,
                screen_surface,
                sdl2.SDL_Rect(*transform.position, surface.contents.w,
                              surface.contents.h))


class RenderLoopProcessor(desper.Processor):
    """Dispatch ``update_screen_surface`` and ``render`` events."""

    def process(self, dt):
        self.world.dispatch('update_screen_surface')
        self.world.dispatch('render')

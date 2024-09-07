import abc
from collections.abc import Collection
from itertools import cycle

import desper
import corso.model as corso
import sdl2


class GUIPlayer(abc.ABC):
    """Abstract class for players suitable for :class:`GameHandler`."""

    def start_selection(self, state: corso.Corso):
        pass


@desper.event_handler('on_bonnet_button_press', 'on_key_down')
class UserPlayer(desper.Controller, GUIPlayer):
    """Corso GUI player for human users."""
    cursor_x = 0
    cursor_y = 0
    _current_state = None
    _block_frame = False

    def start_selection(self, state: corso.Corso):
        """Enable player input."""
        self._current_state = state

        # Block inputs for one frame to prevent funky event overlaps
        # between multiple UserPlayers.
        self.block_next_frame()

    @desper.coroutine
    def _unblock_next_frame(self):
        """Coroutine: wait one frame and unblock user input."""
        yield
        self._block_frame = False

    def block_next_frame(self):
        """Block user input, unblock next frame."""
        self._block_frame = True
        self._unblock_next_frame()

    def on_bonnet_button_press(self, button):
        """TODO"""
        pass

    def on_key_down(self, key):
        """Handle key press, move cursor, make moves."""
        if self._current_state is None or self._block_frame:
            return

        horizontal = ((key == sdl2.SDL_SCANCODE_RIGHT)
                      - (key == sdl2.SDL_SCANCODE_LEFT))
        vertical = ((key == sdl2.SDL_SCANCODE_DOWN)
                    - (key == sdl2.SDL_SCANCODE_UP))

        # Update cursor and make it circular
        self.cursor_x = ((self.cursor_x + horizontal)
                         % self._current_state.width)
        self.cursor_y = (self.cursor_y + vertical) % self._current_state.height

        # Make a move
        if key == sdl2.SDL_SCANCODE_RETURN:
            self.world.dispatch('on_player_move',
                                corso.Action(self._current_state.player_index,
                                             self.cursor_x, self.cursor_y))
            self._current_state = None


@desper.event_handler('on_player_move')
class GameHandler(desper.Controller):
    """Handle game loop."""

    def __init__(self, grid, starting_state: corso.Corso,
                 players: Collection[GUIPlayer]):
        self.grid = grid
        self.state: corso.Corso = starting_state
        self.cursor_x: int = 0
        self.cursor_y: int = 0

        self._resource_map = {
            (1, False): desper.resource_map['sprites/dye1'],
            (2, False): desper.resource_map['sprites/dye2'],
            (1, True): desper.resource_map['sprites/marble1'],
            (2, True): desper.resource_map['sprites/marble2']
        }

        self.players = cycle(players)
        self._current_player_entity = None

    def next_player(self):
        """Start action selection of the next player.."""
        next(self.players).start_selection(self.state)

    def on_add(self, *args):
        """Init game loop."""
        super().on_add(*args)

        self.next_player()

    def on_player_move(self, action: corso.Action):
        """Apply player move to the game state."""
        # Step on current state
        self.state = self.state.step(action)

        # Replace images on grid based on new state
        for y, row in enumerate(self.state.board):
            for x, cell in enumerate(row):
                if cell.player_index == 0:
                    continue

                transform = self.world.get_component(self.grid[y][x],
                                                     desper.Transform2D)
                self.world.delete_entity(self.grid[y][x])
                self.grid[y][x] = self.world.create_entity(
                    transform, self._resource_map[cell])

        self.next_player()

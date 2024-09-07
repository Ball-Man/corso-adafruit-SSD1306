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

        # Update visual cursor to this player's position
        self.world.dispatch('on_cursor_update', self.cursor_x, self.cursor_y)

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

        # Update visual cursor as well
        self.world.dispatch('on_cursor_update', self.cursor_x, self.cursor_y)

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

        # Check for game termination
        terminal_status, winner = self.state.terminal
        if terminal_status:
            self.world.dispatch('on_game_over', winner)
            return

        self.next_player()


@desper.event_handler('on_cursor_update')
class CursorHandler(desper.Controller):
    """Event handler for the visual cursor.

    Reacts to the user cursor positional updates and updates
    the visual coordinates accordingly. One entity of this kind can
    only handle the position of one SDL surface. Having multiple of
    them is possible.
    """
    transform = desper.ComponentReference(desper.Transform2D)

    def __init__(self, grid, pixel_offset: tuple[int, int]):
        self.grid = grid
        self.pixel_offset = pixel_offset

    def on_cursor_update(self, cursor_x: int, cursor_y: int):
        """Set transform position based on the received coordinates."""
        selected_position = self.world.get_component(
            self.grid[cursor_x][cursor_y], desper.Transform2D).position

        self.transform.position = selected_position + self.pixel_offset

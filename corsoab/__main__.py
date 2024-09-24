import argparse
from dataclasses import dataclass, field

from corso.cli import parse_player as corso_parse_player, CLIPlayer

from .game import GUIPlayer, LegacyPlayer, UserPlayer
from .log import logger
from . import start_game

# Detect whether we are on bonnet
BONNET_DETECTED = True
try:
    from . import bonnet            # NOQA
except Exception:
    BONNET_DETECTED = False
    pass


@dataclass
class Args:
    """Custom argument namespace for corso bonnet CLI."""
    desktop: bool = False
    scale: int = 3
    players: list[GUIPlayer] = field(default_factory=lambda: [])


def parse_player(player_name: str) -> GUIPlayer:
    """Obtain a player instance from its CLI name.

    Under the hood, this uses corso's CLI name parser.
    """
    legacy_player = corso_parse_player(player_name)

    # Adapt CLI user player to our specialized user player
    if type(legacy_player) is CLIPlayer:
        return UserPlayer()

    # Any other legacy player is wrapped in a LegacyPlayer and returned
    return LegacyPlayer(legacy_player)


if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('-d', action='store_true', dest='desktop')
    parser.add_argument('-s', action='store', dest='scale', type=int)
    parser.add_argument('-p', '--player', type=parse_player,
                        nargs='*', action='extend', metavar='PLAYER_TYPE',
                        dest='players')

    args = parser.parse_args(namespace=Args())

    # In the end, we are on bonnet only if it is actually detected
    on_bonnet = BONNET_DETECTED and not args.desktop
    # Warn the user of unexpected situations
    if not args.desktop and not BONNET_DETECTED:
        logger.warning('No bonnet detected, falling back to desktop mode. Use '
                       'option "-d" to hide this warning.')
    if args.desktop and BONNET_DETECTED:
        logger.warning('Desktop mode was forced, but a bonnet is detected. '
                       'Is this what you wanted? If you intend to run '
                       'on bonnet, remove option "-d".')

    start_game(*args.players, on_bonnet=on_bonnet, window_scale=args.scale)

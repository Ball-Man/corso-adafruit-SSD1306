import argparse

from .log import logger
from . import start_game

# Detect whether we are on bonnet
BONNET_DETECTED = True
try:
    from . import bonnet            # NOQA
except Exception:
    BONNET_DETECTED = False
    pass


class Args:
    """Custom argument namespace for corso bonnet CLI."""
    desktop: bool = False


if __name__ == '__main__':
    # Arguments
    parser = argparse.ArgumentParser(__doc__)

    parser.add_argument('-d', action='store_true', dest='desktop')

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

    start_game(on_bonnet)

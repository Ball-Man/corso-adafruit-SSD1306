"""Setup a global logger for the game."""
import logging


# Retrieve logger
logger = logging.getLogger('corsoab')
logger.setLevel(logging.DEBUG)

# Set main handler (console output)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s '
                                '- %(message)s')
handler.setFormatter(formatter)
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

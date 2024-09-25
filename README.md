# Corso for Adafruit OLED bonnet
This project provides a simple GUI frontend for the [game of Corso](https://github.com/Ball-Man/corso), a perfect information board game.

The game is designed to work on a Raspberry Pi equipped with an [Adafruit 128x64 OLED Bonnet](https://www.adafruit.com/product/3531). Nonetheless, playing the game on any regular desktop computer is possible.

## Manual installation
Due to the current structure of the project, it is not possible to directly install the game through pip. The codebase will have to be manually cloned via git. This may very easily change in the future.

### Desktop
Here is a simple script that clones the repo and installs the dependencies on a local virtual environment.

On Unix:
```bash
git clone https://github.com/Ball-Man/corso-adafruit-SSD1306 corsoab
cd corsoab
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r include_sdl_requirements.txt
```

On Windows (cmd):
```bash
git clone https://github.com/Ball-Man/corso-adafruit-SSD1306 corsoab
cd corsoab
python -m venv venv
venv\scripts\activate
pip install -r requirements.txt -r include_sdl_requirements.txt
```

### Raspberry + bonnet
Assuming the bonnet was correctly configured according to the manufacturer, the extra requirements to handle the bonnet can be installed as:
```bash
pip install -r bonnet_requirements.txt
```

## Playing the game
Once the installation is complete, the game can be played on desktop with the command:
```bash
python -m corsoab -d
```

And on Raspberry Pi + bonnet with the command:
```bash
python -m corsoab
```

These will initiate a human vs human game.

### Game controls
On desktop:
* ``Directional Arrows`` to move the cursor.
* ``Return`` to make a move.

On Raspberry Pi + bonnet:
* ``Left Stick`` to move the cursor.
* ``Button #5`` to make a move.

### Custom games
The command line interface provides a few extra parameters for game customization. In particular, a set of simple AIs that are included
in the original ``corso`` package can be used.

To play against a decent MiniMax AI (depth 3):
```bash
# Here the AI goes second
python -m corsoab -p user mm

# Here the AI goes first
python -m corsoab -p mm user
```

See `python -m corsoab -h` for more options and built-in AI players.

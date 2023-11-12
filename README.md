# GeneticSnake ![Python][python] [![License](https://img.shields.io/badge/License-MIT-red.svg?longCache=true&style=flat-square)](LICENSE)

> A Genetic Algorithm used to teach a Neural Network how to play snake.

## Requirements

The game requires [**pygame**](https://github.com/pygame/pygame) and [**matplotlib**](https://matplotlib.org/)

To install them: `pip install -r requirements.txt`.

## Usage

This project consists of the following modules:

### nn.py

This module contains the neural network code.

### snake.py

This module contains the basic snake game code.

It can be used to run a *debug* session:

**Usage**: `python snake.py [filename]`

The optional argument `[filename]` can be used to test a previously trained neural network.

### game.py

This module contains the GUI and the overall game handling code, refactored from my previous project [PythonVsViper](https://github.com/filipposerafini/PythonVsViper).

**Usage**: `python game.py`

There exists 3 game modes:

1. **Single Player**: Play this mode to reach an highscore. Steer the snake with ` ↑ `,` ← `,` ↓ `,` → ` keys.
2. **Two Players**: Play this mode to challenge your friends. Steer the blue snake with ` ↑ `,` ← `,` ↓ `,` → ` keys, and steer the green snake with ` W `,` A `,` S `,` D ` keys.
3. **Player VS AI**: Play this mode to challenge the AI. The AI uses the the neural network saved in `snake_ia.json` JSON file.

### genetic.py

This module contains the genetic algorithm code, and it is used to train the neural network to play the game.

**Usage**: `python genetic.py [filename]`

The trained neural networks are saved in `save\snake_nn_yyyymmdd-HH:MM.json` JSON file.

The optional argument `[filename]` can be used to continue the training of a previusly trained neural network.

## License

Distributed under the [MIT](LICENSE) license.

Copyright &copy; 2023, [Filippo Serafini](https://filipposerafini.github.io/).

[python]: https://img.shields.io/badge/python-3-blue.svg?longCache=true&style=flat-square

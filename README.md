# Maths Games

A collection of fun and educational math games for kids, designed for the Sugar learning platform.

## Included Games

- **Four Color Map**: Color a map so that no two adjacent regions have the same color.
- **Broken Calculator**: Reach the target number using a calculator with some broken buttons.
- **Fifteen Puzzle**: Arrange the tiles in order by sliding them into the empty space.
- **Euclid's Game**: A mathematical strategy game based on subtraction.

## Features

- Colorful, kid-friendly interface
- Random game selection
- Animated UI elements
- Multiple difficulty levels (where applicable)
- Hints and feedback to help learning

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Maths-Games.git
   cd Maths-Games
   ```

2. **Install dependencies:**
   - Requires Python 3 and GTK+ 3.
   - For Sugar integration, install `sugar3`:
     ```bash
     pip install sugar3
     ```

3. **Run as a Sugar Activity:**
   - From Sugar, install the `.xo` bundle or run:
     ```bash
     python3 setup.py dev
     ```

4. **Run standalone (for development):**
   ```bash
   python3 MathsGamesActivity.py
   ```

## Usage

- Launch the activity from Sugar or run `MathsGamesActivity.py`.
- Select a game from the main menu or try a random game.
- Each game has its own instructions and difficulty settings.

## License

MIT License

## Credits

Developed for Sugar Labs.

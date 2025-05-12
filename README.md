# Maths Games

A collection of fun and educational math games for kids, designed for the Sugar learning platform.

## Included Games

- **Broken Calculator**: Reach the target number using a calculator with some broken buttons.
  - Teaches: Arithmetic operations, number composition, and problem-solving
  - Difficulty levels: Easy (2 broken numbers, 1 broken operator), Medium (3 broken numbers, 2 broken operators), Hard (4 broken numbers, 1 broken operator)
  - Skills developed: Mental math and computational thinking

- **Euclid's Game**: A mathematical strategy game based on finding the positive difference between existing numbers.
  - Teaches: Number theory, GCD concepts, and strategic thinking
  - Difficulty levels: Uses randomly generated number pairs (10-50 and 60-100 ranges)
  - Skills developed: Number sense and mathematical reasoning

- **Fifteen Puzzle**: Arrange the tiles in order by sliding them into the empty space, with math equations on tiles.
  - Teaches: Spatial reasoning, planning, and sequential thinking
  - Modes: Numbers mode and Math mode (shows equations instead of numbers)
  - Skills developed: Memory, visualization, and number equivalence understanding

- **Math Minesweeper**: Uncover cells while solving math questions to avoid mines.
  - Teaches: Deductive reasoning, arithmetic, and problem-solving
  - Question types: True/false, missing operators, word problems, time riddles
  - Skills developed: Quick mathematical thinking and logical reasoning

- **Number Ninja**: An action game where players must quickly identify numbers to solve mathematical equations.
  - Teaches: Number recognition, calculation speed, and equation solving
  - Features: Animated UI, score tracking, combo system for consecutive correct answers
  - Skills developed: Quick mental calculations and numerical fluency

- **Oddscoring**: Identify and score points by distinguishing between odd and even numbers.
  - Teaches: Odd/even number recognition, pattern identification
  - Features: Grid-based gameplay with color-coded odd and even cells
  - Skills developed: Pattern recognition and numerical classification

## Demo Videos

Watch our games in action:

- [**Watch the Overview Video**](https://example.com/maths-games-overview) - A quick tour of all games

Embed in your classroom materials:
```html
<iframe width="560" height="315" src="https://www.youtube.com/embed/DEMO_VIDEO_ID" frameborder="0" allowfullscreen></iframe>
```

## Features

- Colorful, kid-friendly interface
- Random game selection
- Animated UI elements
- Multiple difficulty levels (where applicable)
- Hints and feedback to help learning

## System Requirements

- Operating System: Linux, Windows, or macOS
- Python version: 3.6 or higher
- Display: 800×600 resolution or higher
- RAM: 512MB minimum
- Storage: 50MB free space

## Detailed Installation Guide

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Maths-Games.git
   cd Maths-Games
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate    # On Linux/macOS
   # OR
   venv\Scripts\activate.bat   # On Windows
   ```

3. **Install dependencies:**
   - Basic dependencies:
     ```bash
     pip install -r requirements.txt
     ```
   - For Sugar integration, install `sugar3`:
     ```bash
     pip install sugar3 pygame
     ```
   - Additional packages for specific games:
     ```bash
     pip install numpy matplotlib
     ```

4. **Configuration (if needed):**
   ```bash
   cp config.example.json config.json
   # Edit config.json with your preferred settings
   ```

5. **Run as a Sugar Activity:**
   - From Sugar, install the `.xo` bundle or run:
     ```bash
     python3 setup.py dev
     ```

6. **Run standalone (for development):**
   ```bash
   python3 MathsGamesActivity.py
   ```

## Troubleshooting Installation

- **Missing dependencies error**: Make sure you've installed all required packages:
  ```bash
  pip install -r requirements.txt
  ```

- **Display issues**: Try running with the `--no-fullscreen` option:
  ```bash
  python3 MathsGamesActivity.py --no-fullscreen
  ```

- **Audio problems**: Check your system's sound configuration or disable sound:
  ```bash
  python3 MathsGamesActivity.py --no-sound
  ```

## Usage

- Launch the activity from Sugar or run `MathsGamesActivity.py`.
- Select a game from the main menu or try a random game.
- Each game has its own instructions and difficulty settings.
- Progress is automatically saved between sessions.
- Press 'H' at any time to see in-game help.

## Educational Benefits

These math games are designed to:
- Reinforce key mathematical concepts in an engaging way
- Develop critical thinking and problem-solving skills
- Adapt to different learning styles and abilities
- Provide immediate feedback to enhance understanding
- Create a positive attitude toward mathematics through play

## License

MIT License

## Credits

Developed for Sugar Labs by math educators and open-source contributors.

## Documentation

For developers and educators, detailed documentation is available in the `docs/` directory.

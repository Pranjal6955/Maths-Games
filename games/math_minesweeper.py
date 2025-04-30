#!/usr/bin/env python3
# Math Minesweeper Game
# A math-based twist on the classic Minesweeper game for kids
# Uses GTK3 for the user interface

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, Pango
import random
import os
import datetime

class QuestionGenerator:
    def __init__(self):
        """Initialize the question generator with various question types"""
        self.question_types = [
            self._generate_number_pattern,
            self._generate_fill_in_blank,
            self._generate_missing_operator,
            self._generate_reverse_logic,
            self._generate_word_puzzle,
            self._generate_true_false,
            self._generate_time_riddle
        ]
    
    def get_random_question(self):
        """Returns a random question, its answer, and its type"""
        question_func = random.choice(self.question_types)
        return question_func()
    
    def _generate_number_pattern(self):
        """Generate a number pattern question"""
        pattern_type = random.choice(["arithmetic", "geometric", "fibonacci"])
        
        if pattern_type == "arithmetic":
            # Arithmetic sequence (add constant)
            start = random.randint(1, 10)
            step = random.randint(1, 5)
            sequence = [start + i * step for i in range(4)]
            answer = start + 4 * step
            
        elif pattern_type == "geometric":
            # Geometric sequence (multiply by constant)
            start = random.randint(1, 5)
            ratio = random.randint(2, 3)
            sequence = [start * (ratio ** i) for i in range(4)]
            answer = start * (ratio ** 4)
            
        else:  # fibonacci-like
            # Simple fibonacci-like sequence (each number is sum of two before)
            a, b = random.randint(1, 5), random.randint(1, 5)
            sequence = [a, b]
            for _ in range(2):
                sequence.append(sequence[-1] + sequence[-2])
            answer = sequence[-1] + sequence[-2]
        
        question = f"What comes next? {', '.join(map(str, sequence))}, ___"
        return question, str(answer), "number_pattern"
    
    def _generate_fill_in_blank(self):
        """Generate a fill-in-the-blank arithmetic question"""
        operation = random.choice(["addition", "subtraction", "multiplication"])
        
        if operation == "addition":
            a = random.randint(5, 20)
            c = random.randint(10, 30)
            b = c - a
            question = f"{a} + ___ = {c}"
            
        elif operation == "subtraction":
            b = random.randint(5, 20)
            c = random.randint(b + 5, b + 25)
            a = c + b
            question = f"{a} - ___ = {c}"
            
        else:  # multiplication
            a = random.randint(2, 9)
            c = random.randint(a + 1, 20)
            b = c // a
            if b * a == c:  # Ensure exact division
                question = f"{a} × ___ = {c}"
            else:
                a = random.randint(2, 9)
                b = random.randint(2, 9)
                c = a * b
                question = f"{a} × ___ = {c}"
        
        return question, str(b), "fill_in_blank"
    
    def _generate_missing_operator(self):
        """Generate a missing operator question"""
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        
        # Generate answer for all possible operators
        results = {
            '+': a + b,
            '-': a - b,
            '×': a * b,
            '÷': a / b if b != 0 else None
        }
        
        # Choose operator with clean results (avoid division with remainder)
        valid_ops = [op for op, result in results.items() 
                    if result is not None and (op != '÷' or a % b == 0)]
        
        chosen_op = random.choice(valid_ops)
        result = results[chosen_op]
        
        question = f"What operator works? {a} ___ {b} = {int(result)}"
        return question, chosen_op, "missing_operator"
    
    def _generate_reverse_logic(self):
        """Generate a reverse logic question"""
        operations = [
            {"desc": "doubled a number", "op": lambda x: x * 2, "inv": lambda y: y // 2, "range": (2, 10)},
            {"desc": "tripled a number", "op": lambda x: x * 3, "inv": lambda y: y // 3, "range": (2, 7)},
            {"desc": "added 5 to a number", "op": lambda x: x + 5, "inv": lambda y: y - 5, "range": (1, 15)},
            {"desc": "subtracted 3 from a number", "op": lambda x: x - 3, "inv": lambda y: y + 3, "range": (4, 20)},
            {"desc": "squared a number", "op": lambda x: x ** 2, "inv": lambda y: int(y ** 0.5), "range": (2, 10)}
        ]
        
        op_info = random.choice(operations)
        original = random.randint(*op_info["range"])
        
        # Ensure clean results for operations like square root
        while "squared" in op_info["desc"] and int(original ** 0.5) ** 2 != original:
            original = random.randint(*op_info["range"])
        
        result = op_info["op"](original)
        
        question = f"I {op_info['desc']} and got {result}. What was the original number?"
        answer = original
        
        return question, str(answer), "reverse_logic"
    
    def _generate_word_puzzle(self):
        """Generate a simple word problem"""
        templates = [
            {
                "template": "{name} has {start} apples. {pronoun} buys {buys} more and eats {eats}. How many apples does {pronoun} have now?",
                "calc": lambda start, buys, eats: start + buys - eats,
                "ranges": {"start": (2, 8), "buys": (1, 5), "eats": (1, 3)}
            },
            {
                "template": "{name} has {start} pencils. {pronoun} gives {gives} to friends and finds {finds} more. How many pencils does {pronoun} have now?",
                "calc": lambda start, gives, finds: start - gives + finds,
                "ranges": {"start": (5, 10), "gives": (1, 4), "finds": (1, 4)}
            },
            {
                "template": "There are {start} children on a bus. {board} more get on and {exit} get off. How many children are on the bus now?",
                "calc": lambda start, board, exit: start + board - exit,
                "ranges": {"start": (5, 15), "board": (2, 8), "exit": (1, 7)}
            }
        ]
        
        names = [("Amy", "she"), ("Tom", "he"), ("Sam", "they"), ("Pat", "they"), ("Alex", "they")]
        template_data = random.choice(templates)
        
        # Generate random values for the puzzle
        values = {}
        for key, (min_val, max_val) in template_data["ranges"].items():
            values[key] = random.randint(min_val, max_val)
        
        # Select a random name if needed
        if "{name}" in template_data["template"]:
            name, pronoun = random.choice(names)
            values["name"] = name
            values["pronoun"] = pronoun
            
        # Calculate the answer
        answer = template_data["calc"](**{k: v for k, v in values.items() if k in ["start", "buys", "eats", "gives", "finds", "board", "exit"]})
        
        # Generate the question
        question = template_data["template"].format(**values)
        
        return question, str(answer), "word_puzzle"
    
    def _generate_true_false(self):
        """Generate a true/false math statement"""
        operation = random.choice(["addition", "subtraction", "multiplication"])
        is_true = random.choice([True, False])
        
        if operation == "addition":
            a = random.randint(1, 20)
            b = random.randint(1, 20)
            true_result = a + b
            
        elif operation == "subtraction":
            a = random.randint(5, 25)
            b = random.randint(1, a)
            true_result = a - b
            
        else:  # multiplication
            a = random.randint(2, 10)
            b = random.randint(2, 10)
            true_result = a * b
        
        if is_true:
            result = true_result
            answer = "True"
        else:
            # Make the false result close to true result for challenge
            offset = random.choice([-2, -1, 1, 2])
            result = true_result + offset
            answer = "False"
        
        if operation == "addition":
            question = f"True or False: {a} + {b} = {result}"
        elif operation == "subtraction":
            question = f"True or False: {a} - {b} = {result}"
        else:  # multiplication
            question = f"True or False: {a} × {b} = {result}"
        
        return question, answer, "true_false"
    
    def _generate_time_riddle(self):
        """Generate a time-based riddle"""
        # Generate a random current time
        current_hour = random.randint(1, 12)
        am_pm = random.choice(["AM", "PM"])
        
        # Generate time change
        hours_change = random.randint(1, 5)
        operation = random.choice(["add", "subtract"])
        
        if operation == "add":
            new_hour = (current_hour + hours_change) % 12
            if new_hour == 0:
                new_hour = 12
            
            # Handle AM/PM change
            new_am_pm = am_pm
            if current_hour + hours_change > 12:
                new_am_pm = "PM" if am_pm == "AM" else "AM"
                
            question = f"If it's {current_hour} {am_pm} now, what time will it be in {hours_change} hours?"
            answer = f"{new_hour} {new_am_pm}"
        else:
            new_hour = (current_hour - hours_change) % 12
            if new_hour <= 0:
                new_hour += 12
            
            # Handle AM/PM change
            new_am_pm = am_pm
            if current_hour - hours_change <= 0:
                new_am_pm = "PM" if am_pm == "AM" else "AM"
                
            question = f"If it's {current_hour} {am_pm} now, what time was it {hours_change} hours ago?"
            answer = f"{new_hour} {new_am_pm}"
        
        return question, answer, "time_riddle"


class MathMinesweeperGame(Gtk.Window):
    def __init__(self):
        super(MathMinesweeperGame, self).__init__(title="Math Minesweeper")
        self.set_default_size(600, 700)
        self.set_border_width(10)
        
        # Initialize CSS
        self._initialize_css()
        
        # Game state
        self.score = 0
        self.lives = 3
        self.question_generator = QuestionGenerator()
        
        # Main layout container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box)
        
        # Game title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold' foreground='#1b5e20'>Math Minesweeper</span>")
        main_box.pack_start(title_label, False, False, 10)
        
        # Instructions
        instructions_label = Gtk.Label()
        instructions_label.set_markup("<span style='italic'>Click on tiles to reveal them. Answer math questions correctly to earn points!</span>")
        instructions_label.set_line_wrap(True)
        main_box.pack_start(instructions_label, False, False, 5)
        
        # Header with score and lives
        header_box = self._create_header()
        main_box.pack_start(header_box, False, False, 10)
        
        # Game grid
        self.grid = self._create_grid()
        main_box.pack_start(self.grid, True, True, 0)
        
        # Restart button
        restart_button = Gtk.Button(label="Restart Game")
        restart_button.connect("clicked", self._on_restart_clicked)
        main_box.pack_start(restart_button, False, False, 10)
    
    def _initialize_css(self):
        """Set up CSS for styling the game"""
        css_provider = Gtk.CssProvider()
        css = """
        window {
            background: linear-gradient(135deg, #f6f8fa 0%, #e9f2ff 100%);
            color: #000000;
        }
        
        .tile-button {
            background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
            color: #000000;
            font-weight: bold;
            font-size: 20px;
            border-radius: 12px;
        }
        
        .tile-button:hover {
            background-color: #2980b9;
            color: #000000;
        }
        
        .tile-button:insensitive {
            background-color: #ecf0f1;
            color: #000000;
            font-size: 24px;
        }
        
        .correct-tile {
            background-color: #2ecc71;
            color: #000000;
        }
        
        .wrong-tile {
            background-color: #e74c3c;
            color: #000000;
        }
        
        .header-label {
            font-size: 16px;
            font-weight: bold;
            color: #1b5e20;
        }
        
        .score-value {
            color: #000000;
            font-weight: bold;
            font-size: 18px;
        }
        
        .lives-value {
            color: #000000;
            font-weight: bold;
            font-size: 18px;
        }
        """
        css_provider.load_from_data(css.encode())
        
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def _create_header(self):
        """Create the header with score and lives display"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)
        
        # Score Label
        score_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        score_label = Gtk.Label(label="Score:")
        score_label.get_style_context().add_class("header-label")
        
        self.score_value = Gtk.Label(label="0")
        self.score_value.get_style_context().add_class("score-value")
        
        score_box.pack_start(score_label, False, False, 0)
        score_box.pack_start(self.score_value, False, False, 0)
        
        # Lives Label
        lives_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        lives_label = Gtk.Label(label="Lives:")
        lives_label.get_style_context().add_class("header-label")
        
        self.lives_value = Gtk.Label(label="❤️ ❤️ ❤️")
        self.lives_value.get_style_context().add_class("lives-value")
        
        lives_box.pack_start(lives_label, False, False, 0)
        lives_box.pack_start(self.lives_value, False, False, 0)
        
        # Add to header
        header_box.pack_start(score_box, True, True, 0)
        header_box.pack_start(lives_box, True, True, 0)
        
        return header_box
    
    def _create_grid(self):
        """Create the game grid with buttons"""
        grid = Gtk.Grid()
        grid.set_row_homogeneous(True)
        grid.set_column_homogeneous(True)
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        
        # Create 5x5 grid of buttons
        self.buttons = []
        for row in range(5):
            button_row = []
            for col in range(5):
                button = Gtk.Button()
                
                # Add CSS class for styling
                context = button.get_style_context()
                context.add_class("tile-button")
                
                # Connect button to click handler with position information
                button.connect("clicked", self._on_tile_clicked, row, col)
                
                grid.attach(button, col, row, 1, 1)
                button_row.append(button)
            self.buttons.append(button_row)
        
        return grid
    
    def _on_tile_clicked(self, button, row, col):
        """Handle click on a game tile"""
        # Only process click if button is still sensitive (not yet revealed)
        if button.get_sensitive():
            # Generate a random question
            question, correct_answer, question_type = self.question_generator.get_random_question()
            
            # Create and show dialog
            dialog = self._create_question_dialog(question, question_type)
            response = dialog.run()
            
            user_answer = ""
            if question_type == "true_false":
                # Get the active radio button for True/False questions
                for radio_button in dialog.radio_buttons:
                    if radio_button.get_active():
                        user_answer = radio_button.get_label()
                        break
            elif question_type == "missing_operator":
                # Get the selected operator from the combo box
                tree_iter = dialog.combo_box.get_active_iter()
                model = dialog.combo_box.get_model()
                user_answer = model[tree_iter][0]
            else:
                # Get the text entry for other question types
                user_answer = dialog.entry.get_text().strip()
            
            dialog.destroy()
            
            # Process answer if dialog wasn't cancelled
            if response == Gtk.ResponseType.OK:
                self._process_answer(button, row, col, user_answer, correct_answer)
    
    def _create_question_dialog(self, question, question_type):
        """Create a dialog to show a question"""
        dialog = Gtk.Dialog(
            title="Math Question",
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            buttons=(
                "Cancel", Gtk.ResponseType.CANCEL,
                "Submit", Gtk.ResponseType.OK
            )
        )
        
        # Make the dialog a bit larger
        dialog.set_default_size(350, 180)
        
        # Create content area
        content_area = dialog.get_content_area()
        content_area.set_margin_top(15)
        content_area.set_margin_bottom(15)
        content_area.set_margin_start(15)
        content_area.set_margin_end(15)
        content_area.set_spacing(15)
        
        # Add question label
        question_label = Gtk.Label()
        question_label.set_markup(f"<span size='large' weight='bold'>{question}</span>")
        question_label.set_line_wrap(True)
        question_label.set_max_width_chars(40)
        question_label.set_justify(Gtk.Justification.CENTER)
        content_area.pack_start(question_label, False, False, 0)
        
        # Handle different question types
        if question_type == "true_false":
            # Create radio buttons for True/False
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=40)
            box.set_halign(Gtk.Align.CENTER)
            
            true_button = Gtk.RadioButton.new_with_label_from_widget(None, "True")
            false_button = Gtk.RadioButton.new_with_label_from_widget(true_button, "False")
            
            box.pack_start(true_button, False, False, 0)
            box.pack_start(false_button, False, False, 0)
            content_area.pack_start(box, False, False, 0)
            
            # Store reference to radio buttons for later access
            dialog.radio_buttons = [true_button, false_button]
            
        elif question_type == "missing_operator":
            # Create a combo box for operators
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.set_halign(Gtk.Align.CENTER)
            
            label = Gtk.Label(label="Select operator:")
            box.pack_start(label, False, False, 0)
            
            # Create the combo box
            combo_box = Gtk.ComboBoxText()
            for op in ['+', '-', '×', '÷']:
                combo_box.append_text(op)
            combo_box.set_active(0)  # Default to first option
            
            box.pack_start(combo_box, False, False, 0)
            content_area.pack_start(box, False, False, 0)
            
            # Store reference to combo box
            dialog.combo_box = combo_box
            
        else:
            # Create entry for text input
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            box.set_halign(Gtk.Align.CENTER)
            
            label = Gtk.Label(label="Your answer:")
            box.pack_start(label, False, False, 0)
            
            entry = Gtk.Entry()
            entry.set_activates_default(True)
            entry.set_width_chars(15)
            entry.set_halign(Gtk.Align.CENTER)
            box.pack_start(entry, False, False, 0)
            
            content_area.pack_start(box, False, False, 0)
            
            # Store reference to entry for later access
            dialog.entry = entry
        
        # Set the OK button as the default response
        dialog.set_default_response(Gtk.ResponseType.OK)
        
        dialog.show_all()
        return dialog
    
    def _process_answer(self, button, row, col, user_answer, correct_answer):
        """Process the answer and update game state"""
        # Convert answers to strings for comparison
        user_answer_str = str(user_answer).strip().lower()
        correct_answer_str = str(correct_answer).strip().lower()
        
        # Check if the answer is correct
        if user_answer_str == correct_answer_str:
            # Correct answer - handle it
            self._handle_correct_answer(button, row, col)
        else:
            # Wrong answer - handle it
            self._handle_wrong_answer(button, row, col)
    
    def _handle_correct_answer(self, button, row, col):
        """Handle correct answer - reveal tile and update score"""
        # Update button appearance to show it's cleared
        button.set_sensitive(False)
        button.set_label("🚀")
        context = button.get_style_context()
        context.add_class("correct-tile")
        
        # Update score
        self.score += 10
        self.score_value.set_text(str(self.score))
        
        # Check if all tiles are cleared (game won)
        tiles_remaining = sum(1 for row in self.buttons for button in row if button.get_sensitive())
        if tiles_remaining == 0:
            self._show_game_over_dialog("You Win!", f"You've cleared all tiles!\nFinal Score: {self.score}")
    
    def _handle_wrong_answer(self, button, row, col):
        """Handle wrong answer - mark as mine and update lives"""
        # Decrease lives
        self.lives -= 1
        
        # Update lives display
        hearts = "❤️ " * self.lives
        self.lives_value.set_text(hearts)
        
        # Mark the tile as a mine
        button.set_sensitive(False)
        button.set_label("💣")
        context = button.get_style_context()
        context.add_class("wrong-tile")
        
        # Check if game over
        if self.lives <= 0:
            self._show_game_over_dialog("Game Over!", f"You've run out of lives!\nFinal Score: {self.score}")
    
    def _show_game_over_dialog(self, title, message):
        """Show game over dialog with results"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
        
        # Disable all remaining buttons
        for row in self.buttons:
            for button in row:
                button.set_sensitive(False)
    
    def _on_restart_clicked(self, button):
        """Handle restart button click"""
        # Reset score and lives
        self.score = 0
        self.lives = 3
        self.score_value.set_text("0")
        self.lives_value.set_text("❤️ ❤️ ❤️")
        
        # Reset buttons
        for row in self.buttons:
            for button in row:
                button.set_label("")
                button.set_sensitive(True)
                context = button.get_style_context()
                context.remove_class("correct-tile")
                context.remove_class("wrong-tile")


def main():
    """Main function to run the game"""
    win = MathMinesweeperGame()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
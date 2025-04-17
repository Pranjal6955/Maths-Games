import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import random
import re

class BrokenCalculatorApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Broken Calculator")
        self.set_border_width(18)
        self.set_default_size(600, 800)  # Larger default for better scaling
        self.set_resizable(True)  # Allow window resizing
        self.set_name("broken-calc-window")
        # Set a playful window icon (optional, requires icon file)
        # self.set_icon_from_file("/path/to/icon.png")
        
        # Game state variables
        self.difficulty = 1  # Default: Easy
        self.max_attempts = 5
        self.total_score = 0
        self.rounds_played = 0
        self.current_attempt = 0
        self.target_number = 0
        self.available_buttons = []
        self.game_active = False
        self.animation_timeout_id = None
        
        # Create the main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        main_box.set_homogeneous(False)
        self.add(main_box)
        
        # Header with game info
        header_box = self.create_header()
        main_box.pack_start(header_box, False, False, 0)
        
        # Target and game stats area
        info_box = self.create_info_area()
        main_box.pack_start(info_box, False, False, 0)
        
        # Calculator display
        self.display = Gtk.Entry()
        self.display.set_editable(False)
        self.display.set_alignment(1)
        self.display.get_style_context().add_class("display")
        self.display.set_hexpand(True)
        self.display.set_vexpand(False)
        main_box.pack_start(self.display, False, False, 0)
        
        # Calculator buttons
        buttons_grid = self.create_calculator_buttons()
        main_box.pack_start(buttons_grid, True, True, 0)
        
        # Feedback area
        self.feedback_label = Gtk.Label()
        self.feedback_label.set_line_wrap(True)
        self.feedback_label.set_hexpand(True)
        self.feedback_label.set_vexpand(True)
        self.feedback_label.set_justify(Gtk.Justification.CENTER)
        main_box.pack_start(self.feedback_label, True, True, 10)
        
        # Bottom controls area
        controls_box = self.create_controls()
        main_box.pack_start(controls_box, False, False, 0)
        
        # Apply CSS styling
        self.apply_css()
        
        # Show welcome message
        self.show_welcome()
        
    def create_header(self):
        """Create the header with title and instructions toggle"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>Broken Calculator</span>")
        header_box.pack_start(title_label, True, True, 0)
        
        # Help button
        help_button = Gtk.Button.new_from_icon_name("dialog-question", Gtk.IconSize.BUTTON)
        help_button.connect("clicked", self.show_instructions)
        header_box.pack_end(help_button, False, False, 0)
        
        return header_box
        
    def create_info_area(self):
        """Create the area showing target number, score, and attempts"""
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        info_box.set_hexpand(True)
        info_box.set_vexpand(False)
        info_box.set_homogeneous(True)
        
        # Target number
        target_frame = Gtk.Frame(label="Target")
        target_frame.set_label_align(0.5, 0.5)  # Center the frame label
        target_frame.set_hexpand(True)
        target_frame.set_vexpand(True)
        self.target_label = Gtk.Label()
        self.target_label.set_markup("<span size='20000' weight='bold' foreground='#0077cc'>0</span>")
        self.target_label.set_justify(Gtk.Justification.CENTER)
        self.target_label.set_halign(Gtk.Align.FILL)
        self.target_label.set_valign(Gtk.Align.FILL)
        self.target_label.set_hexpand(True)
        self.target_label.set_vexpand(True)
        self.target_label.get_style_context().add_class("stat-label")
        target_frame.add(self.target_label)
        info_box.pack_start(target_frame, True, True, 0)
        
        # Attempts
        attempts_frame = Gtk.Frame(label="Attempts")
        attempts_frame.set_label_align(0.5, 0.5)  # Center the frame label
        attempts_frame.set_hexpand(True)
        attempts_frame.set_vexpand(True)
        self.attempts_label = Gtk.Label(label="0/5")
        self.attempts_label.set_justify(Gtk.Justification.CENTER)
        self.attempts_label.set_halign(Gtk.Align.FILL)
        self.attempts_label.set_valign(Gtk.Align.FILL)
        self.attempts_label.set_hexpand(True)
        self.attempts_label.set_vexpand(True)
        self.attempts_label.get_style_context().add_class("stat-label")
        attempts_frame.add(self.attempts_label)
        info_box.pack_start(attempts_frame, True, True, 0)
        
        # Score
        score_frame = Gtk.Frame(label="Score")
        score_frame.set_label_align(0.5, 0.5)  # Center the frame label
        score_frame.set_hexpand(True)
        score_frame.set_vexpand(True)
        self.score_label = Gtk.Label(label="0")
        self.score_label.set_justify(Gtk.Justification.CENTER)
        self.score_label.set_halign(Gtk.Align.FILL)
        self.score_label.set_valign(Gtk.Align.FILL)
        self.score_label.set_hexpand(True)
        self.score_label.set_vexpand(True)
        self.score_label.get_style_context().add_class("stat-label")
        score_frame.add(self.score_label)
        info_box.pack_start(score_frame, True, True, 0)
        
        # Round
        round_frame = Gtk.Frame(label="Round")
        round_frame.set_label_align(0.5, 0.5)  # Center the frame label
        round_frame.set_hexpand(True)
        round_frame.set_vexpand(True)
        self.round_label = Gtk.Label(label="0")
        self.round_label.set_justify(Gtk.Justification.CENTER)
        self.round_label.set_halign(Gtk.Align.FILL)
        self.round_label.set_valign(Gtk.Align.FILL)
        self.round_label.set_hexpand(True)
        self.round_label.set_vexpand(True)
        self.round_label.get_style_context().add_class("stat-label")
        round_frame.add(self.round_label)
        info_box.pack_start(round_frame, True, True, 0)
        
        return info_box
        
    def create_calculator_buttons(self):
        """Create the calculator button grid"""
        buttons_grid = Gtk.Grid()
        buttons_grid.set_row_homogeneous(True)
        buttons_grid.set_column_homogeneous(True)
        buttons_grid.set_hexpand(True)
        buttons_grid.set_vexpand(True)
        
        # Create calculator buttons
        self.calc_buttons = {}
        button_labels = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', 'C', '=', '+'
        ]
        
        positions = [
            (0, 0), (0, 1), (0, 2), (0, 3),
            (1, 0), (1, 1), (1, 2), (1, 3),
            (2, 0), (2, 1), (2, 2), (2, 3),
            (3, 0), (3, 1), (3, 2), (3, 3)
        ]
        
        for label, (row, col) in zip(button_labels, positions):
            button = Gtk.Button(label=label)
            button.get_style_context().add_class("calculator-button")
            button.set_hexpand(True)
            button.set_vexpand(True)
            
            # Add specific styling classes for different button types
            if label in "0123456789":
                button.get_style_context().add_class("number-button")
            elif label in "+-*/":
                button.get_style_context().add_class("operator-button")
            else:
                button.get_style_context().add_class("action-button")
                
            button.connect("clicked", self.on_button_clicked)
            
            self.calc_buttons[label] = button
            buttons_grid.attach(button, col, row, 1, 1)
            
            # Initially disable all buttons until game starts
            button.set_sensitive(False)
        
        return buttons_grid
    
    def create_controls(self):
        """Create the bottom control area with game controls"""
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        controls_box.set_hexpand(True)
        controls_box.set_vexpand(False)
        
        # Difficulty selector
        diff_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        diff_box.set_hexpand(True)
        diff_box.set_vexpand(False)
        diff_box.set_homogeneous(True)
        diff_label = Gtk.Label(label="Difficulty:")
        diff_box.pack_start(diff_label, False, False, 5)
        
        # Radio buttons for difficulty with tooltips
        self.diff_easy = Gtk.RadioButton.new_with_label_from_widget(None, "Easy")
        self.diff_easy.set_tooltip_text("2 broken numbers, 1 broken operator")
        
        self.diff_medium = Gtk.RadioButton.new_with_label_from_widget(self.diff_easy, "Medium")
        self.diff_medium.set_tooltip_text("3 broken numbers, 2 broken operators")
        
        self.diff_hard = Gtk.RadioButton.new_with_label_from_widget(self.diff_easy, "Hard")
        self.diff_hard.set_tooltip_text("4 broken numbers, 1 broken operator")
        
        diff_box.pack_start(self.diff_easy, False, False, 5)
        diff_box.pack_start(self.diff_medium, False, False, 5)
        diff_box.pack_start(self.diff_hard, False, False, 5)
        
        controls_box.pack_start(diff_box, False, False, 0)
        
        # Action buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_hexpand(True)
        buttons_box.set_vexpand(False)
        buttons_box.set_homogeneous(True)
        
        self.start_button = Gtk.Button(label="Start Game")
        self.start_button.connect("clicked", self.on_start_game)
        buttons_box.pack_start(self.start_button, True, True, 0)
        
        self.hint_button = Gtk.Button(label="Get Hint")
        self.hint_button.connect("clicked", self.on_hint_clicked)
        self.hint_button.set_sensitive(False)
        buttons_box.pack_start(self.hint_button, True, True, 0)
        
        self.next_button = Gtk.Button(label="Next Round")
        self.next_button.connect("clicked", self.on_next_round)
        self.next_button.set_sensitive(False)
        buttons_box.pack_start(self.next_button, True, True, 0)
        
        controls_box.pack_start(buttons_box, False, False, 0)
        
        return controls_box
        
    def apply_css(self):
        """Apply CSS styling to the application"""
        css_provider = Gtk.CssProvider()
        css = """
        #broken-calc-window {
            background-image: linear-gradient(135deg, #f8fafc 0%, #e3f0ff 100%);
            border-radius: 32px;
            box-shadow: 0 8px 32px 0 rgba(60, 60, 120, 0.18), 0 1.5px 8px 0 rgba(60, 60, 120, 0.10);
            padding: 32px;
        }
        .dialog-shadow {
            border-radius: 32px;
            box-shadow: 0 8px 32px 0 rgba(60, 60, 120, 0.18), 0 1.5px 8px 0 rgba(60, 60, 120, 0.10);
            background: linear-gradient(135deg, #f3e5f5 0%, #ce93d8 100%);
            padding: 32px;
        }
        * {
            font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
        }
        frame {
            padding: 12px 0px 0px 0px;
            border-radius: 18px;
        }
        frame > * > * {
            background: linear-gradient(90deg, #f9f9f9 60%, #e3f0ff 100%);
            border-radius: 22px;
            padding: 18px 0 18px 0;
        }
        .stat-label {
            font-size: 22px;
            font-weight: bold;
        }
        .calculator-button {
            font-size: 26px;
            font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
            font-weight: bold;
            margin: 6px;
            border-radius: 20px;
            border: 3px solid #b3c6ff;
            box-shadow: 0px 8px 24px rgba(91, 110, 225, 0.10);
            background-image: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            transition: background 0.18s, color 0.18s, box-shadow 0.18s;
        }
        .number-button {
            background-image: linear-gradient(135deg, #b3e5fc 0%, #81d4fa 80%);
            color: #01579b;
            border-color: #4fc3f7;
        }
        .number-button:active {
            background-image: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
            color: #0288d1;
        }
        .operator-button {
            background-image: linear-gradient(135deg, #ffe082 0%, #ffb300 80%);
            color: #e65100;
            border-color: #ffd54f;
        }
        .operator-button:active {
            background-image: linear-gradient(135deg, #fff8e1 0%, #ffe082 100%);
            color: #ff6f00;
        }
        .action-button {
            background-image: linear-gradient(135deg, #c8e6c9 0%, #81c784 80%);
            color: #1b5e20;
            border-color: #66bb6a;
        }
        .action-button:active {
            background-image: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            color: #388e3c;
        }
        .broken-button {
            opacity: 0.18;
        }
        .display {
            font-size: 34px;
            font-family: 'Comic Sans MS', monospace, 'Segoe UI', sans-serif;
            margin: 18px 0 18px 0;
            padding: 18px;
            border-radius: 22px;
            background: linear-gradient(90deg, #f9f9f9 0%, #e3f0ff 80%);
            border: 4px solid #4ba6ff;
            color: #0066cc;
            box-shadow: 0px 2px 12px rgba(143, 91, 225, 0.10);
        }
        .header {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 16px;
            font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
        }
        .hint-text {
            font-style: italic;
            color: #6a1b9a;
            background: linear-gradient(90deg, #fff8e1 60%, #f3e5f5 100%);
            padding: 14px 18px;
            border-radius: 14px;
            border: 2px dashed #ba68c8;
            box-shadow: 0 2px 8px rgba(186,104,200,0.08);
            font-size: 20px;
            margin-top: 10px;
            margin-bottom: 10px;
        }
        .success-text {
            color: #00bb00;
            font-weight: bold;
            background-color: #eafff5;
            padding: 10px;
            border-radius: 10px;
        }
        .failure-text {
            color: #ff0000;
            font-weight: bold;
            background-color: #fff0f0;
            padding: 10px;
            border-radius: 10px;
        }
        .key-frame {
            border: 3px solid #5c6bc0;
            border-radius: 12px;
            padding: 8px;
            background-color: #f5f9ff;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
    def show_welcome(self):
        """Show the welcome message in the feedback area"""
        welcome_msg = (
            "Welcome to Broken Calculator!\n"
            "Try to reach the target number using only the working buttons.\n"
            "Select a difficulty and click 'Start Game' to begin."
        )
        self.feedback_label.set_text(welcome_msg)
        
    def show_instructions(self, button):
        """Show game instructions in a dialog"""
        dialog = Gtk.Dialog(
            title="How to Play",
            transient_for=self,
            flags=0,
        )
        dialog.set_default_size(600, 400)
        dialog.set_resizable(False)
        dialog.set_modal(True)

        # Create a frame for shadow effect
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.set_hexpand(True)
        frame.set_vexpand(True)
        frame.get_style_context().add_class("dialog-shadow")

        # VBox for content, center align, with padding and margin
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        vbox.set_border_width(24)
        vbox.set_halign(Gtk.Align.CENTER)
        vbox.set_valign(Gtk.Align.CENTER)
        vbox.set_margin_top(18)
        vbox.set_margin_bottom(18)
        vbox.set_margin_start(18)
        vbox.set_margin_end(18)
        vbox.set_size_request(700, -1)  # Increased width

        # Title
        title = Gtk.Label()
        title.set_markup("<span size='xx-large' weight='bold'>How to Play</span>")
        title.set_justify(Gtk.Justification.CENTER)
        title.set_halign(Gtk.Align.CENTER)
        title.set_margin_bottom(16)
        title.set_size_request(660, -1)  # Wider title label
        vbox.pack_start(title, False, False, 0)

        # Instructions text
        instructions = (
            "Your calculator is broken! Some buttons don't work.\n\n"
            "Game Rules:\n"
            "1. Try to reach the target number using only the working buttons\n"
            "2. You have 5 attempts per round\n"
            "3. Earn points based on how quickly you reach the target\n"
            "4. Difficulty levels:\n"
            "   - Easy: 2 broken numbers, 1 broken operator\n"
            "   - Medium: 3 broken numbers, 2 broken operators\n"
            "   - Hard: 4 broken numbers, 1 broken operator\n\n"
            "Use the 'Get Hint' button if you're stuck!"
        )
        instr_label = Gtk.Label(label=instructions)
        instr_label.set_justify(Gtk.Justification.LEFT)
        instr_label.set_line_wrap(True)
        instr_label.set_halign(Gtk.Align.CENTER)
        instr_label.set_valign(Gtk.Align.CENTER)
        instr_label.set_margin_top(8)
        instr_label.set_margin_bottom(16)
        instr_label.set_margin_start(8)
        instr_label.set_margin_end(8)
        instr_label.set_size_request(660, -1)  # Wider instructions
        vbox.pack_start(instr_label, True, True, 0)

        # OK button
        ok_button = Gtk.Button(label="Got it!")
        ok_button.set_halign(Gtk.Align.CENTER)
        ok_button.set_margin_top(10)
        ok_button.set_margin_bottom(4)
        ok_button.set_margin_start(4)
        ok_button.set_margin_end(4)
        ok_button.set_size_request(120, -1)
        ok_button.connect("clicked", lambda btn: dialog.response(Gtk.ResponseType.OK))
        vbox.pack_end(ok_button, False, False, 0)

        # Add vbox to frame, then frame to dialog
        frame.add(vbox)
        content_area = dialog.get_content_area()
        for child in content_area.get_children():
            content_area.remove(child)
        content_area.add(frame)
        dialog.set_size_request(600, -1)

        dialog.show_all()
        dialog.run()
        dialog.destroy()
        
    def on_start_game(self, button):
        """Start a new game with the selected difficulty"""
        # Set difficulty based on selection
        if self.diff_medium.get_active():
            self.difficulty = 2
        elif self.diff_hard.get_active():
            self.difficulty = 3
        else:
            self.difficulty = 1
            
        # Reset game state
        self.total_score = 0
        self.rounds_played = 0
        self.score_label.set_text("0")
        
        # Start the first round
        self.start_new_round()
        
        # Update UI state
        self.game_active = True
        self.start_button.set_label("Restart Game")
        self.hint_button.set_sensitive(True)
        
    def on_next_round(self, button):
        """Start a new round"""
        self.start_new_round()
        self.next_button.set_sensitive(False)
        
    def start_new_round(self):
        """Set up a new round of the game"""
        # Increment round counter
        self.rounds_played += 1
        self.round_label.set_text(str(self.rounds_played))
        
        # Reset attempt counter
        self.current_attempt = 0
        self.update_attempts_label()
        
        # Generate target number based on difficulty
        if self.difficulty == 1:
            self.target_number = random.randint(10, 50)
        elif self.difficulty == 2:
            self.target_number = random.randint(20, 100)
        else:
            self.target_number = random.randint(50, 200)
            
        self.target_label.set_markup(f"<span size='20000' weight='bold' foreground='#0077cc'>{self.target_number}</span>")
        
        # Generate available buttons based on difficulty
        self.generate_available_buttons()
        
        # Reset display
        self.display.set_text("")
        
        # Update feedback
        self.feedback_label.set_text(f"Round {self.rounds_played}: Try to reach {self.target_number}")
        
    def generate_available_buttons(self):
        """Generate a random set of available buttons for the calculator based on difficulty"""
        all_digits = list("0123456789")
        all_operators = list("+-*/")
        
        # Set number of broken buttons based on difficulty
        if self.difficulty == 1:  # Easy
            broken_digits = 2
            broken_operators = 1
        elif self.difficulty == 2:  # Medium
            broken_digits = 3
            broken_operators = 2
        else:  # Hard
            broken_digits = 4
            broken_operators = 1
        
        # Select buttons to break
        broken_digit_buttons = random.sample(all_digits, broken_digits)
        broken_operator_buttons = random.sample(all_operators, broken_operators)
        
        # Generate available buttons by removing broken ones
        available_digits = [d for d in all_digits if d not in broken_digit_buttons]
        available_operators = [op for op in all_operators if op not in broken_operator_buttons]
        
        # Always include = and C buttons
        self.available_buttons = available_digits + available_operators + ["=", "C"]
        
        # Update the UI to show which buttons are broken
        for label, button in self.calc_buttons.items():
            if label in self.available_buttons:
                button.set_sensitive(True)
                button.get_style_context().remove_class("broken-button")
            else:
                button.set_sensitive(False)
                button.get_style_context().add_class("broken-button")
                
        # Display information about broken buttons
        broken_digits_str = ", ".join(broken_digit_buttons)
        broken_ops_str = ", ".join(broken_operator_buttons)
        msg = f"Broken buttons: digits [{broken_digits_str}], operators [{broken_ops_str}]"
        self.feedback_label.set_text(msg)
                
    def on_button_clicked(self, button):
        """Handle calculator button clicks"""
        if not self.game_active:
            return
            
        label = button.get_label()
        current_text = self.display.get_text()
        
        if label == "C":
            # Clear the display
            self.display.set_text("")
        elif label == "=":
            # Evaluate the expression
            self.evaluate_expression()
        else:
            # Add the button value to the display
            self.display.set_text(current_text + label)
            
    def evaluate_expression(self):
        """Evaluate the current expression and check if target is reached"""
        expression = self.display.get_text()
        
        if not expression:
            return
            
        # Increment attempt counter
        self.current_attempt += 1
        self.update_attempts_label()
        
        try:
            # Try evaluating the expression
            result = eval(expression)
            
            # Check if target is reached
            if result == self.target_number:
                self.handle_success()
            else:
                self.handle_wrong_answer(result)
                
            # Update display to show result
            self.display.set_text(str(result))
            
        except Exception as e:
            # Handle invalid expressions
            self.feedback_label.set_text("Invalid expression! Try again.")
            
        # Check if max attempts reached
        if self.current_attempt >= self.max_attempts and not self.next_button.get_sensitive():
            self.handle_game_over()
            
    def handle_success(self):
        """Handle the case when player reaches the target number"""
        # Calculate score based on attempts left and difficulty
        remaining_attempts = self.max_attempts - self.current_attempt
        points = 10 + (remaining_attempts * 5) + (self.difficulty * 5)
        self.total_score += points
        self.score_label.set_text(str(self.total_score))
        
        # Update feedback
        self.feedback_label.set_markup(
            f"<span foreground='#00bb00' weight='bold'>🎉 CORRECT! You earned {points} points!</span>"
        )
        
        # Enable next round button
        self.next_button.set_sensitive(True)
        
        # Pulse animation effect
        self.start_pulse_animation()
        
        # Show congratulations dialog
        self.show_congrats_popup(points)
        
    def start_pulse_animation(self):
        """Start a pulse animation effect on the target number"""
        # Instead of CSS animation, use a GLib timeout for a simple pulse effect
        self.pulse_size = 20000
        self.pulse_growing = True
        self.animation_timeout_id = GLib.timeout_add(100, self.pulse_animation_step)
    
    def pulse_animation_step(self):
        """Perform one step of the pulse animation"""
        if self.pulse_growing:
            self.pulse_size += 1000
            if self.pulse_size >= 25000:
                self.pulse_growing = False
        else:
            self.pulse_size -= 1000
            if self.pulse_size <= 20000:
                self.pulse_growing = True
        
        # Update the target label with the new size
        self.target_label.set_markup(
            f"<span size='{self.pulse_size}' weight='bold' foreground='#0077cc'>{self.target_number}</span>"
        )
        
        # Continue the animation for a few seconds
        if not hasattr(self, 'animation_counter'):
            self.animation_counter = 0
        
        self.animation_counter += 1
        if self.animation_counter >= 20:  # About 2 seconds
            self.animation_counter = 0
            self.target_label.set_markup(
                f"<span size='20000' weight='bold' foreground='#0077cc'>{self.target_number}</span>"
            )
            self.animation_timeout_id = None
            return False
        return True
    
    def show_congrats_popup(self, points):
        """Show a congratulations popup dialog with animated content"""
        dialog = Gtk.Dialog(
            title="Congratulations!",
            transient_for=self,
            flags=0,
            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        )
        dialog.set_default_size(300, 200)
        
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_border_width(15)
        
        # Create a box for the content
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Congratulations header
        header_label = Gtk.Label()
        header_label.set_markup(f"<span size='x-large' weight='bold' foreground='#00aa00'>🎉 CORRECT! 🎉</span>")
        content_box.pack_start(header_label, False, False, 5)
        
        # Target reached message
        target_label = Gtk.Label()
        target_label.set_markup(f"<span size='large'>You reached the target: <b>{self.target_number}</b></span>")
        content_box.pack_start(target_label, False, False, 5)
        
        # Points earned
        points_label = Gtk.Label()
        points_label.set_markup(f"<span size='large' foreground='#0000aa'>You earned <b>{points}</b> points!</span>")
        content_box.pack_start(points_label, False, False, 5)
        
        # Add some emoji decorations for kids
        emoji_label = Gtk.Label()
        emoji_label.set_markup("<span size='xx-large'>⭐🏆 🎮 ⭐</span>")
        content_box.pack_start(emoji_label, False, False, 10)
        
        content_area.pack_start(content_box, True, True, 0)
        
        dialog.show_all()
        
        # Set up a simple color changing animation
        self.dialog_animation_count = 0
        self.dialog_bg_colors = ["#f0fdf0", "#f0f0fd", "#fdf0f0", "#f0fdfd", "#fdf0fd"]
        GLib.timeout_add(300, self.animate_dialog_content, dialog, content_box)
        
        dialog.run()
        dialog.destroy()
    
    def animate_dialog_content(self, dialog, box):
        """Animate the content of the dialog with changing background colors"""
        self.dialog_animation_count += 1
        
        # Change background color on each animation step
        color_index = self.dialog_animation_count % len(self.dialog_bg_colors)
        color = self.dialog_bg_colors[color_index]
        
        # Set the background color directly
        box.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA.from_string(color)[0])
        
        # Continue animation for 10 cycles then stop
        return self.dialog_animation_count < 10
    
    def handle_wrong_answer(self, result):
        """Handle the case when player's calculation doesn't match target"""
        difference = abs(result - self.target_number)
        
        if difference <= 5:
            feedback = "Very close! Just a little off."
        elif difference <= 10:
            feedback = "Getting closer!"
        else:
            feedback = "Not quite there yet."
            
        attempts_left = self.max_attempts - self.current_attempt
        if attempts_left > 0:
            feedback += f" ({attempts_left} attempts left)"
            
        self.feedback_label.set_text(feedback)
        
    def handle_game_over(self):
        """Handle the case when player has used all attempts"""
        self.feedback_label.set_markup(
            f"<span foreground='#ff0000' weight='bold'>Game Over! The target was {self.target_number}</span>"
        )
        self.next_button.set_sensitive(True)
        
    def update_attempts_label(self):
        """Update the attempts counter in the UI"""
        self.attempts_label.set_text(f"{self.current_attempt}/{self.max_attempts}")
        
    def on_hint_clicked(self, button):
        """Provide a hint for reaching the target number"""
        if not self.game_active:
            return

        hint = self.generate_hint()
        # Use improved hint-text class for better style
        self.feedback_label.set_markup(f"<span class='hint-text'>Hint: {hint}</span>")
        
    def generate_hint(self):
        """Generate a hint for reaching the target number"""
        digits = [btn for btn in self.available_buttons if btn in "0123456789"]
        operators = [btn for btn in self.available_buttons if btn in "+-*/"]
        
        # Simple hint strategy
        if "+" in operators and self.target_number > 10:
            a = random.randint(1, self.target_number-1)
            b = self.target_number - a
            if all(d in digits for d in str(a)) and all(d in digits for d in str(b)):
                return f"Try adding two numbers to get {self.target_number}, like {a}+{b}."
        
        if "-" in operators:
            a = random.randint(self.target_number+1, self.target_number+20)
            b = a - self.target_number
            if all(d in digits for d in str(a)) and all(d in digits for d in str(b)):
                return f"Try subtracting from a larger number, like {a}-{b}."
        
        if "*" in operators and self.target_number > 1:
            factors = [i for i in range(1, 11) if self.target_number % i == 0]
            valid_factors = [f for f in factors if all(d in digits for d in str(f)) and 
                             all(d in digits for d in str(self.target_number // f))]
            if valid_factors:
                factor = random.choice(valid_factors)
                return f"Try multiplying {factor} by {self.target_number // factor}."
        
        if "/" in operators and self.target_number > 0:
            multiples = [self.target_number * i for i in range(1, 11)]
            valid_multiples = [m for m in multiples if all(d in digits for d in str(m))]
            if valid_multiples:
                multiple = random.choice(valid_multiples)
                return f"Try dividing {multiple} by {multiple // self.target_number}."
        
        # Generic hint
        available_ops = " and ".join([f"'{op}'" for op in operators])
        return f"Try combining {available_ops} operations with your available digits."

def main():
    """Main entry point for the application"""
    win = BrokenCalculatorApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

def run():
    win = BrokenCalculatorApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
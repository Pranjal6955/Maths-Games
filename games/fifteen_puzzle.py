import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import random
import time

class FifteenPuzzleApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Fifteen Puzzle")
        self.set_border_width(18)
        self.set_default_size(600, 800)  # Larger default for better scaling
        self.set_resizable(True)  # Allow window resizing
        self.set_name("fifteen-puzzle-window")
        
        # Game state variables
        self.grid_size = 4
        self.move_count = 0
        self.start_time = time.time()
        self.elapsed_time = 0
        self.timer_running = False  # Add this line to track timer status
        self.math_mode = True
        self.math_operations = {}
        self.last_moved_tile = None
        self.solved = False
        self.tiles = []  # To store tile buttons
        
        # Create the main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_hexpand(True)
        main_box.set_vexpand(True)
        main_box.set_homogeneous(False)
        self.add(main_box)
        
        # Header with game info
        header_box = self.create_header()
        main_box.pack_start(header_box, False, False, 0)
        
        # Info area (score, moves, time)
        info_box = self.create_info_area()
        main_box.pack_start(info_box, False, False, 0)
        
        # Puzzle grid
        self.grid = Gtk.Grid()
        self.grid.set_row_homogeneous(True)
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_spacing(8)
        self.grid.set_column_spacing(8)
        self.grid.set_hexpand(True)
        self.grid.set_vexpand(True)
        main_box.pack_start(self.grid, True, True, 0)
        
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
        
        # Initialize the game
        self.init_game()
        
        # Start timer for elapsed time updates
        GLib.timeout_add(1000, self.update_timer)
        
        # Show welcome message
        self.show_welcome()
    
    def create_header(self):
        """Create the header with title and instructions toggle"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Title
        title_label = Gtk.Label()
        title_label.set_markup("<span size='x-large' weight='bold'>Fifteen Puzzle</span>")
        header_box.pack_start(title_label, True, True, 0)
        
        # Help button
        help_button = Gtk.Button.new_from_icon_name("dialog-question", Gtk.IconSize.BUTTON)
        help_button.connect("clicked", self.show_instructions)
        header_box.pack_end(help_button, False, False, 0)
        
        return header_box
    
    def create_info_area(self):
        """Create the area showing score, moves, and time"""
        info_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        info_box.set_hexpand(True)
        info_box.set_vexpand(False)
        info_box.set_homogeneous(True)
        
        # Moves
        moves_frame = Gtk.Frame(label="Moves")
        moves_frame.set_label_align(0.5, 0.5)  # Center the frame label
        moves_frame.set_hexpand(True)
        moves_frame.set_vexpand(True)
        self.moves_label = Gtk.Label(label="0")
        self.moves_label.set_justify(Gtk.Justification.CENTER)
        self.moves_label.set_halign(Gtk.Align.FILL)
        self.moves_label.set_valign(Gtk.Align.FILL)
        self.moves_label.set_hexpand(True)
        self.moves_label.set_vexpand(True)
        self.moves_label.get_style_context().add_class("stat-label")
        moves_frame.add(self.moves_label)
        info_box.pack_start(moves_frame, True, True, 0)
        
        # Time
        time_frame = Gtk.Frame(label="Time")
        time_frame.set_label_align(0.5, 0.5)  # Center the frame label
        time_frame.set_hexpand(True)
        time_frame.set_vexpand(True)
        self.time_label = Gtk.Label(label="0:00")
        self.time_label.set_justify(Gtk.Justification.CENTER)
        self.time_label.set_halign(Gtk.Align.FILL)
        self.time_label.set_valign(Gtk.Align.FILL)
        self.time_label.set_hexpand(True)
        self.time_label.set_vexpand(True)
        self.time_label.get_style_context().add_class("stat-label")
        time_frame.add(self.time_label)
        info_box.pack_start(time_frame, True, True, 0)
        
        # Mode
        mode_frame = Gtk.Frame(label="Mode")
        mode_frame.set_label_align(0.5, 0.5)  # Center the frame label
        mode_frame.set_hexpand(True)
        mode_frame.set_vexpand(True)
        self.mode_label = Gtk.Label(label="Math")
        self.mode_label.set_justify(Gtk.Justification.CENTER)
        self.mode_label.set_halign(Gtk.Align.FILL)
        self.mode_label.set_valign(Gtk.Align.FILL)
        self.mode_label.set_hexpand(True)
        self.mode_label.set_vexpand(True)
        self.mode_label.get_style_context().add_class("stat-label")
        mode_frame.add(self.mode_label)
        info_box.pack_start(mode_frame, True, True, 0)
        
        return info_box
    
    def create_controls(self):
        """Create the bottom control area with game controls"""
        controls_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        controls_box.set_hexpand(True)
        controls_box.set_vexpand(False)
        
        # Math mode toggle
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        mode_box.set_hexpand(True)
        mode_box.set_vexpand(False)
        mode_box.set_homogeneous(True)
        mode_label = Gtk.Label(label="Game Mode:")
        mode_box.pack_start(mode_label, False, False, 5)
        
        # Radio buttons for game mode
        self.mode_number = Gtk.RadioButton.new_with_label_from_widget(None, "Numbers")
        self.mode_number.set_tooltip_text("Show numbers from 1 to 15")
        
        self.mode_math = Gtk.RadioButton.new_with_label_from_widget(self.mode_number, "Math")
        self.mode_math.set_tooltip_text("Show math equations instead of numbers")
        self.mode_math.set_active(True)  # Default to math mode
        
        mode_box.pack_start(self.mode_number, False, False, 5)
        mode_box.pack_start(self.mode_math, False, False, 5)
        
        # Connect toggle signals
        self.mode_number.connect("toggled", self.on_mode_toggled)
        self.mode_math.connect("toggled", self.on_mode_toggled)
        
        controls_box.pack_start(mode_box, False, False, 0)
        
        # Action buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_hexpand(True)
        buttons_box.set_vexpand(False)
        buttons_box.set_homogeneous(True)
        
        self.new_game_button = Gtk.Button(label="New Game")
        self.new_game_button.connect("clicked", self.on_new_game)
        buttons_box.pack_start(self.new_game_button, True, True, 0)
        
        self.hint_button = Gtk.Button(label="Get Hint")
        self.hint_button.connect("clicked", self.on_hint_clicked)
        buttons_box.pack_start(self.hint_button, True, True, 0)
        
        controls_box.pack_start(buttons_box, False, False, 0)
        
        return controls_box
    
    def apply_css(self):
        """Apply CSS styling to the application"""
        css_provider = Gtk.CssProvider()
        css = """
        #fifteen-puzzle-window {
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
            color: #000000;
        }
        label, button {
            color: black;
        }
        frame > label {
            color: black;
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
            color: black;
        }
        .tile-button {
            font-size: 26px;
            font-weight: bold;
            margin: 6px;
            border-radius: 20px;
            border: 3px solid #b3c6ff;
            min-height: 80px;
            min-width: 80px;
            background-image: linear-gradient(135deg, #b3e5fc 0%, #81d4fa 80%);
            color: #01579b;
            border-color: #4fc3f7;
        }
        .tile-button:active {
            background-image: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
            color: #0288d1;
        }
        .correct-position {
            background-image: linear-gradient(135deg, #c8e6c9 0%, #81c784 80%);
            color: #1b5e20;
            border-color: #66bb6a;
        }
        .empty-tile {
            background-color: #f5f5f5;
            border-color: #e0e0e0;
            opacity: 0.5;
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
            "Welcome to Fifteen Puzzle!\n"
            "Arrange the tiles in order from 1 to 15.\n"
            "Click 'New Game' to begin."
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
            "The goal of Fifteen Puzzle is to arrange the tiles in numerical order.\n\n"
            "Game Rules:\n"
            "1. Click on a tile to move it into the empty space\n"
            "2. A tile can only move if it's adjacent to the empty space\n"
            "3. Arrange the tiles in order from 1 to 15\n"
            "4. The empty space should end up in the bottom right corner\n\n"
            "Game Modes:\n"
            "- Numbers: Shows the numbers 1-15 on the tiles\n"
            "- Math: Shows math equations that equal the tile's number\n\n"
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
    
    def init_game(self):
        """Initialize the game board"""
        # Clear any existing tiles
        for child in self.grid.get_children():
            self.grid.remove(child)
        
        self.tiles = []
        
        # Create the board (1-15 and 0 for empty)
        self.board = list(range(1, self.grid_size * self.grid_size)) + [0]
        self.empty_pos = (self.grid_size - 1, self.grid_size - 1)
        
        # Generate math operations
        self.math_operations = self.generate_math_operations()
        
        # Shuffle board
        self.shuffle_board()
        
        # Create tile buttons
        self.create_tile_buttons()
        
        # Reset game state
        self.move_count = 0
        self.moves_label.set_text("0")
        self.start_time = time.time()
        self.elapsed_time = 0
        self.timer_running = False  # Reset timer state on new game
        self.update_timer()
        self.solved = False
        
        self.grid.show_all()
    
    def create_tile_buttons(self):
        """Create and arrange tile buttons based on the current board state"""
        self.tiles = []
        
        # Create buttons for each position in the grid
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                idx = y * self.grid_size + x
                value = self.board[idx]
                
                button = Gtk.Button()
                button.set_hexpand(True)
                button.set_vexpand(True)
                
                # Store the grid position as button data
                button.x_pos = x
                button.y_pos = y
                
                if value == 0:
                    # Empty tile
                    button.set_sensitive(False)
                    button.get_style_context().add_class("empty-tile")
                else:
                    # Normal tile
                    button.connect("clicked", self.on_tile_clicked)
                    button.get_style_context().add_class("tile-button")
                    
                    # Set button label based on mode
                    self.update_button_label(button, value)
                    
                    # Check if tile is in correct position
                    if value == idx + 1:
                        button.get_style_context().add_class("correct-position")
                
                self.grid.attach(button, x, y, 1, 1)
                self.tiles.append(button)
        
        # Show all the tiles
        self.grid.show_all()
    
    def generate_math_operations(self):
        """Generate simple math operations for numbers 1-15"""
        operations = {}
        for num in range(1, 16):
            # Generate different types of operations
            if num <= 5:
                # Simple addition for smaller numbers
                a = random.randint(0, num)
                operations[num] = f"{a} + {num - a}"
            elif num <= 10:
                # Mix of addition and subtraction
                op = random.choice(['+', '-'])
                if op == '+':
                    a = random.randint(1, num - 1)
                    operations[num] = f"{a} + {num - a}"
                else:
                    a = random.randint(num + 1, num + 5)
                    operations[num] = f"{a} - {a - num}"
            else:
                # Include multiplication for larger numbers
                op = random.choice(['+', '-', '×'])
                if op == '+':
                    a = random.randint(5, num - 1)
                    operations[num] = f"{a} + {num - a}"
                elif op == '-':
                    a = random.randint(num + 1, num + 10)
                    operations[num] = f"{a} - {a - num}"
                else:
                    factors = [i for i in range(2, 6) if num % i == 0]
                    if factors:
                        factor = random.choice(factors)
                        operations[num] = f"{factor} × {num // factor}"
                    else:
                        a = random.randint(5, num - 1)
                        operations[num] = f"{a} + {num - a}"
        return operations
    
    def update_button_label(self, button, value):
        """Update a button's label based on current mode"""
        if value == 0:
            button.set_label("")
            return
            
        if self.math_mode and value in self.math_operations:
            button.set_label(self.math_operations[value])
            # Add small number indicator in corner (could be improved with custom drawing)
            button.set_tooltip_text(f"Value: {value}")
        else:
            button.set_label(str(value))
    
    def shuffle_board(self):
        """Shuffle the board while ensuring it's solvable"""
        # Perform random valid moves to shuffle
        for _ in range(1000):
            possible_moves = self.get_possible_moves()
            move = random.choice(possible_moves)
            self.move_tile(move[0], move[1], update_ui=False)
        
        # Make sure the puzzle is solvable
        if not self.is_solvable():
            # Swap the first two tiles to make it solvable
            if self.board[0] != 0 and self.board[1] != 0:
                self.board[0], self.board[1] = self.board[1], self.board[0]
            else:
                self.board[2], self.board[3] = self.board[3], self.board[2]
    
    def is_solvable(self):
        """Check if the puzzle is solvable"""
        # Count inversions
        inversions = 0
        board_without_zero = [x for x in self.board if x != 0]
        
        for i in range(len(board_without_zero)):
            for j in range(i + 1, len(board_without_zero)):
                if board_without_zero[i] > board_without_zero[j]:
                    inversions += 1
        
        # For a 4x4 puzzle, if the empty tile is on an even row from the bottom (second or fourth row),
        # then the puzzle is solvable if the number of inversions is odd.
        # If the empty tile is on an odd row from the bottom (first or third row),
        # then the puzzle is solvable if the number of inversions is even.
        empty_row = self.empty_pos[0]
        if (self.grid_size - empty_row) % 2 == 0:
            return inversions % 2 == 1
        else:
            return inversions % 2 == 0
    
    def get_possible_moves(self):
        """Get coordinates of tiles that can be moved"""
        moves = []
        empty_x, empty_y = self.empty_pos
        
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            x, y = empty_x + dx, empty_y + dy
            if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                moves.append((x, y))
        
        return moves
    
    def move_tile(self, x, y, update_ui=True):
        """Move a tile to the empty position if it's adjacent"""
        empty_x, empty_y = self.empty_pos
        
        # Check if tile is adjacent to empty space
        if (x == empty_x and abs(y - empty_y) == 1) or (y == empty_y and abs(x - empty_x) == 1):
            # Get the index of the clicked tile and empty tile
            empty_idx = empty_y * self.grid_size + empty_x
            tile_idx = y * self.grid_size + x
            
            # Remember which tile was moved
            self.last_moved_tile = self.board[tile_idx]
            
            # Swap the tiles
            self.board[empty_idx], self.board[tile_idx] = self.board[tile_idx], self.board[empty_idx]
            self.empty_pos = (x, y)
            
            # Update UI if needed
            if update_ui:
                self.move_count += 1
                self.moves_label.set_text(str(self.move_count))
                self.update_grid_ui()
                self.check_solution()
            
            return True
        return False
    
    def update_grid_ui(self):
        """Update the grid UI after a move"""
        # Remove all buttons from the grid
        for child in self.grid.get_children():
            self.grid.remove(child)
        
        # Create new buttons based on current board state
        self.create_tile_buttons()
    
    def check_solution(self):
        """Check if the puzzle is solved"""
        solution = list(range(1, self.grid_size * self.grid_size)) + [0]
        if self.board == solution:
            self.solved = True
            self.feedback_label.set_markup(
                f"<span class='success-text'>🎉 CONGRATULATIONS! YOU SOLVED THE PUZZLE! 🎉</span>"
            )
            self.show_success_dialog()
        
    def show_success_dialog(self):
        """Show a success dialog"""
        dialog = Gtk.Dialog(
            title="Puzzle Solved!",
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
        
        # Success header
        header_label = Gtk.Label()
        header_label.set_markup(f"<span size='x-large' weight='bold' foreground='#00aa00'>🎉 PUZZLE SOLVED! 🎉</span>")
        content_box.pack_start(header_label, False, False, 5)
        
        # Stats
        mins = int(self.elapsed_time // 60)
        secs = int(self.elapsed_time % 60)
        stats_label = Gtk.Label()
        stats_label.set_markup(
            f"<span size='large'>You solved it in <b>{self.move_count}</b> moves!</span>\n"
            f"<span size='large'>Time: <b>{mins}:{secs:02d}</b></span>"
        )
        content_box.pack_start(stats_label, False, False, 5)
        
        # Add some emoji decorations for kids
        emoji_label = Gtk.Label()
        emoji_label.set_markup("<span size='xx-large'>⭐🏆 🎮 ⭐</span>")
        content_box.pack_start(emoji_label, False, False, 10)
        
        content_area.pack_start(content_box, True, True, 0)
        
        dialog.show_all()
        dialog.run()
        dialog.destroy()
    
    def on_tile_clicked(self, button):
        """Handle tile button clicks"""
        # Get the position of the clicked tile
        x = button.x_pos
        y = button.y_pos
        
        # Get the empty tile position
        empty_x, empty_y = self.empty_pos
        
        # Check if this tile can move
        if ((x == empty_x and abs(y - empty_y) == 1) or 
            (y == empty_y and abs(x - empty_x) == 1)):
            
            # Start the timer on the first move if it's not already running
            if not self.timer_running:
                self.timer_running = True
                self.start_time = time.time() - self.elapsed_time  # Account for any displayed time
            
            self.move_tile(x, y)
    
    def on_mode_toggled(self, button):
        """Handle mode toggle"""
        if button.get_active():
            if button == self.mode_math:
                self.math_mode = True
                self.mode_label.set_text("Math")
            else:
                self.math_mode = False
                self.mode_label.set_text("Numbers")
            
            # Update all button labels
            self.update_grid_ui()
    
    def on_new_game(self, button):
        """Start a new game"""
        self.init_game()
        self.feedback_label.set_text("New game started. Arrange the tiles in order from 1 to 15.")
    
    def on_hint_clicked(self, button):
        """Provide a hint for the puzzle"""
        hint = self.generate_hint()
        self.feedback_label.set_markup(f"<span class='hint-text'>Hint: {hint}</span>")
    
    def generate_hint(self):
        """Generate a hint for solving the puzzle"""
        # Find a tile that can be moved toward its correct position
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                idx = y * self.grid_size + x
                value = self.board[idx]
                
                if value == 0:
                    continue
                
                # Calculate where this tile should be
                target_idx = value - 1
                target_x = target_idx % self.grid_size
                target_y = target_idx // self.grid_size
                
                # Is this tile adjacent to the empty space?
                empty_x, empty_y = self.empty_pos
                if ((x == empty_x and abs(y - empty_y) == 1) or 
                    (y == empty_y and abs(x - empty_x) == 1)):
                    
                    # Calculate if moving would get it closer to target
                    current_dist = abs(x - target_x) + abs(y - target_y)
                    new_x, new_y = empty_x, empty_y
                    new_dist = abs(new_x - target_x) + abs(new_y - target_y)
                    
                    if new_dist < current_dist:
                        if self.math_mode:
                            return f"Try moving {self.math_operations[value]} toward its correct position"
                        else:
                            return f"Try moving tile {value} toward its correct position"
        
        # If no good move found, give general hint
        return "Focus on getting the top row and left column in place first"
    
    def update_timer(self):
        """Update the timer display"""
        if not self.solved and self.timer_running:
            self.elapsed_time = time.time() - self.start_time
            
        mins = int(self.elapsed_time // 60)
        secs = int(self.elapsed_time % 60)
        self.time_label.set_text(f"{mins}:{secs:02d}")
        
        return True  # Continue the timer

def main():
    """Main entry point for the application"""
    win = FifteenPuzzleApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()

def run():
    win = FifteenPuzzleApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
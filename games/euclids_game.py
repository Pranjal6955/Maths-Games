#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import random
import sugar3.activity.activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton, StopButton
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics import style
from sugar3.graphics.icon import Icon
from sugar3.graphics.alert import Alert
from sugar3.graphics.xocolor import XoColor


class EuclidsGameActivity(sugar3.activity.activity.Activity):
    """
    Euclid's Game - A Sugar activity where players create new numbers
    by finding the positive difference between existing numbers.
    """
    
    def __init__(self, handle):
        """Initialize the activity."""
        # Handle case when running outside of Sugar
        if handle is None:
            self._standalone_init()
            return
            
        super(EuclidsGameActivity, self).__init__(handle)
        
        # Apply modern CSS styling
        self._apply_css()
        
        # Initialize alerts container
        self._alerts = []
        
        # Set up the activity toolbar
        toolbar_box = ToolbarBox()
        
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        
        # Add a restart button
        restart_button = ToolButton('view-refresh')
        restart_button.set_tooltip('Restart Game')
        restart_button.connect('clicked', self.__restart_game_cb)
        toolbar_box.toolbar.insert(restart_button, -1)
        
        # Add a help button
        help_button = ToolButton('help-icon')
        help_button.set_tooltip('How to Play')
        help_button.connect('clicked', self.__show_help_cb)
        toolbar_box.toolbar.insert(help_button, -1)
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        
        self.set_toolbar_box(toolbar_box)
        
        # Game variables
        self.numbers_on_board = []
        self.player_moves = 0
        self.bot_moves = 0
        self.current_turn = "Player"  # "Player" or "Bot"
        self.game_active = False
        self.selected_numbers = []
        
        # Create the main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_border_width(10)
        self.set_canvas(self.main_box)
        
        # Create UI components
        self.__create_title_screen()
        self.__create_game_screen()
        
        # Initially show title screen
        self.__show_title_screen()
        self.show_all()
    
    def _standalone_init(self):
        """Initialize the activity when running standalone (outside of Sugar)."""
        Gtk.Window.__init__(self)
        self.set_default_size(800, 600)
        self.set_title("Euclid's Game")
        self.connect("destroy", Gtk.main_quit)
        
        # Apply modern CSS styling
        self._apply_css()
        
        # Initialize alerts container
        self._alerts = []
        
        # Create a simple toolbar for standalone mode
        toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        
        # Add a restart button
        restart_button = Gtk.Button(label="Restart Game")
        restart_button.connect('clicked', self.__restart_game_cb)
        toolbar_box.pack_start(restart_button, False, False, 5)
        
        # Add a help button
        help_button = Gtk.Button(label="How to Play")
        help_button.connect('clicked', self.__show_help_cb)
        toolbar_box.pack_start(help_button, False, False, 5)
        
        # Game variables
        self.numbers_on_board = []
        self.player_moves = 0
        self.bot_moves = 0
        self.current_turn = "Player"  # "Player" or "Bot"
        self.game_active = False
        self.selected_numbers = []
        
        # Create the main container
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.main_box.set_border_width(10)
        self.main_box.pack_start(toolbar_box, False, False, 5)
        self.add(self.main_box)
        
        # Create UI components
        self.__create_title_screen()
        self.__create_game_screen()
        
        # Initially show title screen
        self.__show_title_screen()
        # Don't return self (just finish initialization)
    
    def _apply_css(self):
        """Apply CSS styling to the activity."""
        css_provider = Gtk.CssProvider()
        css = """
        #euclid-game-window {
            background-image: linear-gradient(135deg, #f8fafc 0%, #e3f0ff 100%);
            border-radius: 18px;
            box-shadow: 0 6px 24px 0 rgba(60, 60, 120, 0.18);
            padding: 12px;
            color: #000;
        }
        .stat-frame {
            padding: 5px 0px 0px 0px;
            border-radius: 12px;
        }
        .stat-frame > * > * {
            background: linear-gradient(90deg, #f9f9f9 60%, #e3f0ff 100%);
            border-radius: 12px;
            padding: 8px 0 8px 0;
            color: #000;
        }
        .header-label {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            font-family: 'Sans', serif;
            color: #000;
        }
        .number-button {
            font-size: 18px;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
            background: linear-gradient(90deg, #f9f9f9 60%, #e3f0ff 100%);
        }
        .number-button:hover {
            background: linear-gradient(90deg, #e3f0ff 60%, #d1e3ff 100%);
        }
        .number-button.selected {
            background: linear-gradient(90deg, #4dabf7 60%, #3793dd 100%);
            color: white;
        }
        .game-status {
            font-size: 16px;
            font-weight: bold;
            color: #6a1b9a;
            background: linear-gradient(90deg, #fff8e1 60%, #f3e5f5 100%);
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px dashed #ba68c8;
            box-shadow: 0 2px 8px rgba(186,104,200,0.08);
            margin: 5px;
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def __create_title_screen(self):
        """Create the title screen UI components."""
        self.title_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.title_screen.set_halign(Gtk.Align.CENTER)
        self.title_screen.set_valign(Gtk.Align.CENTER)
        
        # Game title
        title_label = Gtk.Label()
        title_label.set_markup("<span weight='bold' foreground='#3E7D1C'>Euclid's Game</span>")
        title_label.get_style_context().add_class("header-label")
        self.title_screen.pack_start(title_label, False, False, 10)
        
        # Instructions in a frame with gradient background
        instructions_frame = Gtk.Frame()
        instructions_frame.get_style_context().add_class("stat-frame")
        
        instructions = Gtk.Label()
        instructions.set_markup(
            '<span size="large" weight="bold">How to play:</span>\n\n'
            '1. Start with two numbers on the board.\n'
            '2. Take turns with the computer to create new numbers.\n'
            '3. To create a new number, select two numbers and find their positive difference.\n'
            '4. The game ends when no new numbers can be created.\n'
            '5. The player who makes more moves wins!'
        )
        instructions.set_line_wrap(True)
        instructions.set_max_width_chars(40)
        instructions.set_margin_top(10)
        instructions.set_margin_bottom(10)
        instructions.set_margin_start(10)
        instructions.set_margin_end(10)
        instructions_frame.add(instructions)
        
        self.title_screen.pack_start(instructions_frame, False, False, 10)
        
        # Start button with modern style
        start_button = Gtk.Button.new_with_label("Start Game")
        start_button.connect("clicked", self.__start_game_cb)
        start_button.set_halign(Gtk.Align.CENTER)
        start_button.get_style_context().add_class("suggested-action")
        self.title_screen.pack_start(start_button, False, False, 10)

    def __create_game_screen(self):
        """Create the game screen UI components."""
        self.game_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Stats area with frames
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        stats_box.set_homogeneous(True)
        
        # Player moves frame
        player_frame = Gtk.Frame(label="Player Moves")
        player_frame.set_label_align(0.5, 0.5)
        player_frame.get_style_context().add_class("stat-frame")
        self.player_score_value = Gtk.Label(label="0")
        player_frame.add(self.player_score_value)
        stats_box.pack_start(player_frame, True, True, 5)
        
        # Bot moves frame
        bot_frame = Gtk.Frame(label="Bot Moves")
        bot_frame.set_label_align(0.5, 0.5)
        bot_frame.get_style_context().add_class("stat-frame")
        self.bot_score_value = Gtk.Label(label="0")
        bot_frame.add(self.bot_score_value)
        stats_box.pack_start(bot_frame, True, True, 5)
        
        self.game_screen.pack_start(stats_box, False, False, 5)
        
        # Current turn label with status styling
        self.turn_label = Gtk.Label()
        self.turn_label.set_markup('<span weight="bold">Current Turn: Player</span>')
        self.turn_label.get_style_context().add_class("game-status")
        self.game_screen.pack_start(self.turn_label, False, False, 5)
        
        # Numbers board with modern styling
        board_frame = Gtk.Frame()
        board_frame.get_style_context().add_class("stat-frame")
        
        self.numbers_grid = Gtk.Grid()
        self.numbers_grid.set_column_spacing(10)
        self.numbers_grid.set_row_spacing(10)
        self.numbers_grid.set_border_width(10)
        self.numbers_grid.set_halign(Gtk.Align.CENTER)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add(self.numbers_grid)
        scrolled.set_min_content_height(150)
        
        board_frame.add(scrolled)
        self.game_screen.pack_start(board_frame, True, True, 10)

        # Selection area
        selection_frame = Gtk.Frame(label="Make Your Move")
        selection_frame.get_style_context().add_class("stat-frame")
        
        selection_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        selection_box.set_border_width(15)
        
        # Selection status
        self.selection_status = Gtk.Label(label="Select first number...")
        selection_box.pack_start(self.selection_status, False, False, 5)
        
        # Number selection flow box
        self.selection_buttons_box = Gtk.FlowBox()
        self.selection_buttons_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.selection_buttons_box.set_max_children_per_line(6)
        self.selection_buttons_box.set_homogeneous(True)
        self.selection_buttons_box.set_halign(Gtk.Align.CENTER)
        selection_box.pack_start(self.selection_buttons_box, False, False, 5)
        
        # Selected numbers display
        selected_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        selected_box.set_halign(Gtk.Align.CENTER)
        
        self.first_number_label = Gtk.Label(label="?")
        self.first_number_label.get_style_context().add_class("number-button")
        
        minus_label = Gtk.Label(label="-")
        
        self.second_number_label = Gtk.Label(label="?")
        self.second_number_label.get_style_context().add_class("number-button")
        
        equals_label = Gtk.Label(label="=")
        
        self.result_label = Gtk.Label(label="?")
        self.result_label.get_style_context().add_class("number-button")
        
        selected_box.pack_start(self.first_number_label, False, False, 5)
        selected_box.pack_start(minus_label, False, False, 5)
        selected_box.pack_start(self.second_number_label, False, False, 5)
        selected_box.pack_start(equals_label, False, False, 5)
        selected_box.pack_start(self.result_label, False, False, 5)
        
        selection_box.pack_start(selected_box, False, False, 10)
        
        # Action buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        buttons_box.set_halign(Gtk.Align.CENTER)
        
        self.create_button = Gtk.Button.new_with_label("Create Number")
        self.create_button.connect("clicked", self.__create_number_cb)
        self.create_button.set_sensitive(False)
        self.create_button.get_style_context().add_class("suggested-action")
        buttons_box.pack_start(self.create_button, False, False, 5)
        
        clear_button = Gtk.Button.new_with_label("Clear Selection")
        clear_button.connect("clicked", self.__clear_selection_cb)
        buttons_box.pack_start(clear_button, False, False, 5)
        
        selection_box.pack_start(buttons_box, False, False, 5)
        
        # Status message
        self.status_label = Gtk.Label()
        self.status_label.set_line_wrap(True)
        selection_box.pack_start(self.status_label, False, False, 10)
        
        selection_frame.add(selection_box)
        self.game_screen.pack_start(selection_frame, False, False, 10)
    
    def __show_title_screen(self):
        """Show the title screen and hide the game screen."""
        # Remove game screen if it exists in the container
        if self.game_screen in self.main_box.get_children():
            self.main_box.remove(self.game_screen)
        
        # Add title screen if it's not already there
        if self.title_screen not in self.main_box.get_children():
            self.main_box.pack_start(self.title_screen, True, True, 0)
            self.title_screen.show_all()
    
    def __show_game_screen(self):
        """Show the game screen and hide the title screen."""
        # Remove title screen if it exists in the container
        if self.title_screen in self.main_box.get_children():
            self.main_box.remove(self.title_screen)
        
        # Add game screen if it's not already there
        if self.game_screen not in self.main_box.get_children():
            self.main_box.pack_start(self.game_screen, True, True, 0)
            self.game_screen.show_all()
    
    def __start_game_cb(self, button):
        """Callback when the Start Game button is clicked."""
        self.__start_new_game()
        self.__show_game_screen()
    
    def __restart_game_cb(self, button):
        """Callback when the Restart Game button is clicked."""
        self.__start_new_game()
        self.__show_game_screen()
    
    def __show_help_cb(self, button):
        """Show help dialog when the Help button is clicked."""
        help_text = (
            "1. Select two numbers from the board.\n"
            "2. Click 'Create Number' to find their positive difference.\n"
            "3. If the difference is not already on the board, it will be added.\n"
            "4. Take turns with the bot until no more valid moves remain.\n"
            "5. The player who makes more moves wins!"
        )
        
        # Create and show help instructions
        try:
            # Check if running in standalone mode
            standalone = not isinstance(self, sugar3.activity.activity.Activity)
            
            if standalone or not hasattr(sugar3.activity.activity.Activity, 'add_alert'):
                # Standalone mode - use a simple Gtk dialog
                dialog = Gtk.MessageDialog(
                    transient_for=self,
                    modal=True,
                    message_type=Gtk.MessageType.INFO,
                    buttons=Gtk.ButtonsType.OK,
                    text="How to Play Euclid's Game"
                )
                dialog.format_secondary_text(help_text)
                dialog.run()
                dialog.destroy()
            else:
                # Sugar mode - use Alert
                alert = Alert()
                alert.props.title = "How to Play Euclid's Game"
                alert.props.msg = help_text
                alert.add_button(Gtk.ResponseType.OK, "OK")
                alert.connect('response', self.__help_alert_cb)
                
                # Show the alert
                box = self.get_canvas()
                if box is not None:
                    box.pack_start(alert, False, False, 0)
                    alert.show_all()
                    self._alerts.append(alert)  # Store reference to alert
        except Exception as e:
            # If all else fails, show a simple dialog
            print(f"Error showing help: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text="How to Play Euclid's Game"
            )
            dialog.format_secondary_text(help_text)
            dialog.run()
            dialog.destroy()

    def __help_alert_cb(self, alert, response_id):
        """Callback for the help alert response."""
        try:
            if alert.get_parent() is not None:
                alert.get_parent().remove(alert)
            if alert in self._alerts:
                self._alerts.remove(alert)
        except Exception as e:
            print(f"Error removing help alert: {e}")
    
    def __clear_selection_cb(self, button):
        """Clear the current number selection."""
        # Reset selection state
        self.first_selected_number = None
        self.second_selected_number = None
        self.selected_numbers = []
        
        # Clear displayed values
        self.first_number_label.set_text("?")
        self.second_number_label.set_text("?")
        self.result_label.set_text("?")
        
        # Reset button states
        for child in self.selection_buttons_box.get_children():
            button_widget = child.get_child()
            style_context = button_widget.get_style_context()
            style_context.remove_class('first-selected')
            style_context.remove_class('second-selected')
        
        # Update status
        self.selection_status.set_text("Select first number...")
        self.create_button.set_sensitive(False)
    
    def __start_new_game(self):
        """Initialize a new game."""
        # Clear previous game state
        self.numbers_on_board = []
        self.player_moves = 0
        self.bot_moves = 0
        self.selected_numbers = []
        self.first_selected_number = None
        self.second_selected_number = None
        self.game_active = True
        
        # Update UI
        self.player_score_value.set_text("0")
        self.bot_score_value.set_text("0")
        self.first_number_label.set_text("?")
        self.second_number_label.set_text("?")
        self.result_label.set_text("?")
        self.selection_status.set_text("Select first number...")
        self.create_button.set_sensitive(False)
        
        # Clear the numbers board
        for child in self.numbers_grid.get_children():
            self.numbers_grid.remove(child)
        
        # Generate two random starting numbers
        num1 = random.randint(10, 50)
        num2 = random.randint(60, 100)
        
        # Make sure the numbers are different
        while num1 == num2:
            num2 = random.randint(60, 100)
        
        # Add the starting numbers to the board
        self.__add_number_to_board(num1)
        self.__add_number_to_board(num2)
        
        # Set player's turn
        self.current_turn = "Player"
        self.__update_turn_label()
        
        self.status_label.set_text("Game started! Select two numbers to find their difference.")
    
    def __add_number_to_board(self, number):
        """Add a new number to the game board."""
        if number in self.numbers_on_board:
            return False
        
        self.numbers_on_board.append(number)
        self.numbers_on_board.sort()  # Keep numbers sorted for easier viewing
        
        # Refresh the numbers board UI
        self.__refresh_numbers_board()
        
        return True
    
    def __refresh_numbers_board(self):
        """Refresh the numbers shown on the board."""
        # Clear existing numbers from the grid
        for child in self.numbers_grid.get_children():
            self.numbers_grid.remove(child)
        
        # Clear selection buttons
        for child in self.selection_buttons_box.get_children():
            self.selection_buttons_box.remove(child)
        
        # Add buttons in a grid layout (up to 6 per row)
        max_columns = 6
        for i, number in enumerate(self.numbers_on_board):
            row = i // max_columns
            col = i % max_columns
            
            button = Gtk.Button.new_with_label(str(number))
            button.get_style_context().add_class('number-button')
            button.set_size_request(60, 60)
            self.numbers_grid.attach(button, col, row, 1, 1)
            
            # Also create selection buttons
            select_button = Gtk.Button.new_with_label(str(number))
            select_button.get_style_context().add_class('selection-button')
            select_button.set_size_request(70, 50)
            select_button.connect("clicked", self.__number_button_clicked, number)
            self.selection_buttons_box.add(select_button)
        
        # Initialize selection state
        self.first_selected_number = None
        self.second_selected_number = None
        
        # Show all widgets
        self.numbers_grid.show_all()
        self.selection_buttons_box.show_all()
    
    def __number_button_clicked(self, button, number):
        """Handle direct number button clicks."""
        if not self.game_active or self.current_turn != "Player":
            return
        
        if self.first_selected_number is None:
            # First selection
            self.first_selected_number = number
            self.first_number_label.set_text(str(number))
            self.selection_status.set_text("Select second number...")
            # Highlight the selected button
            button.get_style_context().add_class('first-selected')
        elif self.second_selected_number is None:
            # Second selection
            if number == self.first_selected_number:
                self.status_label.set_text("Please select a different number")
                return
            
            self.second_selected_number = number
            self.selected_numbers = [self.first_selected_number, self.second_selected_number]
            
            # Update the display
            larger = max(self.selected_numbers)
            smaller = min(self.selected_numbers)
            self.first_number_label.set_text(str(larger))
            self.second_number_label.set_text(str(smaller))
            
            # Calculate the difference
            difference = larger - smaller
            self.result_label.set_text(str(difference))
            
            # Update selection status
            self.selection_status.set_text(f"Difference: {larger} - {smaller} = {difference}")
            
            # Highlight the selected button
            button.get_style_context().add_class('second-selected')
            
            # Enable the create button
            self.create_button.set_sensitive(True)
    
    def __create_number_cb(self, button):
        """Create a new number when the player clicks the Create Number button."""
        if not self.game_active or not self.selected_numbers or len(self.selected_numbers) != 2:
            return
        
        # Calculate the difference
        bigger = max(self.selected_numbers)
        smaller = min(self.selected_numbers)
        difference = bigger - smaller
        
        # Check if the difference is already on the board
        if difference in self.numbers_on_board:
            self.status_label.set_text(f"The number {difference} is already on the board. Try again!")
            return
        
        # Check if the difference is 0
        if difference == 0:
            self.status_label.set_text("The difference is 0, which is not a valid move. Try again!")
            return
        
        # Add the new number to the board
        self.__add_number_to_board(difference)
        
        # Update player's score
        self.player_moves += 1
        self.player_score_value.set_text(str(self.player_moves))
        
        # Clear selections
        self.__clear_selection_cb(None)
        
        # Set status message
        self.status_label.set_text(f"Added {difference} to the board!")
        
        # Check if game continues
        if self.__check_game_over():
            self.__end_game()
            return
        
        # Switch to bot's turn
        self.current_turn = "Bot"
        self.__update_turn_label()
        
        # Give bot time to think
        GLib.timeout_add(1500, self.__bot_turn)
    
    def __bot_turn(self):
        """Handle the bot's turn."""
        if not self.game_active or self.current_turn != "Bot":
            return False
        
        self.status_label.set_text("Bot is thinking...")
        
        # Let the UI update before the bot's move
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Wait a moment to make the bot seem like it's thinking
        GLib.timeout_add(1000, self.__bot_make_move)
        return False  # Don't repeat this timeout
    
    def __find_valid_bot_move(self):
        """Find a valid move for the bot."""
        # Get all possible pairs of numbers
        possible_pairs = []
        for i in range(len(self.numbers_on_board)):
            for j in range(i + 1, len(self.numbers_on_board)):
                num1 = self.numbers_on_board[i]
                num2 = self.numbers_on_board[j]
                difference = abs(num1 - num2)
                
                # Check if the difference is valid (not already on board and not 0)
                if difference > 0 and difference not in self.numbers_on_board:
                    possible_pairs.append((num1, num2, difference))
        
        # If there are valid moves, randomly select one
        if possible_pairs:
            return random.choice(possible_pairs)
        
        # No valid moves found
        return None
    
    def __bot_make_move(self):
        """Bot makes a move by selecting two numbers."""
        # Find a valid move
        move = self.__find_valid_bot_move()
        
        if move:
            num1, num2, difference = move
            
            # Update UI to show the bot's selection
            self.first_number_label.set_text(str(max(num1, num2)))
            self.second_number_label.set_text(str(min(num1, num2)))
            self.result_label.set_text(str(difference))
            
            # Add the new number to the board
            self.__add_number_to_board(difference)
            
            # Update bot's score
            self.bot_moves += 1
            self.bot_score_value.set_text(str(self.bot_moves))
            
            # Set status message
            self.status_label.set_text(f"Bot created {difference} by finding the difference between {max(num1, num2)} and {min(num1, num2)}!")
            
            # Check if game continues
            if self.__check_game_over():
                self.__end_game()
                return False
            
            # Switch back to player's turn
            self.current_turn = "Player"
            self.__update_turn_label()
            
            # Reset selection labels
            GLib.timeout_add(1500, self.__reset_selection_labels)
        else:
            # No valid moves found, end the game
            self.__end_game()
        
        return False  # Don't repeat this timeout
    
    def __reset_selection_labels(self):
        """Reset the selection labels after the bot's turn."""
        self.__clear_selection_cb(None)
        self.selection_status.set_text("Your turn! Select first number...")
        self.status_label.set_text("Your turn! Select two numbers to find their difference.")
        return False  # Don't repeat this timeout
    
    def __check_game_over(self):
        """Check if the game is over (no more valid moves possible)."""
        # Check all possible combinations of numbers on the board
        for i in range(len(self.numbers_on_board)):
            for j in range(i + 1, len(self.numbers_on_board)):
                num1 = self.numbers_on_board[i]
                num2 = self.numbers_on_board[j]
                difference = abs(num1 - num2)
                
                # If a valid move exists, game is not over
                if difference > 0 and difference not in self.numbers_on_board:
                    return False
        
        # No valid moves found, game is over
        return True
    
    def __update_turn_label(self):
        """Update the turn label to show whose turn it is."""
        if self.current_turn == "Player":
            self.turn_label.set_markup('<span size="large" weight="bold" color="blue">Current Turn: Player</span>')
        else:
            self.turn_label.set_markup('<span size="large" weight="bold" color="red">Current Turn: Bot</span>')
    
    def __end_game(self):
        """End the game and show the results."""
        self.game_active = False
        
        # Clear the board selection
        self.__clear_selection_cb(None)  # Use our existing clear method instead
        self.create_button.set_sensitive(False)
        
        # Determine the winner
        if self.player_moves > self.bot_moves:
            message = f"Game over! You win! Score: Player {self.player_moves} - Bot {self.bot_moves}"
        elif self.bot_moves > self.player_moves:
            message = f"Game over! Bot wins! Score: Player {self.player_moves} - Bot {self.bot_moves}"
        else:
            message = f"Game over! It's a tie! Score: Player {self.player_moves} - Bot {self.bot_moves}"
        
        # Show game over message
        self.status_label.set_text(message)
        self.turn_label.set_markup('<span size="large" weight="bold" color="purple">Game Over!</span>')
        
        # Create and show alert for game results
        if isinstance(self, Gtk.Window) and not isinstance(self, sugar3.activity.activity.Activity):
            # Standalone mode
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text="Game Over"
            )
            dialog.format_secondary_text(message)
            dialog.set_response_sensitive(Gtk.ResponseType.OK, True)
            dialog.set_default_response(Gtk.ResponseType.OK)
            # Change OK button to "Play Again"
            ok_button = dialog.get_widget_for_response(Gtk.ResponseType.OK)
            if ok_button:
                ok_button.set_label("Play Again")
            
            response = dialog.run()
            dialog.destroy()
            
            # If "Play Again" was clicked
            if response == Gtk.ResponseType.OK:
                self.__start_new_game()
        else:
            # Sugar mode
            alert = Alert()
            alert.props.title = "Game Over"
            alert.props.msg = message
            
            # Add restart button
            restart_button = alert.add_button(Gtk.ResponseType.APPLY, "Play Again")
            alert.add_button(Gtk.ResponseType.OK, "OK")
            alert.connect('response', self.__game_over_alert_cb)
            
            # Show the alert
            self.add_alert(alert)
            alert.show_all()
    
    def add_alert(self, alert):
        """Add an alert - compatibility method for standalone mode."""
        if not hasattr(self, '_alerts'):
            self._alerts = []
            
        if isinstance(self, Gtk.Window) and not isinstance(self, sugar3.activity.activity.Activity):
            # We're in standalone mode
            dialog = Gtk.Dialog(parent=self)
            dialog.set_title(alert.props.title)
            dialog.set_modal(True)
            
            content_area = dialog.get_content_area()
            content_area.set_border_width(15)
            
            # Add message
            label = Gtk.Label(label=alert.props.msg)
            label.set_line_wrap(True)
            content_area.add(label)
            
            # Store response callback if exists
            if hasattr(alert, 'connect'):
                response_cb = None
                for signal_id, callback in alert.list_signal_handlers():
                    if signal_id == 'response':
                        response_cb = callback
                        break
            else:
                response_cb = getattr(alert, '_response_cb', None)
            
            # Add buttons from alert
            buttons = getattr(alert, '_buttons', [(Gtk.ResponseType.OK, "OK")])
            for response_id, button_label in buttons:
                dialog.add_button(button_label, response_id)
            
            dialog.show_all()
            response = dialog.run()
            dialog.destroy()
            
            # Call the response callback if it exists
            if response_cb:
                response_cb(alert, response)
        else:
            # We're in Sugar mode
            # First ensure the _alerts attribute exists
            if not hasattr(self, '_alerts'):
                self._alerts = []
            self._alerts.append(alert)
            
            # Show the alert
            box = self.get_canvas()
            if box is not None:
                toolbar = self.get_toolbar_box()
                if toolbar is not None:
                    toolbar_height = toolbar.get_allocation().height
                else:
                    toolbar_height = 0
                    
                alert.connect('response', self.__alert_response_cb)
                box.pack_start(alert, False, False, 0)
                alert.show()
                
                if hasattr(self, 'get_allocation'):
                    width = self.get_allocation().width
                    height = self.get_allocation().height - toolbar_height
                    alert.size_allocate(Gdk.Rectangle(0, 0, width, height))
    
    def __alert_response_cb(self, alert, response_id):
        """Handle alert response."""
        self.remove_alert(alert)
    
    def remove_alert(self, alert):
        """Remove an alert - compatibility method for standalone mode."""
        if not hasattr(self, '_alerts'):
            return
            
        if isinstance(self, Gtk.Window) and not isinstance(self, sugar3.activity.activity.Activity):
            # In standalone mode, nothing to do - dialog is already destroyed
            if alert in self._alerts:
                self._alerts.remove(alert)
        else:
            # We're in Sugar mode
            if alert in self._alerts:
                self._alerts.remove(alert)
                if alert.get_parent() is not None:
                    alert.get_parent().remove(alert)


# This allows the activity to be launched from the command line
if __name__ == '__main__':
    win = EuclidsGameActivity(None)
    win.show_all()
    Gtk.main()
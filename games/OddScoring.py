#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Odd Scoring - A Sugar Activity
A 1D grid-based game where the player who makes an even number of moves wins.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gdk
import random
import os
from sugar3.activity import activity
from sugar3.graphics.style import GRID_CELL_SIZE
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.activity.widgets import StopButton


class OddScoringActivity(activity.Activity):
    """Main activity class for the Odd Scoring game."""
    
    def __init__(self, handle):
        """Initialize the activity."""
        # Check if running as standalone or within Sugar
        self.running_as_standalone = handle is None
        
        if self.running_as_standalone:
            # Standalone initialization (without Sugar)
            Gtk.Window.__init__(self)
            self.set_default_size(800, 600)
            self.set_title("Odd Scoring")
            self.connect("delete-event", Gtk.main_quit)
        else:
            # Initialize as Sugar activity
            activity.Activity.__init__(self, handle)
            self.set_title("Odd Scoring")
        
        # Apply CSS styling
        self._apply_css()
        
        # Create toolbar
        if self.running_as_standalone:
            # Simple toolbar for standalone
            toolbar_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.main_box.pack_start(toolbar_box, False, False, 0)
        else:
            # Sugar toolbar
            toolbar_box = ToolbarBox()
            self.set_toolbar_box(toolbar_box)
            toolbar_box.show()
            
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, -1)
            activity_button.show()
            
            separator = Gtk.SeparatorToolItem()
            separator.props.draw = False
            separator.set_expand(True)
            toolbar_box.toolbar.insert(separator, -1)
            separator.show()
            
            stop_button = StopButton(self)
            toolbar_box.toolbar.insert(stop_button, -1)
            stop_button.show()
            
            # Main container
            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            self.main_box.set_border_width(10)
            self.main_box.set_name("odd-scoring-window")
            self.set_canvas(self.main_box)
        
        # Game variables - ensure N is always odd
        self.N = 15  # Default value, always odd
        if self.N % 2 == 0:
            self.N += 1  # Make it odd if it's not
        self.chip_position = self.N  # Starting position
        self.human_moves = 0
        self.computer_moves = 0
        self.game_over = False
        self.cell_buttons = []
        
        # Create and show title screen
        self.show_title_screen()
        
        # If standalone, add main_box to window
        if self.running_as_standalone:
            self.add(self.main_box)
        
        self.show_all()
    
    def _apply_css(self):
        """Apply CSS styling to widgets."""
        css_provider = Gtk.CssProvider()
        css = """
        #odd-scoring-window {
            background-image: linear-gradient(135deg, #f8fafc 0%, #e3f0ff 100%);
            border-radius: 32px;
            box-shadow: 0 8px 32px 0 rgba(60, 60, 120, 0.18), 0 1.5px 8px 0 rgba(60, 60, 120, 0.10);
            padding: 32px;
            color: #000;
        }
        .even-cell {
            background-color: #a0d0ff;
            border-radius: 8px;
            font-weight: bold;
            color: #2c3e50;
            transition: all 0.3s ease;
        }
        .odd-cell {
            background-color: #ffe0a0;
            border-radius: 8px;
            font-weight: bold;
            color: #2c3e50;
            transition: all 0.3s ease;
        }
        .chip-position {
            background-color: #ff7e79;
            font-weight: bold;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .move-button {
            background-image: linear-gradient(135deg, #6e8efb 0%, #a777e3 100%);
            border-radius: 12px;
            color: white;
            font-weight: bold;
            padding: 10px;
            transition: all 0.3s ease;
        }
        .move-button:hover {
            background-image: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            color: #6e8efb;
            /* Removed the transform property that was causing the error */
        }
        .header-label {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 16px;
            font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
            color: #3E7D1C;
        }
        .stat-frame {
            padding: 12px 0px 0px 0px;
            border-radius: 18px;
        }
        .stat-frame > * > * {
            background: linear-gradient(90deg, #f9f9f9 60%, #e3f0ff 100%);
            border-radius: 22px;
            padding: 18px 0 18px 0;
            color: #000;
        }
        .stat-label {
            font-size: 22px;
            font-weight: bold;
            color: #000;
        }
        .rule-label {
            font-size: 22px;
            font-weight: bold;
            color: #6a1b9a;
            background: linear-gradient(90deg, #fff8e1 60%, #f3e5f5 100%);
            padding: 14px 18px;
            border-radius: 14px;
            border: 2px dashed #ba68c8;
            box-shadow: 0 2px 8px rgba(186,104,200,0.08);
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
        """
        css_provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def show_title_screen(self):
        """Create and display the title screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Title label
        title_label = Gtk.Label()
        title_label.set_markup("<span size='xx-large' weight='bold'>Odd Scoring</span>")
        title_label.get_style_context().add_class("header-label")
        title_label.set_margin_top(30)
        title_label.set_margin_bottom(20)
        self.main_box.pack_start(title_label, False, False, 0)
        
        # Instructions
        instructions = Gtk.Label()
        instructions_text = (
            "Welcome to Odd Scoring!\n\n"
            "How to play:\n"
            "• Move the chip left by 1, 2, or 3 steps on your turn\n"
            "• The chip starts at position " + str(self.N) + "\n"
            "• The player who makes an EVEN number of moves wins\n"
            "• You play first, then the computer\n"
            "• Game ends when the chip reaches position 1"
        )
        instructions.set_text(instructions_text)
        instructions.set_line_wrap(True)
        instructions.get_style_context().add_class("rule-label")
        instructions.set_margin_bottom(30)
        
        # Add instructions in a container for better styling
        instruction_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        instruction_container.pack_start(instructions, True, True, 0)
        instruction_container.set_margin_start(50)
        instruction_container.set_margin_end(50)
        
        self.main_box.pack_start(instruction_container, False, False, 0)
        
        # Start game button
        start_button = Gtk.Button(label="Start Game")
        start_button.connect("clicked", self.on_start_game)
        start_button.set_size_request(200, 50)
        start_button.get_style_context().add_class("move-button")
        
        # Center the button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        button_box.pack_start(start_button, False, False, 0)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        
        self.main_box.pack_start(button_box, False, False, 0)
        self.main_box.show_all()
    
    def on_start_game(self, button):
        """Start a new game when the Start Game button is clicked."""
        # Reset game state
        self.chip_position = self.N
        self.human_moves = 0
        self.computer_moves = 0
        self.game_over = False
        
        # Switch to game screen
        self.show_game_screen()
    
    def show_game_screen(self):
        """Create and display the game screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Top bar with frames for stats
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        top_bar.set_hexpand(True)
        top_bar.set_vexpand(False)
        top_bar.set_homogeneous(True)
        
        # Your moves frame
        human_moves_frame = Gtk.Frame(label="Your Moves")
        human_moves_frame.set_label_align(0.5, 0.5)
        human_moves_frame.set_hexpand(True)
        human_moves_frame.set_vexpand(True)
        human_moves_frame.get_style_context().add_class("stat-frame")
        self.human_moves_label = Gtk.Label(label="0")
        self.human_moves_label.get_style_context().add_class("stat-label")
        human_moves_frame.add(self.human_moves_label)
        top_bar.pack_start(human_moves_frame, True, True, 0)
        
        # Game status frame
        status_frame = Gtk.Frame(label="Status")
        status_frame.set_label_align(0.5, 0.5)
        status_frame.set_hexpand(True)
        status_frame.set_vexpand(True)
        status_frame.get_style_context().add_class("stat-frame")
        self.status_label = Gtk.Label(label="Your Turn")
        self.status_label.get_style_context().add_class("stat-label")
        status_frame.add(self.status_label)
        top_bar.pack_start(status_frame, True, True, 0)
        
        # Computer moves frame
        computer_moves_frame = Gtk.Frame(label="Computer Moves")
        computer_moves_frame.set_label_align(0.5, 0.5)
        computer_moves_frame.set_hexpand(True)
        computer_moves_frame.set_vexpand(True)
        computer_moves_frame.get_style_context().add_class("stat-frame")
        self.computer_moves_label = Gtk.Label(label="0")
        self.computer_moves_label.get_style_context().add_class("stat-label")
        computer_moves_frame.add(self.computer_moves_label)
        top_bar.pack_start(computer_moves_frame, True, True, 0)
        
        self.main_box.pack_start(top_bar, False, False, 10)
        
        # Visual representation of the game board
        board_frame = Gtk.Frame()
        board_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.board_label = Gtk.Label()
        self.board_label.set_markup("<span font='monospace 18'></span>")
        self.update_board_visual()
        board_frame.add(self.board_label)
        
        board_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        board_container.pack_start(board_frame, True, True, 0)
        board_container.set_margin_top(20)
        board_container.set_margin_bottom(20)
        
        self.main_box.pack_start(board_container, False, False, 0)
        
        # Game grid
        grid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        grid_box.set_margin_start(30)
        grid_box.set_margin_end(30)
        self.cell_buttons = []
        
        for i in range(1, self.N + 1):
            cell = Gtk.Button()
            cell.set_size_request(45, 45)
            cell.set_label(str(i))
            
            # Set different background for even and odd cells
            context = cell.get_style_context()
            if i % 2 == 0:
                context.add_class("even-cell")
            else:
                context.add_class("odd-cell")
            
            self.cell_buttons.append(cell)
            grid_box.pack_start(cell, True, True, 3)
        
        self.main_box.pack_start(grid_box, False, False, 10)
        
        # Game rules reminder
        rules_reminder = Gtk.Label()
        rules_reminder.set_text("Remember: The player who makes an EVEN number of moves wins!")
        rules_reminder.get_style_context().add_class("rule-label")
        rules_reminder.set_margin_top(20)
        rules_reminder.set_margin_bottom(20)
        self.main_box.pack_start(rules_reminder, False, False, 0)
        
        # Move buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.move_buttons = []  # Store references to the move buttons
        
        for move in range(1, 4):
            move_button = Gtk.Button(label=f"Move {move}")
            move_button.get_style_context().add_class("move-button")
            move_button.connect("clicked", self.on_move_clicked, move)
            buttons_box.pack_start(move_button, True, True, 0)
            self.move_buttons.append(move_button)  # Add to the list for easy access
            
        # Center the buttons
        centering_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        centering_box.pack_start(Gtk.Label(label=""), True, True, 0)
        centering_box.pack_start(buttons_box, False, False, 0)
        centering_box.pack_start(Gtk.Label(label=""), True, True, 0)
        
        self.main_box.pack_start(centering_box, False, False, 20)
        
        # Update the UI to show initial chip position
        self.update_game_ui()
        self.main_box.show_all()
    
    def apply_css(self):
        """Apply CSS styling to widgets."""
        css_provider = Gtk.CssProvider()
        css = """
        .even-cell {
            background-color: #a0d0ff;
        }
        .odd-cell {
            background-color: #ffe0a0;
        }
        .chip-position {
            background-color: #ff8080;
            font-weight: bold;
        }
        """
        css_provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def update_board_visual(self):
        """Update the visual representation of the board."""
        board = "|"
        for i in range(1, self.N + 1):
            if i == self.chip_position:
                board += " <span foreground='red' weight='bold'>C</span>"
            else:
                board += " <span foreground='gray'>-</span>"
        board += " |"
        self.board_label.set_markup(f"<span font='monospace 18'>{board}</span>")
    
    def update_game_ui(self):
        """Update the UI to reflect the current game state."""
        # Update move counts
        self.human_moves_label.set_text(f"{self.human_moves}")
        self.computer_moves_label.set_text(f"{self.computer_moves}")
        
        # Update visual board representation
        if hasattr(self, 'board_label'):
            self.update_board_visual()
        
        # Update cell appearance
        for i, button in enumerate(self.cell_buttons):
            cell_num = i + 1
            context = button.get_style_context()
            
            # Remove chip position class from all cells
            if context.has_class("chip-position"):
                context.remove_class("chip-position")
            
            # Add chip position class to current cell
            if cell_num == self.chip_position:
                button.set_label("C")
                context.add_class("chip-position")
            else:
                button.set_label(str(cell_num))
        
        # Disable invalid move buttons using the stored references
        if hasattr(self, 'move_buttons'):
            for i, move in enumerate(range(1, 4)):
                # Disable button if the move would go past cell 1
                if self.chip_position - move < 1:
                    self.move_buttons[i].set_sensitive(False)
                else:
                    self.move_buttons[i].set_sensitive(not self.game_over)

    def on_move_clicked(self, button, move):
        """Handle player's move."""
        if self.game_over:
            return
        
        # Update chip position
        self.chip_position -= move
        self.human_moves += 1
        
        # Update UI
        self.status_label.set_markup("<span size='large' weight='bold'>Computer's Turn</span>")
        self.update_game_ui()
        
        # Check if game over
        if self.chip_position == 1:
            self.end_game()
            return
        
        # Disable buttons during computer's turn
        if hasattr(self, 'move_buttons'):
            for button in self.move_buttons:
                button.set_sensitive(False)
        
        # Computer's turn after delay
        GLib.timeout_add(1000, self.computer_move)
    
    def computer_move(self):
        """Execute computer's move."""
        if self.game_over:
            return False
        
        # Determine valid moves
        valid_moves = [i for i in range(1, 4) if self.chip_position - i >= 1]
        
        if not valid_moves:
            self.end_game()
            return False
        
        # Enhanced strategy based on number theory and the win condition
        # The key insight: with optimal play, the player who gets to position 1+4n first will win
        if self.chip_position == 2:
            # Must move to 1 and lose if this is the only option
            move = 1
        elif self.chip_position == 3:
            # Must move to position 1 or 2
            move = 1 if (self.human_moves % 2 == 0) else 2
        elif self.chip_position == 4:
            # Must move to position 1, 2, or 3
            if self.human_moves % 2 == 0:  # Try to make human have odd moves
                move = 3  # Move to position 1
            else:
                move = 2  # Move to position 2
        else:
            # Calculate the target position that guarantees a win if possible
            remainder = (self.chip_position - 1) % 4
            
            if remainder == 0:
                # Already at a winning position, move 1 to maintain advantage
                move = 1
            elif remainder == 1:
                # Need to move 2 to reach a winning position
                move = 2 if 2 in valid_moves else valid_moves[0]
            elif remainder == 2:
                # Need to move 3 to reach a winning position
                move = 3 if 3 in valid_moves else valid_moves[0]
            else:  # remainder == 3
                # Need to move 4 to reach a winning position, but max is 3
                # So move 3 and hope for human error
                move = 3 if 3 in valid_moves else valid_moves[0]
        
        # Update chip position
        self.chip_position -= move
        self.computer_moves += 1
        
        # Update UI
        self.status_label.set_markup("<span size='large' weight='bold'>Your Turn</span>")
        self.update_game_ui()
        
        # Check if game over
        if self.chip_position == 1:
            self.end_game()
            return False
        
        # Re-enable buttons for player's turn
        if hasattr(self, 'move_buttons'):
            for i, button in enumerate(self.move_buttons):
                move = i + 1
                if self.chip_position - move >= 1:
                    button.set_sensitive(True)
        
        return False
    
    def end_game(self):
        """End the game and show the results."""
        self.game_over = True
        
        # Determine winner
        if self.human_moves % 2 == 0:
            winner = "You Win!"
            message = "You made an even number of moves!"
        else:
            winner = "Computer Wins!"
            message = "Computer made an even number of moves!"
        
        # Show end screen
        self.show_end_screen(winner, message)
    
    def show_end_screen(self, winner, message):
        """Display the end game screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Winner announcement
        winner_label = Gtk.Label()
        winner_label.set_markup(f"<span size='xx-large' weight='bold'>{winner}</span>")
        winner_label.get_style_context().add_class("header-label")
        winner_label.set_margin_top(30)
        winner_label.set_margin_bottom(10)
        self.main_box.pack_start(winner_label, False, False, 0)
        
        # Result message
        result_label = Gtk.Label(label=message)
        if "You Win" in winner:
            result_label.get_style_context().add_class("success-text")
        else:
            result_label.get_style_context().add_class("failure-text")
        result_label.set_margin_bottom(20)
        self.main_box.pack_start(result_label, False, False, 0)
        
        # Final board position
        final_board = Gtk.Label()
        board_text = "| C" + " -" * (self.N - 1) + " |"
        final_board.set_markup(f"<span font='monospace 16'>Final position: {board_text}</span>")
        self.main_box.pack_start(final_board, False, False, 10)
        
        # Move counts in frames like the game screen
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stats_box.set_homogeneous(True)
        
        # Your moves frame
        human_frame = Gtk.Frame(label="Your Moves")
        human_frame.set_label_align(0.5, 0.5)
        human_frame.get_style_context().add_class("stat-frame")
        human_label = Gtk.Label(label=f"{self.human_moves} ({'even' if self.human_moves%2==0 else 'odd'})")
        human_label.get_style_context().add_class("stat-label")
        human_frame.add(human_label)
        stats_box.pack_start(human_frame, True, True, 0)
        
        # Computer moves frame
        comp_frame = Gtk.Frame(label="Computer Moves")
        comp_frame.set_label_align(0.5, 0.5)
        comp_frame.get_style_context().add_class("stat-frame")
        comp_label = Gtk.Label(label=f"{self.computer_moves} ({'even' if self.computer_moves%2==0 else 'odd'})")
        comp_label.get_style_context().add_class("stat-label")
        comp_frame.add(comp_label)
        stats_box.pack_start(comp_frame, True, True, 0)
        
        # Total moves frame
        total_frame = Gtk.Frame(label="Total Moves")
        total_frame.set_label_align(0.5, 0.5)
        total_frame.get_style_context().add_class("stat-frame")
        total_label = Gtk.Label(label=f"{self.human_moves + self.computer_moves}")
        total_label.get_style_context().add_class("stat-label")
        total_frame.add(total_label)
        stats_box.pack_start(total_frame, True, True, 0)
        
        self.main_box.pack_start(stats_box, False, False, 20)
        
        # Explanation of the win condition
        explanation = Gtk.Label()
        explanation.set_text("Remember: The player who makes an even number of moves wins!")
        explanation.get_style_context().add_class("rule-label")
        explanation.set_margin_top(10)
        explanation.set_margin_bottom(20)
        self.main_box.pack_start(explanation, False, False, 0)
        
        # Play again button
        play_again_button = Gtk.Button(label="Play Again")
        play_again_button.get_style_context().add_class("move-button")
        play_again_button.connect("clicked", self.on_start_game)
        play_again_button.set_size_request(200, 50)
        
        # Center the button
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        button_box.pack_start(play_again_button, False, False, 0)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        
        self.main_box.pack_start(button_box, False, False, 20)
        self.main_box.show_all()


# To make the activity discoverable by Sugar
def main():
    # Create an instance and start the main loop
    win = OddScoringActivity(None)
    Gtk.main()

if __name__ == '__main__':
    main()
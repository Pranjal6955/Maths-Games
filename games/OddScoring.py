#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Math Challenges - A Sugar Activity
A game with two modes: Sum to Target and Countdown to Zero
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
    """Main activity class for the Math Challenges game."""
    
    def __init__(self, handle):
        """Initialize the activity."""
        # Check if running as standalone or within Sugar
        self.running_as_standalone = handle is None
        
        if self.running_as_standalone:
            # Standalone initialization (without Sugar)
            Gtk.Window.__init__(self)
            self.set_default_size(800, 600)
            self.set_title("Math Challenges")
            self.connect("delete-event", Gtk.main_quit)
        else:
            # Initialize as Sugar activity
            activity.Activity.__init__(self, handle)
            self.set_title("Math Challenges")
        
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
            self.main_box.set_name("math-challenges-window")
            self.set_canvas(self.main_box)
        
        # Game variables
        self.target_sum = 21  # Target sum to reach
        self.current_sum = 0  # Running sum starts at 0
        self.human_moves = 0
        self.computer_moves = 0
        self.game_over = False
        self.game_mode = "sum"  # Default mode: "sum" or "countdown"
        self.difficulty = "normal"  # Default difficulty: "easy", "normal", "hard"
        
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
        #math-challenges-window {
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
            box-shadow: 0 2px 8px rgba(3, 169, 244, 0.3);
        }
        .odd-cell {
            background-color: #ffe0a0;
            border-radius: 8px;
            font-weight: bold;
            color: #2c3e50;
            transition: all 0.3s ease;
            border: none;
        }
        .current-sum {
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
        .mode-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 20px;
            border: 2px solid #d0e0ff;
            padding: 20px;
            margin: 10px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .mode-card:hover {
            margin-top: 5px;
            margin-bottom: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
            border-color: #a0c0ff;
        }
        .mode-card-selected {
            background: linear-gradient(135deg, #e0f0ff 0%, #d0e8ff 100%);
            border: 3px solid #80b0ff;
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        .mode-title {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .mode-description {
            font-size: 14px;
            color: #525252;
            margin-bottom: 10px;
        }
        .difficulty-button {
            border-radius: 15px;
            padding: 8px 15px;
            margin: 5px;
            font-weight: bold;
            transition: all 0.2s ease;
        }
        .difficulty-easy {
            background-color: #c8e6c9;
            color: #33691e;
            border: 1px solid #81c784;
        }
        .difficulty-normal {
            background-color: #bbdefb;
            color: #1565c0;
            border: 1px solid #64b5f6;
        }
        .difficulty-hard {
            background-color: #ffcdd2;
            color: #b71c1c;
            border: 1px solid #e57373;
        }
        .difficulty-selected {
            padding: 10px 17px;
            margin: 3px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .sum-value {
            font-size: 48px;
            font-weight: bold;
            color: #3949ab;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .target-value {
            font-size: 20px;
            color: #5e35b1;
            margin-bottom: 10px;
        }
        .countdown-value {
            font-size: 48px;
            font-weight: bold;
            color: #e53935;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
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
        .animation-container {
            transition: all 0.5s ease;
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
        
        # Title container
        title_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        
        # Title label
        title_label = Gtk.Label()
        title_label.set_markup("<span size='xx-large' weight='bold'>Math Challenges</span>")
        title_label.get_style_context().add_class("header-label")
        title_label.set_margin_top(30)
        title_label.set_margin_bottom(20)
        title_container.pack_start(title_label, False, False, 0)
        
        # Welcome message
        welcome_label = Gtk.Label()
        welcome_label.set_markup("<span size='large'>Welcome to the exciting world of mathematical challenges!</span>")
        welcome_label.set_margin_bottom(30)
        title_container.pack_start(welcome_label, False, False, 0)
        
        # Start game button
        start_button = Gtk.Button(label="Play Game")
        start_button.connect("clicked", self.on_show_mode_selection)
        start_button.set_size_request(200, 50)
        start_button.get_style_context().add_class("move-button")
        
        # Button box for centering
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        button_box.pack_start(start_button, False, False, 20)
        button_box.pack_start(Gtk.Label(label=""), True, True, 0)
        
        title_container.pack_start(button_box, False, False, 0)
        
        self.main_box.pack_start(title_container, True, True, 0)
        self.main_box.show_all()
    
    def on_show_mode_selection(self, button):
        """Show the game mode selection screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Container for mode selection
        mode_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        # Header
        header_label = Gtk.Label()
        header_label.set_markup("<span size='x-large' weight='bold'>Choose Game Mode</span>")
        header_label.set_margin_top(20)
        header_label.set_margin_bottom(20)
        mode_container.pack_start(header_label, False, False, 0)
        
        # Game modes in cards
        modes_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        modes_box.set_halign(Gtk.Align.CENTER)
        
        # Sum to Target mode card
        sum_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sum_card.set_size_request(280, 350)
        sum_card.get_style_context().add_class("mode-card")
        if self.game_mode == "sum":
            sum_card.get_style_context().add_class("mode-card-selected")
        
        sum_title = Gtk.Label()
        sum_title.set_markup("<span font_desc='18'>Sum to Target</span>")
        sum_title.get_style_context().add_class("mode-title")
        sum_card.pack_start(sum_title, False, False, 0)
        
        # Mode image (icon or representation)
        sum_img = Gtk.Image.new_from_icon_name("list-add", Gtk.IconSize.DIALOG)
        sum_img.set_pixel_size(64)
        sum_card.pack_start(sum_img, False, False, 10)
        
        sum_desc = Gtk.Label()
        sum_desc.set_markup(
            "<span>• Start from 0 and add numbers\n"
            "• First to reach the target exactly wins\n"
            "• Going over means you lose\n"
            "• Take turns with the computer\n"
            "• Select your difficulty level</span>"
        )
        sum_desc.set_line_wrap(True)
        sum_desc.get_style_context().add_class("mode-description")
        sum_card.pack_start(sum_desc, False, False, 10)
        
        # Example visualization
        sum_example = Gtk.Label()
        sum_example.set_markup("<span size='large'>0 → <b>21</b></span>")
        sum_card.pack_start(sum_example, False, False, 10)
        
        # Select button
        sum_button = Gtk.Button(label="Select Mode")
        sum_button.get_style_context().add_class("move-button")
        sum_button.connect("clicked", self.on_mode_selected, "sum")
        sum_card.pack_start(sum_button, False, False, 10)
        
        modes_box.pack_start(sum_card, False, False, 10)
        
        # Countdown mode card
        countdown_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        countdown_card.set_size_request(280, 350)
        countdown_card.get_style_context().add_class("mode-card")
        if self.game_mode == "countdown":
            countdown_card.get_style_context().add_class("mode-card-selected")
        
        countdown_title = Gtk.Label()
        countdown_title.set_markup("<span font_desc='18'>Countdown to Zero</span>")
        countdown_title.get_style_context().add_class("mode-title")
        countdown_card.pack_start(countdown_title, False, False, 0)
        
        # Mode image
        countdown_img = Gtk.Image.new_from_icon_name("list-remove", Gtk.IconSize.DIALOG)
        countdown_img.set_pixel_size(64)
        countdown_card.pack_start(countdown_img, False, False, 10)
        
        countdown_desc = Gtk.Label()
        countdown_desc.set_markup(
            "<span>• Start from target and subtract\n"
            "• First to reach exactly 0 wins\n"
            "• Going below 0 means you lose\n"
            "• Take turns with the computer\n"
            "• Strategic fun for all ages</span>"
        )
        countdown_desc.set_line_wrap(True)
        countdown_desc.get_style_context().add_class("mode-description")
        countdown_card.pack_start(countdown_desc, False, False, 10)
        
        # Example visualization
        countdown_example = Gtk.Label()
        countdown_example.set_markup("<span size='large'><b>21</b> → 0</span>")
        countdown_card.pack_start(countdown_example, False, False, 10)
        
        # Select button
        countdown_button = Gtk.Button(label="Select Mode")
        countdown_button.get_style_context().add_class("move-button")
        countdown_button.connect("clicked", self.on_mode_selected, "countdown")
        countdown_card.pack_start(countdown_button, False, False, 10)
        
        modes_box.pack_start(countdown_card, False, False, 10)
        
        mode_container.pack_start(modes_box, True, True, 0)
        
        # Back button
        back_button = Gtk.Button(label="Back")
        back_button.connect("clicked", lambda w: self.show_title_screen())
        back_button.set_halign(Gtk.Align.START)
        back_button.set_margin_start(10)
        back_button.set_margin_bottom(10)
        mode_container.pack_start(back_button, False, False, 10)
        
        self.main_box.pack_start(mode_container, True, True, 0)
        self.main_box.show_all()
    
    def on_mode_selected(self, button, mode):
        """Handle game mode selection."""
        self.game_mode = mode
        self.show_difficulty_selection()
    
    def show_difficulty_selection(self):
        """Show the difficulty selection screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Container for difficulty selection
        difficulty_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        difficulty_container.set_halign(Gtk.Align.CENTER)
        difficulty_container.set_valign(Gtk.Align.CENTER)
        
        # Header
        mode_name = "Sum to Target" if self.game_mode == "sum" else "Countdown to Zero"
        header_label = Gtk.Label()
        header_label.set_markup(f"<span size='x-large' weight='bold'>{mode_name}</span>")
        header_label.set_margin_top(20)
        header_label.set_margin_bottom(10)
        difficulty_container.pack_start(header_label, False, False, 0)
        
        # Sub-header
        sub_header = Gtk.Label()
        sub_header.set_markup("<span size='large'>Select Difficulty Level</span>")
        sub_header.set_margin_bottom(30)
        difficulty_container.pack_start(sub_header, False, False, 0)
        
        # Difficulty options
        difficulties_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        difficulties_box.set_halign(Gtk.Align.CENTER)
        
        # Easy
        easy_button = Gtk.Button(label="Easy")
        easy_button.get_style_context().add_class("difficulty-button")
        easy_button.get_style_context().add_class("difficulty-easy")
        if self.difficulty == "easy":
            easy_button.get_style_context().add_class("difficulty-selected")
        easy_button.connect("clicked", self.on_difficulty_selected, "easy")
        difficulties_box.pack_start(easy_button, False, False, 0)
        
        # Normal
        normal_button = Gtk.Button(label="Normal")
        normal_button.get_style_context().add_class("difficulty-button")
        normal_button.get_style_context().add_class("difficulty-normal")
        if self.difficulty == "normal":
            normal_button.get_style_context().add_class("difficulty-selected")
        normal_button.connect("clicked", self.on_difficulty_selected, "normal")
        difficulties_box.pack_start(normal_button, False, False, 0)
        
        # Hard
        hard_button = Gtk.Button(label="Hard")
        hard_button.get_style_context().add_class("difficulty-button")
        hard_button.get_style_context().add_class("difficulty-hard")
        if self.difficulty == "hard":
            hard_button.get_style_context().add_class("difficulty-selected")
        hard_button.connect("clicked", self.on_difficulty_selected, "hard")
        difficulties_box.pack_start(hard_button, False, False, 0)
        
        difficulty_container.pack_start(difficulties_box, False, False, 0)
        
        # Explanation of difficulty levels
        explanation = Gtk.Label()
        explanation.set_markup(
            "<span size='small'>\n"
            "<b>Easy:</b> Target of 15, optimal computer strategy disabled\n"
            "<b>Normal:</b> Target of 21, moderate computer strategy\n"
            "<b>Hard:</b> Target of 30, advanced computer strategy\n"
            "</span>"
        )
        explanation.set_margin_top(20)
        explanation.set_margin_bottom(30)
        difficulty_container.pack_start(explanation, False, False, 0)
        
        # Start game button
        start_button = Gtk.Button(label="Start Game")
        start_button.connect("clicked", self.on_start_game)
        start_button.set_size_request(200, 50)
        start_button.get_style_context().add_class("move-button")
        difficulty_container.pack_start(start_button, False, False, 10)
        
        # Back button
        back_button = Gtk.Button(label="Back")
        back_button.connect("clicked", lambda w: self.on_show_mode_selection(None))
        back_button.set_halign(Gtk.Align.CENTER)
        back_button.set_margin_top(20)
        difficulty_container.pack_start(back_button, False, False, 0)
        
        self.main_box.pack_start(difficulty_container, True, True, 0)
        self.main_box.show_all()
    
    def on_difficulty_selected(self, button, difficulty):
        """Handle difficulty selection."""
        self.difficulty = difficulty
        
        # Update target based on difficulty
        if difficulty == "easy":
            self.target_sum = 15
        elif difficulty == "normal":
            self.target_sum = 21
        elif difficulty == "hard":
            self.target_sum = 30
        
        # Refresh the UI to show the selection
        self.show_difficulty_selection()
    
    def on_start_game(self, button):
        """Start a new game when the Start Game button is clicked."""
        # Reset game state
        if self.game_mode == "sum":
            self.current_sum = 0
        else:  # countdown
            self.current_sum = self.target_sum
        
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
        
        # Top bar with game info
        info_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        
        # Mode indicator
        mode_name = "Sum to Target" if self.game_mode == "sum" else "Countdown to Zero"
        mode_label = Gtk.Label()
        mode_label.set_markup(f"<span font_desc='14'><b>{mode_name}</b> | {self.difficulty.capitalize()}</span>")
        mode_label.set_halign(Gtk.Align.START)
        info_bar.pack_start(mode_label, True, True, 10)
        
        # New Game button
        new_game_button = Gtk.Button(label="New Game")
        new_game_button.connect("clicked", lambda w: self.on_show_mode_selection(None))
        info_bar.pack_end(new_game_button, False, False, 10)
        
        self.main_box.pack_start(info_bar, False, False, 10)
        
        # Stats bar
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stats_box.set_hexpand(True)
        stats_box.set_vexpand(False)
        stats_box.set_homogeneous(True)
        
        # Your moves frame
        human_moves_frame = Gtk.Frame(label="Your Moves")
        human_moves_frame.set_label_align(0.5, 0.5)
        human_moves_frame.get_style_context().add_class("stat-frame")
        self.human_moves_label = Gtk.Label(label="0")
        self.human_moves_label.get_style_context().add_class("stat-label")
        human_moves_frame.add(self.human_moves_label)
        stats_box.pack_start(human_moves_frame, True, True, 0)
        
        # Game status frame
        status_frame = Gtk.Frame(label="Status")
        status_frame.set_label_align(0.5, 0.5)
        status_frame.get_style_context().add_class("stat-frame")
        self.status_label = Gtk.Label(label="Your Turn")
        self.status_label.get_style_context().add_class("stat-label")
        status_frame.add(self.status_label)
        stats_box.pack_start(status_frame, True, True, 0)
        
        # Computer moves frame
        computer_moves_frame = Gtk.Frame(label="Computer Moves")
        computer_moves_frame.set_label_align(0.5, 0.5)
        computer_moves_frame.get_style_context().add_class("stat-frame")
        self.computer_moves_label = Gtk.Label(label="0")
        self.computer_moves_label.get_style_context().add_class("stat-label")
        computer_moves_frame.add(self.computer_moves_label)
        stats_box.pack_start(computer_moves_frame, True, True, 0)
        
        self.main_box.pack_start(stats_box, False, False, 10)
        
        # Game content container
        game_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_container.set_halign(Gtk.Align.CENTER)
        game_container.set_valign(Gtk.Align.CENTER)
        game_container.set_margin_top(20)
        game_container.set_margin_bottom(20)
        
        # Current and target values
        if self.game_mode == "sum":
            current_label = Gtk.Label()
            current_label.set_markup("<span size='large' weight='bold'>Current Sum:</span>")
            game_container.pack_start(current_label, False, False, 0)
            
            self.current_value_display = Gtk.Label()
            self.current_value_display.get_style_context().add_class("sum-value")
            self.current_value_display.set_markup(f"<span>{self.current_sum}</span>")
            game_container.pack_start(self.current_value_display, False, False, 0)
            
            target_label = Gtk.Label()
            target_label.set_markup(f"<span size='large' weight='bold'>Target: {self.target_sum}</span>")
            target_label.get_style_context().add_class("target-value")
            game_container.pack_start(target_label, False, False, 10)
        else:  # countdown mode
            current_label = Gtk.Label()
            current_label.set_markup("<span size='large' weight='bold'>Remaining:</span>")
            game_container.pack_start(current_label, False, False, 0)
            
            self.current_value_display = Gtk.Label()
            self.current_value_display.get_style_context().add_class("countdown-value")
            self.current_value_display.set_markup(f"<span>{self.current_sum}</span>")
            game_container.pack_start(self.current_value_display, False, False, 0)
            
            target_label = Gtk.Label()
            target_label.set_markup("<span size='large' weight='bold'>Target: 0</span>")
            target_label.get_style_context().add_class("target-value")
            game_container.pack_start(target_label, False, False, 10)
        
        # Progress bar showing how close to the target
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_margin_start(50)
        self.progress_bar.set_margin_end(50)
        self.progress_bar.set_margin_bottom(20)
        self.update_progress()
        game_container.pack_start(self.progress_bar, False, False, 0)
        
        self.main_box.pack_start(game_container, True, True, 0)
        
        # Game rules reminder
        rules_reminder = Gtk.Label()
        if self.game_mode == "sum":
            rules_reminder.set_text(f"First to reach EXACTLY {self.target_sum} wins!")
        else:  # countdown
            rules_reminder.set_text("First to reach EXACTLY 0 wins!")
        rules_reminder.get_style_context().add_class("rule-label")
        rules_reminder.set_margin_bottom(20)
        self.main_box.pack_start(rules_reminder, False, False, 0)
        
        # Move buttons
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.move_buttons = []  # Store references to the move buttons
        
        for move in range(1, 4):
            action = "Add" if self.game_mode == "sum" else "Subtract"
            move_button = Gtk.Button(label=f"{action} {move}")
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
        self.main_box.show_all()
    
    def update_progress(self):
        """Update the progress bar to show progress toward target."""
        if self.game_mode == "sum":
            fraction = min(1.0, self.current_sum / self.target_sum)
            self.progress_bar.set_fraction(fraction)
            self.progress_bar.set_text(f"{self.current_sum} / {self.target_sum}")
        else:  # countdown
            fraction = 1.0 - min(1.0, self.current_sum / self.target_sum)
            self.progress_bar.set_fraction(fraction)
            self.progress_bar.set_text(f"{self.current_sum} → 0")
        
        self.progress_bar.set_show_text(True)
    
    def update_game_ui(self):
        """Update the UI to reflect the current game state."""
        # Update move counts
        self.human_moves_label.set_text(f"{self.human_moves}")
        self.computer_moves_label.set_text(f"{self.computer_moves}")
        
        # Update current value display
        self.current_value_display.set_markup(f"<span>{self.current_sum}</span>")
        
        # Update progress bar
        self.update_progress()
    
    def on_move_clicked(self, button, move):
        """Handle player's move."""
        if self.game_over:
            return
        
        # Update current sum based on game mode
        if self.game_mode == "sum":
            self.current_sum += move
        else:  # countdown
            self.current_sum -= move
        
        self.human_moves += 1
        
        # Update UI with animation
        button.get_style_context().add_class("animation-container")
        self.status_label.set_markup("<span size='large' weight='bold'>Computer's Turn</span>")
        self.update_game_ui()
        
        # Check if game over
        if self.check_game_over():
            return
        
        # Disable buttons during computer's turn
        if hasattr(self, 'move_buttons'):
            for btn in self.move_buttons:
                btn.set_sensitive(False)
        
        # Computer's turn after delay
        GLib.timeout_add(1000, self.computer_move)
    
    def computer_move(self):
        """Execute computer's move."""
        if self.game_over:
            return False
        
        move = self.calculate_computer_move()
        
        # Update sum based on game mode
        if self.game_mode == "sum":
            self.current_sum += move
        else:  # countdown
            self.current_sum -= move
        
        self.computer_moves += 1
        
        # Update UI
        self.status_label.set_markup(f"<span size='large' weight='bold'>Your Turn (Computer {('added' if self.game_mode == 'sum' else 'subtracted')} {move})</span>")
        self.update_game_ui()
        
        # Check if game over
        if self.check_game_over():
            return False
        
        # Re-enable valid move buttons for player's turn
        self.update_move_buttons()
        
        return False
    
    def calculate_computer_move(self):
        """Calculate the computer's move based on game mode and difficulty."""
        if self.game_mode == "sum":
            # Calculate optimal move for sum mode
            remaining = self.target_sum - self.current_sum
            
            if self.difficulty == "easy":
                # Easy: Just random moves
                valid_moves = [i for i in range(1, 4) if self.current_sum + i <= self.target_sum]
                return random.choice(valid_moves) if valid_moves else 1
            
            elif self.difficulty == "normal":
                # Normal: Some strategy but not perfect
                if remaining <= 3:
                    # Can win in one move
                    return remaining
                elif random.random() < 0.7:  # 70% chance of making optimal move
                    return self.get_optimal_sum_move(remaining)
                else:
                    # Random move
                    valid_moves = [i for i in range(1, 4) if self.current_sum + i <= self.target_sum]
                    return random.choice(valid_moves) if valid_moves else 1
            
            else:  # hard
                # Hard: Always optimal
                if remaining <= 3:
                    # Can win in one move
                    return remaining
                else:
                    return self.get_optimal_sum_move(remaining)
        
        else:  # countdown mode
            if self.difficulty == "easy":
                # Easy: Just random moves
                valid_moves = [i for i in range(1, 4) if self.current_sum - i >= 0]
                return random.choice(valid_moves) if valid_moves else 1
            
            elif self.difficulty == "normal":
                # Normal: Some strategy but not perfect
                if self.current_sum <= 3:
                    # Can win in one move
                    return self.current_sum
                elif random.random() < 0.7:  # 70% chance of making optimal move
                    return self.get_optimal_countdown_move()
                else:
                    # Random move
                    valid_moves = [i for i in range(1, 4) if self.current_sum - i >= 0]
                    return random.choice(valid_moves) if valid_moves else 1
            
            else:  # hard
                # Hard: Always optimal
                if self.current_sum <= 3:
                    # Can win in one move
                    return self.current_sum
                else:
                    return self.get_optimal_countdown_move()
    
    def get_optimal_sum_move(self, remaining):
        """Get the optimal move for sum mode."""
        if remaining == 4:
            # Force player into a losing position
            return 3
        elif remaining % 4 == 0:
            # Leave a multiple of 4 to maintain advantage
            return 3
        elif remaining % 4 == 1:
            # Leave a multiple of 4 to maintain advantage
            return 1
        elif remaining % 4 == 2:
            # Leave a multiple of 4 to maintain advantage
            return 2
        else:  # remaining % 4 == 3
            # Leave a multiple of 4 to maintain advantage
            return 3
    
    def get_optimal_countdown_move(self):
        """Get the optimal move for countdown mode."""
        if self.current_sum % 4 == 0:
            return 3
        elif self.current_sum % 4 == 1:
            return 1
        elif self.current_sum % 4 == 2:
            return 2
        else:  # current_sum % 4 == 3
            return 3
    
    def update_move_buttons(self):
        """Update move buttons based on current game state."""
        if hasattr(self, 'move_buttons'):
            for i, button in enumerate(self.move_buttons):
                move = i + 1
                if self.game_mode == "sum":
                    button.set_sensitive(not self.game_over and self.current_sum + move <= self.target_sum)
                else:  # countdown
                    button.set_sensitive(not self.game_over and self.current_sum - move >= 0)
    
    def check_game_over(self):
        """Check if the game is over and handle end game if needed."""
        if self.game_mode == "sum":
            if self.current_sum >= self.target_sum:
                self.end_game()
                return True
        else:  # countdown
            if self.current_sum <= 0:
                self.end_game()
                return True
        return False
    
    def end_game(self):
        """End the game and show the results."""
        self.game_over = True
        
        # Determine winner based on game mode
        if self.game_mode == "sum":
            if self.current_sum == self.target_sum:
                # Last player to move wins
                if self.human_moves > self.computer_moves:
                    winner = "You Win!"
                    message = f"You reached exactly {self.target_sum}!"
                else:
                    winner = "Computer Wins!"
                    message = f"Computer reached exactly {self.target_sum}!"
            else:  # Over the target
                if self.human_moves > self.computer_moves:
                    winner = "Computer Wins!"
                    message = f"You went over {self.target_sum}!"
                else:
                    winner = "You Win!"
                    message = f"Computer went over {self.target_sum}!"
        else:  # countdown
            if self.current_sum == 0:
                # Last player to move wins
                if self.human_moves > self.computer_moves:
                    winner = "You Win!"
                    message = "You reached exactly 0!"
                else:
                    winner = "Computer Wins!"
                    message = "Computer reached exactly 0!"
            else:  # Under zero
                if self.human_moves > self.computer_moves:
                    winner = "Computer Wins!"
                    message = "You went below 0!"
                else:
                    winner = "You Win!"
                    message = "Computer went below 0!"
        
        # Show end screen
        self.show_end_screen(winner, message)
    
    def show_end_screen(self, winner, message):
        """Display the end game screen."""
        # Clear previous widgets
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Create end screen container with animation
        end_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        end_container.set_halign(Gtk.Align.CENTER)
        end_container.set_valign(Gtk.Align.CENTER)
        end_container.get_style_context().add_class("animation-container")
        
        # Winner announcement
        winner_label = Gtk.Label()
        winner_label.set_markup(f"<span size='xx-large' weight='bold'>{winner}</span>")
        winner_label.get_style_context().add_class("header-label")
        winner_label.set_margin_top(30)
        winner_label.set_margin_bottom(10)
        end_container.pack_start(winner_label, False, False, 0)
        
        # Result message
        result_label = Gtk.Label(label=message)
        if "You Win" in winner:
            result_label.get_style_context().add_class("success-text")
        else:
            result_label.get_style_context().add_class("failure-text")
        result_label.set_margin_bottom(20)
        end_container.pack_start(result_label, False, False, 0)
        
        # Final value display
        final_value = Gtk.Label()
        if self.game_mode == "sum":
            final_value.set_markup(f"<span size='x-large' weight='bold'>Final Sum: {self.current_sum}</span>")
        else:  # countdown
            final_value.set_markup(f"<span size='x-large' weight='bold'>Final Value: {self.current_sum}</span>")
        end_container.pack_start(final_value, False, False, 10)
        
        # Move counts in frames like the game screen
        stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        stats_box.set_homogeneous(True)
        
        # Your moves frame
        human_frame = Gtk.Frame(label="Your Moves")
        human_frame.set_label_align(0.5, 0.5)
        human_frame.get_style_context().add_class("stat-frame")
        human_label = Gtk.Label(label=f"{self.human_moves}")
        human_label.get_style_context().add_class("stat-label")
        human_frame.add(human_label)
        stats_box.pack_start(human_frame, True, True, 0)
        
        # Computer moves frame
        comp_frame = Gtk.Frame(label="Computer Moves")
        comp_frame.set_label_align(0.5, 0.5)
        comp_frame.get_style_context().add_class("stat-frame")
        comp_label = Gtk.Label(label=f"{self.computer_moves}")
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
        
        end_container.pack_start(stats_box, False, False, 20)
        
        # Button container
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        button_box.set_halign(Gtk.Align.CENTER)
        
        # Play again with same settings
        play_again_button = Gtk.Button(label="Play Again")
        play_again_button.get_style_context().add_class("move-button")
        play_again_button.connect("clicked", self.on_start_game)
        play_again_button.set_size_request(150, 50)
        button_box.pack_start(play_again_button, False, False, 10)
        
        # Change game settings
        change_settings_button = Gtk.Button(label="Change Settings")
        change_settings_button.connect("clicked", lambda w: self.on_show_mode_selection(None))
        change_settings_button.set_size_request(150, 50)
        button_box.pack_start(change_settings_button, False, False, 10)
        
        end_container.pack_start(button_box, False, False, 20)
        
        self.main_box.pack_start(end_container, True, True, 0)
        self.main_box.show_all()


# To make the activity discoverable by Sugar
def main():
    # Create an instance and start the main loop
    win = OddScoringActivity(None)
    Gtk.main()

if __name__ == '__main__':
    main()
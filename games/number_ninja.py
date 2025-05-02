#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
import cairo
import random
import math
from gettext import gettext as _

from sugar3.activity import activity
from sugar3.activity.widgets import StopButton, ActivityToolbarButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton
from sugar3.graphics.style import GRID_CELL_SIZE

# Define a number class to handle the floating numbers
class Number:
    def __init__(self, value, x, y, speed):
        self.value = value
        self.x = x
        self.y = y
        self.speed = speed
        self.size = 30  # Default, will be overridden on game start
        
        # More vibrant color palette based on number value
        hue = (value * 25) % 360 / 360  # Use value to create different hues
        self.color = self._hsv_to_rgb(hue, 0.85, 0.95)
        
        self.alive = True
        self.pulse = 0  # For animation
        self.pulse_direction = 1
        # Add rotation for more dynamic appearance
        self.rotation = random.uniform(-0.1, 0.1)
    
    def _hsv_to_rgb(self, h, s, v):
        if s == 0:
            return v, v, v
        
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i % 6 == 0:
            return v, t, p
        elif i % 6 == 1:
            return q, v, p
        elif i % 6 == 2:
            return p, v, t
        elif i % 6 == 3:
            return p, q, v
        elif i % 6 == 4:
            return t, p, v
        else:
            return v, p, q
        
    def move(self):
        self.x += self.speed
        # Add a pulsating animation
        self.pulse += 0.1 * self.pulse_direction
        if self.pulse > 1:
            self.pulse = 1
            self.pulse_direction = -1
        elif self.pulse < 0:
            self.pulse = 0
            self.pulse_direction = 1
        
    def is_clicked(self, click_x, click_y):
        # Check if the click is inside the number
        distance = math.sqrt((self.x - click_x)**2 + (self.y - click_y)**2)
        return distance < self.size / 2
        
    def draw(self, context):
        # Calculate size with pulse effect
        pulse_size = self.size * (1 + self.pulse * 0.15)
        
        # Save context for rotation
        context.save()
        context.translate(self.x, self.y)
        context.rotate(self.rotation)
        
        # Draw a glow effect
        gradient = cairo.RadialGradient(0, 0, 0, 0, 0, pulse_size)
        r, g, b = self.color
        gradient.add_color_stop_rgba(0, r, g, b, 0.9)
        gradient.add_color_stop_rgba(1, r, g, b, 0)
        context.set_source(gradient)
        context.arc(0, 0, pulse_size * 1.5, 0, 2 * math.pi)
        context.fill()
        
        # Draw a circle with gradient - more pronounced
        gradient = cairo.RadialGradient(0, 0, 0, 0, 0, pulse_size/2)
        gradient.add_color_stop_rgba(0, 1, 1, 1, 1)  # White center
        gradient.add_color_stop_rgba(0.7, r+0.2, g+0.2, b+0.2, 1)  # Brighter color
        gradient.add_color_stop_rgba(1, r, g, b, 1)
        context.set_source(gradient)
        context.arc(0, 0, pulse_size/2, 0, 2 * math.pi)
        context.fill()
        
        # Draw border
        context.set_line_width(2.5)
        context.set_source_rgba(1, 1, 1, 0.8)
        context.arc(0, 0, pulse_size/2, 0, 2 * math.pi)
        context.stroke()
        
        # Draw the number with shadow
        context.set_source_rgba(0, 0, 0, 0.3)  # Shadow color
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(pulse_size * 0.6)
        
        # Center the text
        text = str(self.value)
        x_bearing, y_bearing, width, height, x_advance, y_advance = context.text_extents(text)
        context.move_to(-width / 2 - x_bearing + 1, -height / 2 - y_bearing + 1)  # Shadow offset
        context.show_text(text)
        
        # Actual text
        context.set_source_rgb(0.1, 0.1, 0.1)
        context.move_to(-width / 2 - x_bearing, -height / 2 - y_bearing)
        context.show_text(text)
        
        # Restore context after rotation
        context.restore()

class NumberNinjaActivity(activity.Activity):
    def __init__(self, handle):
        activity.Activity.__init__(self, handle)
        self.in_sugar = True

        # Apply CSS styling
        self._apply_css()

        # Set up toolbar
        toolbar_box = ToolbarBox()
        activity_button = ActivityToolbarButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()
        
        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()
        
        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_name("number-ninja-window")
        self.set_canvas(vbox)
        
        # Create screens
        self.title_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.game_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.end_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        vbox.pack_start(self.title_screen, True, True, 0)
        vbox.pack_start(self.game_screen, True, True, 0)
        vbox.pack_start(self.end_screen, True, True, 0)
        
        self._init_common()

    def _apply_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        #number-ninja-window {
            background-image: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            border-radius: 18px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            padding: 16px;
            color: #ffffff;
        }
        .stat-frame {
            padding: 8px;
            border-radius: 16px;
            background-color: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .stat-frame:hover {
            background-color: rgba(255, 255, 255, 0.18);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
        }
        .stat-frame > * > * {
            background: linear-gradient(90deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
            border-radius: 12px;
            padding: 12px 0;
            color: #ffffff;
        }
        .stat-title {
            font-size: 15px;
            font-weight: normal;
            color: #a2d2ff;
            text-shadow: 0 1px 3px rgba(0,0,0,0.2);
        }
        .stat-label {
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .header-label {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 20px;
            font-family: 'Sans', serif;
            color: #ffd166;
            text-shadow: 0 3px 6px rgba(0,0,0,0.4);
        }
        .rule-label {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
            background: linear-gradient(90deg, rgba(41,121,255,0.3) 0%, rgba(41,121,255,0.2) 100%);
            padding: 14px 20px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.25);
            box-shadow: 0 4px 10px rgba(0,0,0,0.25);
            margin-top: 8px;
            margin-bottom: 8px;
            text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
        .rule-label:hover {
            background: linear-gradient(90deg, rgba(41,121,255,0.4) 0%, rgba(41,121,255,0.3) 100%);
        }
        .rule-frame, .result-frame {
            background-color: rgba(255, 255, 255, 0.12);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 18px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            padding: 5px;
        }
        .rule-frame:hover, .result-frame:hover {
            background-color: rgba(255, 255, 255, 0.15);
            box-shadow: 0 12px 28px rgba(0,0,0,0.35);
        }
        .success-text {
            color: #4ade80;
            font-weight: bold;
            background-color: rgba(74,222,128,0.15);
            padding: 14px;
            border-radius: 12px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
            border: 1px solid rgba(74,222,128,0.3);
        }
        .failure-text {
            color: #f87171;
            font-weight: bold;
            background-color: rgba(248,113,113,0.15);
            padding: 14px;
            border-radius: 12px;
            text-shadow: 0 1px 2px rgba(0,0,0,0.2);
            border: 1px solid rgba(248,113,113,0.3);
        }
        button {
            background: linear-gradient(45deg, #4f46e5 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 28px;
            padding: 14px 28px;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 12px rgba(99,102,241,0.4);
        }
        button:hover {
            background: linear-gradient(45deg, #6366f1 0%, #818cf8 100%);
            box-shadow: 0 8px 16px rgba(99,102,241,0.5);
        }
        button:active {
            box-shadow: 0 2px 6px rgba(99,102,241,0.3);
        }
        combobox {
            border-radius: 20px;
            padding: 10px;
            background-color: rgba(255,255,255,0.15);
            color: white;
            border: 1px solid rgba(255,255,255,0.25);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        combobox:hover {
            background-color: rgba(255,255,255,0.25);
            box-shadow: 0 6px 12px rgba(0,0,0,0.25);
        }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    # Move all shared initialization code to _init_common
    def _init_common(self):
        # Load background image for all subclasses
        self.bg_pixbuf = None
        try:
            self.bg_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                "/home/pranjalnegi/Maths-Games/assets/background.jpg", 800, 500, preserve_aspect_ratio=True)
        except Exception as e:
            print("Could not load background image:", e)
            
        # Set up title screen
        self._setup_title_screen()
        
        # Set up game screen
        self._setup_game_screen()
        
        # Set up end screen
        self._setup_end_screen()
        
        # Game variables
        self.numbers = []
        self.score = 0
        self.health = 100
        self.game_time = 60  # 60 seconds
        self.rule_type = "even"  # Default rule
        self.is_running = False
        
        # New gameplay variables
        self.level = 1
        self.combo_count = 0
        self.max_combo = 0
        self.number_speed_multiplier = 1.0
        self.spawn_rate = 1500  # ms between spawns
        self.next_level_score = 100  # Score needed for level 2
        self.last_correct_time = 0  # For tracking combo timing
        
        # Power-up variables
        self.slow_time_active = False
        self.slow_time_remaining = 0
        self.power_up_available = False
        self.power_up_type = None
        
        # Show title screen initially
        self._show_title_screen()
        
        # Connect to size-allocate to handle resizing
        self.connect("size-allocate", self._on_resize)
        self.connect("destroy", self._cleanup)
        
    def _on_resize(self, widget, allocation):
        # Update number size based on screen size
        if hasattr(self, 'drawing_area'):
            width = self.drawing_area.get_allocated_width()
            height = self.drawing_area.get_allocated_height()
            # Scale number size based on smaller dimension
            Number.size = min(width, height) / 12
            
            # Adjust existing numbers
            for num in self.numbers:
                num.size = Number.size
                
            # Queue redraw
            self.drawing_area.queue_draw()

    def _setup_title_screen(self):
        # Use a fixed container for better positioning
        self.title_screen.set_size_request(-1, -1)  # Let it adjust to content
        
        # Center all content
        title_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title_container.set_halign(Gtk.Align.CENTER)
        title_container.set_valign(Gtk.Align.CENTER)
        self.title_screen.pack_start(title_container, True, True, 0)
        
        # Logo label
        logo_label = Gtk.Label()
        logo_label.set_markup("<span weight='bold' size='xx-large'>Number Ninja</span>")
        logo_label.get_style_context().add_class("header-label")
        title_container.pack_start(logo_label, False, False, 20)
        
        # Rule selector frame
        rule_frame = Gtk.Frame()
        rule_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        rule_frame.get_style_context().add_class("rule-frame")
        rule_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        rule_box.set_margin_top(10)
        rule_box.set_margin_bottom(10)
        rule_box.set_margin_start(20)
        rule_box.set_margin_end(20)
        rule_frame.add(rule_box)
        
        # Rule selector label
        rule_title = Gtk.Label(label=_("Select Game Mode:"))
        rule_title.set_halign(Gtk.Align.START)
        rule_box.pack_start(rule_title, False, False, 0)
        
        # Combo box in its own container
        combo_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.rule_combo = Gtk.ComboBoxText()
        self.rule_combo.append_text(_("Even Numbers"))
        self.rule_combo.append_text(_("Prime Numbers"))
        self.rule_combo.append_text(_("Multiples of 3"))
        self.rule_combo.set_active(0)  # Default to even numbers
        self.rule_combo.connect("changed", self._on_rule_changed)
        combo_container.pack_start(self.rule_combo, True, True, 0)
        rule_box.pack_start(combo_container, False, False, 5)
        
        # Instructions
        instructions = Gtk.Label()
        instructions.set_markup(_("<span>Click only on numbers that match the rule!</span>"))
        rule_box.pack_start(instructions, False, False, 5)
        
        # Show rule label below selector
        self.rule_preview_label = Gtk.Label()
        self.rule_preview_label.get_style_context().add_class("rule-label")
        rule_box.pack_start(self.rule_preview_label, False, False, 5)
        self._on_rule_changed(self.rule_combo)  # Set initial rule preview
        
        title_container.pack_start(rule_frame, False, False, 20)
        
        # Start button in its own container
        button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_container.set_halign(Gtk.Align.CENTER)
        start_button = Gtk.Button(label=_("Start Game"))
        start_button.connect("clicked", self._on_start_game)
        button_container.pack_start(start_button, False, False, 0)
        title_container.pack_start(button_container, False, False, 20)

    def _on_rule_changed(self, combo):
        rule_index = combo.get_active()
        if rule_index == 0:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        elif rule_index == 1:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on prime numbers</span>")
        else:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on multiples of 3</span>")

    def _setup_game_screen(self):
        # Game screen container
        game_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_container.set_margin_top(10)
        game_container.set_margin_bottom(10)
        game_container.set_margin_start(10)
        game_container.set_margin_end(10)
        self.game_screen.pack_start(game_container, True, True, 0)

        # Top bar with frames for stats
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        top_bar.set_hexpand(True)
        top_bar.set_vexpand(False)
        top_bar.set_homogeneous(True)
        top_bar.set_margin_bottom(10)

        # Score
        score_frame = Gtk.Frame()
        score_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        score_frame.get_style_context().add_class("stat-frame")
        score_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        score_label_text = Gtk.Label(label=_("Score"))
        score_label_text.get_style_context().add_class("stat-title")
        self.score_label = Gtk.Label(label=_("0"))
        self.score_label.get_style_context().add_class("stat-label")
        score_box.pack_start(score_label_text, False, False, 3)
        score_box.pack_start(self.score_label, False, False, 3)
        score_frame.add(score_box)
        top_bar.pack_start(score_frame, True, True, 0)

        # Level
        level_frame = Gtk.Frame()
        level_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        level_frame.get_style_context().add_class("stat-frame")
        level_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        level_label_text = Gtk.Label(label=_("Level"))
        level_label_text.get_style_context().add_class("stat-title")
        self.level_label = Gtk.Label(label=_("1"))
        self.level_label.get_style_context().add_class("stat-label")
        level_box.pack_start(level_label_text, False, False, 3)
        level_box.pack_start(self.level_label, False, False, 3)
        level_frame.add(level_box)
        top_bar.pack_start(level_frame, True, True, 0)

        # Timer
        timer_frame = Gtk.Frame()
        timer_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        timer_frame.get_style_context().add_class("stat-frame")
        timer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        timer_label_text = Gtk.Label(label=_("Time"))
        timer_label_text.get_style_context().add_class("stat-title")
        self.timer_label = Gtk.Label(label=_("60"))
        self.timer_label.get_style_context().add_class("stat-label")
        timer_box.pack_start(timer_label_text, False, False, 3)
        timer_box.pack_start(self.timer_label, False, False, 3)
        timer_frame.add(timer_box)
        top_bar.pack_start(timer_frame, True, True, 0)

        # Health
        health_frame = Gtk.Frame()
        health_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        health_frame.get_style_context().add_class("stat-frame")
        health_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        health_label_text = Gtk.Label(label=_("Health"))
        health_label_text.get_style_context().add_class("stat-title")
        self.health_label = Gtk.Label(label=_("100%"))
        self.health_label.get_style_context().add_class("stat-label")
        health_box.pack_start(health_label_text, False, False, 3)
        health_box.pack_start(self.health_label, False, False, 3)
        health_frame.add(health_box)
        top_bar.pack_start(health_frame, True, True, 0)

        game_container.pack_start(top_bar, False, False, 0)
        
        # Combo indicator
        self.combo_label = Gtk.Label()
        self.combo_label.set_markup("<span weight='bold' size='large' color='#FFEB3B'>Combo: 0</span>")
        self.combo_label.set_no_show_all(True)  # Hide initially
        game_container.pack_start(self.combo_label, False, False, 5)
        
        # Game area (Drawing area) in a frame for better appearance
        game_frame = Gtk.Frame()
        game_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect("draw", self._on_draw)
        self.drawing_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self._on_area_clicked)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        game_frame.add(self.drawing_area)
        
        game_container.pack_start(game_frame, True, True, 0)
        
        # Current rule display
        rule_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        rule_box.set_halign(Gtk.Align.CENTER)
        
        self.rule_label = Gtk.Label()
        self.rule_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        self.rule_label.get_style_context().add_class("rule-label")
        rule_box.pack_start(self.rule_label, False, False, 0)
        
        # Power-up button
        self.power_button = Gtk.Button(label=_("Power-Up"))
        self.power_button.set_sensitive(False)  # Disabled until available
        self.power_button.connect("clicked", self._activate_power_up)
        rule_box.pack_start(self.power_button, False, False, 0)
        
        game_container.pack_start(rule_box, False, False, 10)

    def _setup_end_screen(self):
        # End game container - center everything
        end_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        end_container.set_halign(Gtk.Align.CENTER)
        end_container.set_valign(Gtk.Align.CENTER)
        self.end_screen.pack_start(end_container, True, True, 0)
        
        # End game title
        end_title = Gtk.Label()
        end_title.set_markup("<span weight='bold' size='xx-large'>Game Over!</span>")
        end_title.get_style_context().add_class("header-label")
        end_container.pack_start(end_title, False, False, 10)
        
        # Result frame
        result_frame = Gtk.Frame()
        result_frame.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        result_frame.get_style_context().add_class("result-frame")
        result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        result_box.set_margin_top(15)
        result_box.set_margin_bottom(15)
        result_box.set_margin_start(30)
        result_box.set_margin_end(30)
        
        # Final score
        self.final_score_label = Gtk.Label()
        self.final_score_label.set_markup("<span size='large'>Your score: 0</span>")
        result_box.pack_start(self.final_score_label, False, False, 5)
        
        # Max level and combo
        self.final_level_label = Gtk.Label()
        self.final_level_label.set_markup("<span>Highest Level: 1</span>")
        result_box.pack_start(self.final_level_label, False, False, 5)
        
        self.final_combo_label = Gtk.Label()
        self.final_combo_label.set_markup("<span>Max Combo: 0</span>")
        result_box.pack_start(self.final_combo_label, False, False, 5)
        
        result_frame.add(result_box)
        end_container.pack_start(result_frame, False, False, 15)
        
        # Buttons container
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        buttons_box.set_halign(Gtk.Align.CENTER)
        
        # Play again button
        play_again_button = Gtk.Button(label=_("Play Again"))
        play_again_button.connect("clicked", self._on_play_again)
        buttons_box.pack_start(play_again_button, False, False, 0)
        
        # Return to title button
        title_button = Gtk.Button(label=_("Return to Title"))
        title_button.connect("clicked", self._show_title_screen)
        buttons_box.pack_start(title_button, False, False, 0)
        
        end_container.pack_start(buttons_box, False, False, 10)
        
    def _show_title_screen(self, widget=None):
        self.title_screen.show_all()
        self.game_screen.hide()
        self.end_screen.hide()
        
        # Stop any running game
        if self.is_running:
            self._stop_game()
        
    def _show_game_screen(self):
        self.title_screen.hide()
        self.game_screen.show_all()
        self.end_screen.hide()
        
    def _show_end_screen(self):
        self.title_screen.hide()
        self.game_screen.hide()
        self.end_screen.show_all()
        
        # Update final score and stats
        self.final_score_label.set_markup(f"<span>Your score: {self.score}</span>")
        self.final_level_label.set_markup(f"<span>Highest Level: {self.level}</span>")
        self.final_combo_label.set_markup(f"<span>Max Combo: {self.max_combo}</span>")
        
        # Add success/failure style
        if self.health > 0:
            self.final_score_label.get_style_context().add_class("success-text")
        else:
            self.final_score_label.get_style_context().add_class("failure-text")
        
    def _on_start_game(self, widget):
        # Get selected rule
        rule_index = self.rule_combo.get_active()
        if rule_index == 0:
            self.rule_type = "even"
            self.rule_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        elif rule_index == 1:
            self.rule_type = "prime"
            self.rule_label.set_markup("<span weight='bold'>Rule: Click on prime numbers</span>")
        else:
            self.rule_type = "multiple3"
            self.rule_label.set_markup("<span weight='bold'>Rule: Click on multiples of 3</span>")
        
        # Reset game variables
        self.numbers = []
        self.score = 0
        self.health = 100
        self.game_time = 60
        self.level = 1
        self.combo_count = 0
        self.max_combo = 0
        self.number_speed_multiplier = 1.0
        self.spawn_rate = 1500
        self.next_level_score = 100
        self.slow_time_active = False
        self.power_up_available = False
        self.power_up_type = None
        self.combo_label.hide()
        self.power_button.set_sensitive(False)

        # Calculate appropriate number size based on screen dimensions
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()
        Number.size = min(width, height) / 12
        
        # Update labels
        self.score_label.set_text(_("0"))
        self.timer_label.set_text(_("60"))
        self.health_label.set_text(_("100%"))
        self.level_label.set_text(_("1"))
        
        # Show game screen
        self._show_game_screen()
        
        # Start the game loop
        self.is_running = True
        GLib.timeout_add(1000, self._update_timer)  # Update timer every second
        GLib.timeout_add(50, self._update_game)     # Update game every 50ms
        GLib.timeout_add(self.spawn_rate, self._add_number)    # Add numbers at current spawn rate
        GLib.timeout_add(500, self._check_level_up)   # Check for level up every 0.5 seconds
        
    def _on_play_again(self, widget):
        self._show_title_screen()
        
    def _on_draw(self, widget, context):
        # Get the dimensions of the drawing area
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Draw background with level-based color changes - more vibrant gradients
        hue = 0.6 - min(0.3, (self.level - 1) * 0.05)  # Gradually shift color with level
        pattern = cairo.LinearGradient(0, 0, width, height)
        
        # More vibrant base colors
        r, g, b = self._hsv_to_rgb(hue, 0.8, 0.3)
        r2, g2, b2 = self._hsv_to_rgb(hue + 0.05, 0.7, 0.5)
        
        pattern.add_color_stop_rgba(0, r, g, b, 1)
        pattern.add_color_stop_rgba(1, r2, g2, b2, 1)
        context.set_source(pattern)
        context.rectangle(0, 0, width, height)
        context.fill()
        
        # Draw background particles with more variety
        particle_count = 30 + min(40, self.level * 5)
        
        for i in range(particle_count):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(2, 15)
            opacity = random.uniform(0.02, 0.08 + min(0.12, self.level * 0.01))
            
            # Vary particle color
            particle_hue = random.uniform(0, 1)
            pr, pg, pb = self._hsv_to_rgb(particle_hue, 0.6, 0.9)
            context.set_source_rgba(pr, pg, pb, opacity)
            
            context.arc(x, y, size, 0, 2 * math.pi)
            context.fill()
        
        # Draw grid lines for visual depth - faint
        context.set_source_rgba(1, 1, 1, 0.03)
        context.set_line_width(1)
        
        # Horizontal lines
        for y in range(0, height, 30):
            context.move_to(0, y)
            context.line_to(width, y)
        
        # Vertical lines
        for x in range(0, width, 30):
            context.move_to(x, 0)
            context.line_to(x, height)
        
        context.stroke()
        
        # Draw slow time effect - more dramatic
        if self.slow_time_active:
            # Create a pulsing effect for slow time
            pulse = (GLib.get_monotonic_time() % 1000000) / 1000000.0
            opacity = 0.05 + 0.05 * math.sin(pulse * 2 * math.pi)
            
            # Gradient overlay for slow time
            slow_pattern = cairo.LinearGradient(0, 0, width, height)
            slow_pattern.add_color_stop_rgba(0, 0.2, 0.4, 0.9, opacity)
            slow_pattern.add_color_stop_rgba(1, 0.3, 0.6, 1.0, opacity + 0.05)
            
            context.set_source(slow_pattern)
            context.rectangle(0, 0, width, height)
            context.fill()
            
            # Add time particles
            for i in range(15):
                x = random.randint(0, width)
                y = random.randint(0, height)
                size = random.randint(1, 3)
                context.set_source_rgba(0.6, 0.8, 1.0, random.uniform(0.1, 0.4))
                context.arc(x, y, size, 0, 2 * math.pi)
                context.fill()
        
        # Draw all numbers
        for num in self.numbers:
            num.draw(context)
    
    def _hsv_to_rgb(self, h, s, v):
        if s == 0:
            return v, v, v
        
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        if i % 6 == 0:
            return v, t, p
        elif i % 6 == 1:
            return q, v, p
        elif i % 6 == 2:
            return p, v, t
        elif i % 6 == 3:
            return p, q, v
        elif i % 6 == 4:
            return t, p, v
        else:
            return v, p, q
        
    def _on_area_clicked(self, widget, event):
        if not self.is_running:
            return
            
        # Check if any number was clicked
        for num in self.numbers[:]:  # Use a copy to safely remove while iterating
            if num.is_clicked(event.x, event.y):
                # Check if the number matches the rule
                if self._check_rule(num.value):
                    # Correct click
                    self._handle_correct_click()
                else:
                    # Wrong click
                    self._handle_wrong_click()
                
                # Remove the number
                self.numbers.remove(num)
                self.drawing_area.queue_draw()
                break
    
    def _handle_correct_click(self):
        # Increment combo
        current_time = GLib.get_monotonic_time() / 1000000  # Convert to seconds
        
        # If clicked within 3 seconds of last correct click, increase combo
        if current_time - self.last_correct_time < 3.0:
            self.combo_count += 1
        else:
            self.combo_count = 1  # Reset combo but still count this click
            
        self.last_correct_time = current_time
        
        # Update max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
        
        # Show combo if >= 2
        if self.combo_count >= 2:
            self.combo_label.set_markup(f"<span weight='bold' size='large' color='#FFEB3B'>Combo: {self.combo_count}x</span>")
            self.combo_label.show()
        else:
            self.combo_label.hide()
        
        # Calculate points with combo multiplier
        combo_multiplier = min(1.0 + (self.combo_count * 0.1), 2.0)  # Cap at 2x
        points = int(10 * combo_multiplier * self.level)
        
        self.score += points
        self.score_label.set_text(str(self.score))
        
        # Random chance to get a power-up after 5+ combo
        if self.combo_count >= 5 and not self.power_up_available and random.random() < 0.2:
            self._give_power_up()
    
    def _handle_wrong_click(self):
        # Wrong click breaks combo
        self.combo_count = 0
        self.combo_label.hide()
        
        # Reduce health
        self.health -= 20
        if self.health < 0:
            self.health = 0
        self.health_label.set_text(f"{self.health}%")
        
        if self.health <= 0:
            self._end_game()
    
    def _give_power_up(self):
        self.power_up_available = True
        power_ups = ["slow", "clear", "health"]
        self.power_up_type = random.choice(power_ups)
        
        # Update button label based on power-up type
        if self.power_up_type == "slow":
            self.power_button.set_label(_("Slow Time"))
        elif self.power_up_type == "clear":
            self.power_button.set_label(_("Clear Screen"))
        elif self.power_up_type == "health":
            self.power_button.set_label(_("Heal"))
            
        self.power_button.set_sensitive(True)
    
    def _activate_power_up(self, widget):
        if not self.power_up_available or not self.is_running:
            return
            
        if self.power_up_type == "slow":
            # Activate slow time for 5 seconds
            self.slow_time_active = True
            self.slow_time_remaining = 5
            GLib.timeout_add(1000, self._update_slow_time)
        elif self.power_up_type == "clear":
            # Clear all numbers from screen
            self.numbers = []
            self.drawing_area.queue_draw()
        elif self.power_up_type == "health":
            # Restore some health
            self.health = min(100, self.health + 30)
            self.health_label.set_text(f"{self.health}%")
            
        # Reset power-up
        self.power_up_available = False
        self.power_button.set_sensitive(False)
        self.power_button.set_label(_("Power-Up"))
    
    def _update_slow_time(self):
        if not self.is_running:
            self.slow_time_active = False
            return False
            
        self.slow_time_remaining -= 1
        
        if self.slow_time_remaining <= 0:
            self.slow_time_active = False
            return False
            
        return True
    
    def _check_level_up(self):
        if not self.is_running:
            return False
            
        if self.score >= self.next_level_score:
            self.level += 1
            self.level_label.set_text(str(self.level))
            
            # Increase difficulty
            self.number_speed_multiplier = 1.0 + (self.level - 1) * 0.2
            self.spawn_rate = max(700, 1500 - (self.level - 1) * 200)
            
            # Set next level threshold
            self.next_level_score = self.level * 100
            
            # Small health bonus on level up
            self.health = min(100, self.health + 10)
            self.health_label.set_text(f"{self.health}%")
            
            # Show level up message
            level_up_label = Gtk.Label()
            level_up_label.set_markup(f"<span weight='bold' size='x-large' color='#FFEB3B'>LEVEL UP!</span>")
            level_up_label.set_halign(Gtk.Align.CENTER)
            
            # Remove after 2 seconds
            def remove_level_up_label(label):
                self.game_screen.get_children()[0].remove(label)
                return False
                
            self.game_screen.get_children()[0].pack_start(level_up_label, False, False, 0)
            self.game_screen.show_all()
            GLib.timeout_add(2000, remove_level_up_label, level_up_label)
        
        return True
        
    def _add_number(self):
        if not self.is_running:
            return False
            
        # Get dimensions
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()
        
        # Create a new number
        value = random.randint(1, 20)
        x = 0  # Start at the left edge
        y = random.randint(int(Number.size), height - int(Number.size))  # Random vertical position
        
        # Adjust speed based on screen width, level, and slow time effect
        base_speed = random.uniform(width / 400, width / 200)
        if self.slow_time_active:
            speed = base_speed * self.number_speed_multiplier * 0.5  # Half speed when slow time active
        else:
            speed = base_speed * self.number_speed_multiplier
            
        # Add to the list
        new_number = Number(value, x, y, speed)
        new_number.size = Number.size  # Ensure the size is set for each number
        self.numbers.append(new_number)
        
        # Redraw
        self.drawing_area.queue_draw()
        
        # Continue the timeout with adaptive spawn rate
        GLib.timeout_add(self.spawn_rate, self._add_number)
        return False  # Don't repeat this timeout, we're scheduling a new one
        
    def _update_game(self):
        if not self.is_running:
            return False
            
        # Move all numbers
        width = self.drawing_area.get_allocated_width()
        for num in self.numbers[:]:  # Use a copy to safely remove while iterating
            num.move()
            
            # Remove numbers that go out of bounds
            if num.x > width + 20:
                # If a correct number leaves, reduce health
                if self._check_rule(num.value):
                    self.health -= 10
                    if self.health < 0:
                        self.health = 0
                    self.health_label.set_text(f"{self.health}%")
                    
                    # Break combo
                    self.combo_count = 0
                    self.combo_label.hide()
                    
                    if self.health <= 0:
                        self._end_game()
                        return False
                
                self.numbers.remove(num)
        
        # Redraw
        self.drawing_area.queue_draw()
        
        # Continue the timeout
        return True
        
    def _update_timer(self):
        if not self.is_running:
            return False
            
        self.game_time -= 1
        self.timer_label.set_text(str(self.game_time))
        
        if self.game_time <= 0:
            self._end_game()
            return False
            
        return True
        
    def _check_rule(self, value):
        if self.rule_type == "even":
            return value % 2 == 0
        elif self.rule_type == "prime":
            # Simple prime check
            if value < 2:
                return False
            for i in range(2, int(value**0.5) + 1):
                if value % i == 0:
                    return False
            return True
        elif self.rule_type == "multiple3":
            return value % 3 == 0
        return False
        
    def _end_game(self):
        self.is_running = False
        self._show_end_screen()
        
    def _stop_game(self):
        self.is_running = False
        
    def _cleanup(self, widget):
        self._stop_game()


# Define a base class for shared functionality - move this AFTER NumberNinjaActivity
class NumberNinjaBase:
    def _init_common(self):
        # Load background image for all subclasses
        self.bg_pixbuf = None
        try:
            self.bg_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                "/home/pranjalnegi/Maths-Games/assets/background.jpg", 800, 500, preserve_aspect_ratio=True)
        except Exception as e:
            print("Could not load background image:", e)
            
        # Set up title screen
        self._setup_title_screen()
        
        # Set up game screen
        self._setup_game_screen()
        
        # Set up end screen
        self._setup_end_screen()
        
        # Game variables
        self.numbers = []
        self.score = 0
        self.health = 100
        self.game_time = 60
        self.rule_type = "even"
        self.is_running = False
        
        # New gameplay variables
        self.level = 1
        self.combo_count = 0
        self.max_combo = 0
        self.number_speed_multiplier = 1.0
        self.spawn_rate = 1500  # ms between spawns
        self.next_level_score = 100  # Score needed for level 2
        self.last_correct_time = 0  # For tracking combo timing
        
        # Power-up variables
        self.slow_time_active = False
        self.slow_time_remaining = 0
        self.power_up_available = False
        self.power_up_type = None
        
        # Connect to size-allocate to handle resizing
        self.connect("size-allocate", self._on_resize)
        
        # Show title screen initially
        self._show_title_screen()
        
        self.connect("destroy", self._cleanup)
        
    def _on_resize(self, widget, allocation):
        # Update number size based on screen size
        if hasattr(self, 'drawing_area'):
            width = self.drawing_area.get_allocated_width()
            height = self.drawing_area.get_allocated_height()
            # Scale number size based on smaller dimension
            Number.size = min(width, height) / 12
            
            # Adjust existing numbers
            for num in self.numbers:
                num.size = Number.size
                
            # Queue redraw
            self.drawing_area.queue_draw()


class NumberNinjaStandalone(Gtk.Box, NumberNinjaBase):
    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.in_sugar = False

        # Apply CSS styling
        self._apply_css()
        
        # Set up toolbar
        toolbar_box = ToolbarBox()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()
        
        self.pack_start(toolbar_box, False, False, 0)
        toolbar_box.show()
        
        # Main container
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.set_name("number-ninja-window")
        self.pack_start(vbox, True, True, 0)
        
        # Create screens
        self.title_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.game_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.end_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        vbox.pack_start(self.title_screen, True, True, 0)
        vbox.pack_start(self.game_screen, True, True, 0)
        vbox.pack_start(self.end_screen, True, True, 0)
        
        # Initialize the custom activity_id for Sugar compatibility
        self.activity_id = None
        
        self._init_common()
        
    def _apply_css(self):
        NumberNinjaActivity._apply_css(self)

    # Implement methods by forwarding to NumberNinjaActivity methods
    def _setup_title_screen(self):
        NumberNinjaActivity._setup_title_screen(self)
        
    def _setup_game_screen(self):
        NumberNinjaActivity._setup_game_screen(self)
        
    def _setup_end_screen(self):
        NumberNinjaActivity._setup_end_screen(self)
        
    def _show_title_screen(self, widget=None):
        NumberNinjaActivity._show_title_screen(self, widget)
        
    def _show_game_screen(self):
        NumberNinjaActivity._show_game_screen(self)
        
    def _show_end_screen(self):
        NumberNinjaActivity._show_end_screen(self)
        
    def _on_start_game(self, widget):
        NumberNinjaActivity._on_start_game(self, widget)
        
    def _on_play_again(self, widget):
        NumberNinjaActivity._on_play_again(self, widget)
        
    def _on_draw(self, widget, context):
        NumberNinjaActivity._on_draw(self, widget, context)
        
    def _on_area_clicked(self, widget, event):
        NumberNinjaActivity._on_area_clicked(self, widget, event)
        
    def _add_number(self):
        return NumberNinjaActivity._add_number(self)
        
    def _update_game(self):
        return NumberNinjaActivity._update_game(self)
        
    def _update_timer(self):
        return NumberNinjaActivity._update_timer(self)
        
    def _check_rule(self, value):
        return NumberNinjaActivity._check_rule(self, value)
        
    def _end_game(self):
        NumberNinjaActivity._end_game(self)
        
    def _stop_game(self):
        NumberNinjaActivity._stop_game(self)
        
    def _cleanup(self, widget):
        NumberNinjaActivity._cleanup(self, widget)
        
    def _on_rule_changed(self, combo):
        NumberNinjaActivity._on_rule_changed(self, combo)
        
    # Add missing method forwarding for new gameplay features
    def _activate_power_up(self, widget):
        return NumberNinjaActivity._activate_power_up(self, widget)
        
    def _handle_correct_click(self):
        return NumberNinjaActivity._handle_correct_click(self)
        
    def _handle_wrong_click(self):
        return NumberNinjaActivity._handle_wrong_click(self)
        
    def _give_power_up(self):
        return NumberNinjaActivity._give_power_up(self)
        
    def _update_slow_time(self):
        return NumberNinjaActivity._update_slow_time(self)
        
    def _check_level_up(self):
        return NumberNinjaActivity._check_level_up(self)
        
    def _hsv_to_rgb(self, h, s, v):
        return NumberNinjaActivity._hsv_to_rgb(self, h, s, v)
        
if __name__ == '__main__':
    win = Gtk.Window()
    win.connect("destroy", Gtk.main_quit)
    win.set_default_size(600, 450)  # Slightly smaller default size
    win.set_title("Number Ninja")
    # Use standalone version when running directly
    activity = NumberNinjaStandalone()
    win.add(activity)
    win.show_all()
    
    Gtk.main()
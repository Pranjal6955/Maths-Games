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
        
        # Simple pastel color palette based on number value
        hue = (value * 25) % 360 / 360  # Use value to create different hues
        self.color = self._hsv_to_rgb(hue, 0.65, 0.95)
        
        self.alive = True
        self.pulse = 0  # For animation
        self.pulse_direction = 1
        # Minimal rotation for subtle movement
        self.rotation = random.uniform(-0.05, 0.05)
    
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
        # Subtle pulsing animation
        self.pulse += 0.08 * self.pulse_direction
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
        # Calculate size with subtle pulse effect
        pulse_size = self.size * (1 + self.pulse * 0.1)
        
        # Save context for rotation
        context.save()
        context.translate(self.x, self.y)
        context.rotate(self.rotation)
        
        # Draw the number bubble - with enhanced visual style
        r, g, b = self.color
        
        # Add a slight shadow for depth
        context.set_source_rgba(0, 0, 0, 0.15)
        context.arc(2, 3, pulse_size/2, 0, 2 * math.pi)
        context.fill()
        
        # Main circle - more vibrant gradient
        gradient = cairo.RadialGradient(
            -pulse_size/6, -pulse_size/6, 0,  # Inner point (offset for highlight)
            0, 0, pulse_size/2                # Outer point
        )
        gradient.add_color_stop_rgba(0, min(r+0.2, 1), min(g+0.2, 1), min(b+0.2, 1), 1)  # Lighter center
        gradient.add_color_stop_rgba(1, r, g, b, 1)                                      # Original color edge
        
        context.set_source(gradient)
        context.arc(0, 0, pulse_size/2, 0, 2 * math.pi)
        context.fill()
        
        # More subtle highlight
        context.set_line_width(2)
        context.set_source_rgba(1, 1, 1, 0.8)
        context.arc(0, 0, pulse_size/2 - 1, 0, math.pi)  # Half circle highlight
        context.stroke()
        
        # Draw the number text
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(pulse_size * 0.6)
        
        # Center the text
        text = str(self.value)
        x_bearing, y_bearing, width, height, x_advance, y_advance = context.text_extents(text)
        
        # Improved text with subtle shadow for better readability
        # Text shadow
        context.set_source_rgba(0, 0, 0, 0.25)
        context.move_to(-width / 2 - x_bearing + 1, -height / 2 - y_bearing + 1)
        context.show_text(text)
        
        # Text with contrast for readability
        context.set_source_rgb(1, 1, 1)  # White text
        context.move_to(-width / 2 - x_bearing, -height / 2 - y_bearing)
        context.show_text(text)
        
        # Restore context after rotation
        context.restore()

class NumberNinjaActivity(Gtk.Window):
    def __init__(self, handle):
        self.in_sugar = handle is not None
        
        if self.in_sugar:
            activity.Activity.__init__(self, handle)
        else:
            # Standalone mode initialization with modern UI elements
            Gtk.Window.__init__(self)
            self.set_title("Number Ninja")
            # Set window properties with 16:9 aspect ratio for better layout
            self.set_default_size(800, 600)
            self.set_size_request(640, 480)
            self.set_position(Gtk.WindowPosition.CENTER)
            self.set_resizable(True)
            self.connect("delete-event", Gtk.main_quit)
            
            # Set application icon
            try:
                self.set_icon_from_file("/home/pranjalnegi/Maths-Games/assets/number_ninja_icon.png")
            except:
                pass  # Icon loading is optional
            
        # Apply modernized CSS styling with animations
        self._apply_css()

        # Create main structure with header bar, content area, and navigation
        self.main_stack = Gtk.Stack()
        self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_stack.set_transition_duration(300)  # Smooth transitions

        if self.in_sugar:
            # Set up toolbar for Sugar with improved organization
            toolbar_box = ToolbarBox()
            activity_button = ActivityToolbarButton(self)
            toolbar_box.toolbar.insert(activity_button, 0)
            activity_button.show()
            
            # Add settings button
            settings_button = ToolButton('preferences-system')
            settings_button.set_tooltip(_("Game Settings"))
            settings_button.connect('clicked', self._show_settings)
            toolbar_box.toolbar.insert(settings_button, -1)
            settings_button.show()
            
            # Add help button
            help_button = ToolButton('help-browser')
            help_button.set_tooltip(_("How to Play"))
            help_button.connect('clicked', self._show_help)
            toolbar_box.toolbar.insert(help_button, -1)
            help_button.show()
            
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
        
        if self.in_sugar:
            self.set_canvas(vbox)
        else:
            self.add(vbox)
        
        # Create screens
        self.title_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.game_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.end_screen = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        
        vbox.pack_start(self.title_screen, True, True, 0)
        vbox.pack_start(self.game_screen, True, True, 0)
        vbox.pack_start(self.end_screen, True, True, 0)

        # Hide end screen and game screen initially
        self.title_screen.show_all()
        self.game_screen.hide()
        self.end_screen.hide()
        
        self._init_common()

    def _apply_css(self):
        css_provider = Gtk.CssProvider()
        css = """
        #number-ninja-window {
            background-image: linear-gradient(145deg, #f2f7fd 0%, #d8e9ff 100%);
            border-radius: 28px;
            box-shadow: 0 10px 40px rgba(35, 75, 150, 0.15);
            padding: 24px;
        }
        * {
            font-family: 'Poppins', 'Segoe UI', sans-serif;
        }
        .stat-frame {
            padding: 12px 0px 0px 0px;
            border-radius: 16px;
            background: linear-gradient(90deg, rgba(255,255,255,0.9) 0%, rgba(240,246,255,0.9) 100%);
            box-shadow: 0px 8px 20px rgba(60, 100, 177, 0.08);
            border: 2px solid #c8dbff;
        }
        .stat-title {
            font-size: 16px;
            font-weight: 600;
            color: #4284e0;
        }
        .stat-label {
            font-size: 24px;
            font-weight: bold;
            color: #1a56bb;
            text-shadow: 0px 1px 1px rgba(255,255,255,0.7);
        }
        .header-label {
            font-size: 36px;
            font-weight: 800;
            margin-bottom: 18px;
            font-family: 'Poppins', 'Segoe UI', sans-serif;
            color: #1a56bb;
            text-shadow: 0px 2px 2px rgba(255,255,255,0.9), 0px 4px 8px rgba(160,200,255,0.5);
        }
        .rule-label {
            font-size: 18px;
            font-weight: 600;
            color: #6200ee;
            background: linear-gradient(90deg, rgba(245,240,255,0.8) 0%, rgba(230,220,255,0.8) 100%);
            padding: 14px 18px;
            border-radius: 14px;
            border: 2px solid #d4c2f0;
            box-shadow: 0 3px 10px rgba(98,0,238,0.08);
            margin-top: 12px;
            margin-bottom: 12px;
        }
        .rule-frame, .result-frame {
            background: linear-gradient(145deg, #e8e0f7 0%, #d4c2f0 100%);
            border-radius: 18px;
            box-shadow: 0 8px 25px rgba(98,0,238,0.15);
            padding: 20px;
            border: 2px solid #c0a9e4;
        }
        .success-text {
            color: #04a777;
            font-weight: bold;
            background-color: #e6fff5;
            padding: 12px;
            border-radius: 12px;
            border-left: 4px solid #04a777;
        }
        .failure-text {
            color: #e53935;
            font-weight: bold;
            background-color: #ffeeee;
            padding: 12px;
            border-radius: 12px;
            border-left: 4px solid #e53935;
        }
        button {
            background-image: linear-gradient(135deg, #a4cbff 0%, #5b9dff 100%);
            color: #ffffff;
            border: none;
            border-radius: 16px;
            padding: 12px 22px;
            font-weight: 600;
            font-size: 16px;
            margin: 6px;
            box-shadow: 0px 4px 15px rgba(91, 157, 255, 0.25);
            text-shadow: 0px 1px 2px rgba(0,0,0,0.1);
        }
        button:hover {
            background-image: linear-gradient(135deg, #bbd7ff 0%, #7db1ff 100%);
        }
        button:active {
            box-shadow: 0px 2px 8px rgba(91, 157, 255, 0.2);
        }
        combobox {
            border-radius: 12px;
            padding: 8px;
            background-color: #f5f0ff;
            color: #6200ee;
            border: 2px solid #d4c2f0;
            box-shadow: 0 2px 8px rgba(98,0,238,0.08);
        }
        .combo-label {
            font-size: 18px;
            font-weight: 600;
            color: #ff6d00;
            background: linear-gradient(90deg, #fff8ed 0%, #fff2e0 100%);
            padding: 10px 18px;
            border-radius: 14px;
            border: 2px solid #ffcc80;
            box-shadow: 0 2px 8px rgba(255,109,0,0.1);
        }
        #drawing-area, drawingarea {
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(240,246,255,0.9) 100%);
            border-radius: 20px;
            border: 3px solid #7db1ff;
            box-shadow: inset 0px 2px 20px rgba(220, 230, 250, 0.8), 0px 5px 15px rgba(91, 157, 255, 0.15);
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
        
        # Gameplay variables
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
        # Center all content
        title_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        title_container.set_halign(Gtk.Align.CENTER)
        title_container.set_valign(Gtk.Align.CENTER)
        title_container.set_margin_top(40)
        title_container.set_margin_bottom(40)
        title_container.set_margin_start(30)
        title_container.set_margin_end(30)
        title_container.set_spacing(25)  # Add spacing between elementstle and button
        self.title_screen.pack_start(title_container, True, True, 0)

        # Logo label
        logo_label = Gtk.Label()
        logo_label.set_markup("<span weight='bold' size='xx-large' color='#1a56bb'>Number Ninja</span>")
        logo_label.get_style_context().add_class("header-label")
        title_container.pack_start(logo_label, False, False, 0)

        # Game mode selector in its own container  bottom
        mode_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        mode_container.set_halign(Gtk.Align.CENTER)R)
        mode_container.set_margin_top(20)("Start Game"))
        mode_container.set_margin_bottom(20)._on_start_game)
        button_container.pack_start(start_button, False, False, 0)
        # Rule selector labelstart(button_container, False, False, 0)
        rule_title = Gtk.Label(label=_("Select Game Mode:"))
        rule_title.set_halign(Gtk.Align.CENTER)
        rule_title.set_markup("<span weight='bold' size='large' color='#6200ee'>Select Game Mode:</span>")
        mode_container.pack_start(rule_title, False, False, 0)ERTICAL, spacing=10)
        game_container.set_margin_top(10)
        # Combo box in its own container(10)
        combo_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        combo_container.set_halign(Gtk.Align.CENTER)
        self.rule_combo = Gtk.ComboBoxText()tainer, True, True, 0)
        self.rule_combo.append_text(_("Even Numbers"))
        self.rule_combo.append_text(_("Prime Numbers"))
        self.rule_combo.append_text(_("Multiples of 3"))
        self.rule_combo.set_active(0)  # Default to even numbersarge' color='#FF9800'>Combo: 0</span>")
        self.rule_combo.connect("changed", self._on_rule_changed)
        combo_container.pack_start(self.rule_combo, False, False, 0)
        mode_container.pack_start(combo_container, False, False, 10)
        # Game area (Drawing area)
        # Show rule label below selector with better spacing
        self.rule_preview_label = Gtk.Label()Type.NONE)
        self.rule_preview_label.get_style_context().add_class("rule-label")
        self.rule_preview_label.set_halign(Gtk.Align.CENTER)
        mode_container.pack_start(self.rule_preview_label, False, False, 10)
        self._on_rule_changed(self.rule_combo)  # Set initial rule previewked)
        self.drawing_area.set_hexpand(True)
        # Instructionsrea.set_vexpand(True)
        instructions = Gtk.Label()g_area)
        instructions.set_markup(_("<span color='black'>Click only on numbers that match the rule!</span>"))
        instructions.set_halign(Gtk.Align.CENTER)e, True, 0)
        mode_container.pack_start(instructions, False, False, 0)
        # Current rule display
        title_container.pack_start(mode_container, False, False, 0)spacing=10)
        rule_box.set_halign(Gtk.Align.CENTER)
        # Start button in its own container at the bottom
        button_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_container.set_halign(Gtk.Align.CENTER)d'>Rule: Click on even numbers</span>")
        button_container.set_margin_top(30).add_class("rule-label")
        start_button = Gtk.Button(label=_("Start Game"))e, 0)
        start_button.connect("clicked", self._on_start_game)
        button_container.pack_start(start_button, False, False, 0)
        title_container.pack_start(button_container, False, False, 0)
    def _setup_end_screen(self):
    def _on_rule_changed(self, combo):everything
        rule_index = combo.get_active()tion=Gtk.Orientation.VERTICAL, spacing=15)
        if rule_index == 0:align(Gtk.Align.CENTER)
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        elif rule_index == 1:start(end_container, True, True, 0)
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on prime numbers</span>")
        else:ult frame (removed Game Over text)
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on multiples of 3</span>")
        result_frame.set_shadow_type(Gtk.ShadowType.NONE)
    def _setup_game_screen(self):ntext().add_class("result-frame")
        # Game screen containerientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        game_container.set_margin_top(10)
        game_container.set_margin_bottom(10)
        game_container.set_margin_start(10)
        game_container.set_margin_end(10)
        self.game_screen.pack_start(game_container, True, True, 0)
        self.final_score_label = Gtk.Label()
        # Combo indicatorlabel.set_markup("<span size='large'>Your score: 0</span>")
        self.combo_label = Gtk.Label()al_score_label, False, False, 5)
        self.combo_label.set_markup("<span weight='bold' size='large' color='#FF9800'>Combo: 0</span>")
        self.combo_label.set_no_show_all(True)  # Hide initially
        game_container.pack_start(self.combo_label, False, False, 5)
        self.final_level_label.set_markup("<span>Highest Level: 1</span>")
        # Game area (Drawing area).final_level_label, False, False, 5)
        game_frame = Gtk.Frame()
        game_frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.drawing_area = Gtk.DrawingArea()pan>Max Combo: 0</span>")
        self.drawing_area.connect("draw", self._on_draw)lse, False, 5)
        self.drawing_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self._on_area_clicked)
        self.drawing_area.set_hexpand(True)me, False, False, 15)
        self.drawing_area.set_vexpand(True)
        game_frame.add(self.drawing_area)
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        game_container.pack_start(game_frame, True, True, 0)
        
        # Current rule display
        rule_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        rule_box.set_halign(Gtk.Align.CENTER)self._on_play_again)
        buttons_box.pack_start(play_again_button, False, False, 0)
        self.rule_label = Gtk.Label()
        self.rule_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        self.rule_label.get_style_context().add_class("rule-label")
        rule_box.pack_start(self.rule_label, False, False, 0)en)
        buttons_box.pack_start(title_button, False, False, 0)
        game_container.pack_start(rule_box, False, False, 10)
        end_container.pack_start(buttons_box, False, False, 10)
    def _setup_end_screen(self):
        # End game container - center everything
        end_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        end_container.set_halign(Gtk.Align.CENTER)
        end_container.set_valign(Gtk.Align.CENTER)
        self.end_screen.pack_start(end_container, True, True, 0)
        # Stop any running game
        # Result frame (removed Game Over text)
        result_frame = Gtk.Frame()
        result_frame.set_shadow_type(Gtk.ShadowType.NONE)
        result_frame.get_style_context().add_class("result-frame")
        result_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        result_box.set_margin_top(15)
        result_box.set_margin_bottom(15)
        result_box.set_margin_start(30)
        result_box.set_margin_end(30)
        self.title_screen.hide()
        # Final scoreeen.hide()
        self.final_score_label = Gtk.Label()
        self.final_score_label.set_markup("<span size='large'>Your score: 0</span>")
        result_box.pack_start(self.final_score_label, False, False, 5)
        self.final_score_label.set_markup(f"<span>Your score: {self.score}</span>")
        # Max level and combol.set_markup(f"<span>Highest Level: {self.level}</span>")
        self.final_level_label = Gtk.Label()<span>Max Combo: {self.max_combo}</span>")
        self.final_level_label.set_markup("<span>Highest Level: 1</span>")
        result_box.pack_start(self.final_level_label, False, False, 5)
        if self.health > 0:
        self.final_combo_label = Gtk.Label()_context().add_class("success-text")
        self.final_combo_label.set_markup("<span>Max Combo: 0</span>")
        result_box.pack_start(self.final_combo_label, False, False, 5)ure-text")
        
        result_frame.add(result_box):
        end_container.pack_start(result_frame, False, False, 15)
        rule_index = self.rule_combo.get_active()
        # Buttons container
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        buttons_box.set_halign(Gtk.Align.CENTER)ight='bold'>Rule: Click on even numbers</span>")
        elif rule_index == 1:
        # Play again button= "prime"
        play_again_button = Gtk.Button(label=_("Play Again"))ule: Click on prime numbers</span>")
        play_again_button.connect("clicked", self._on_play_again)
        buttons_box.pack_start(play_again_button, False, False, 0)
            self.rule_label.set_markup("<span weight='bold'>Rule: Click on multiples of 3</span>")
        # Return to title button
        title_button = Gtk.Button(label=_("Return to Title"))
        title_button.connect("clicked", self._show_title_screen)
        buttons_box.pack_start(title_button, False, False, 0)
        self.health = 100
        end_container.pack_start(buttons_box, False, False, 10)
        self.level = 1
    def _show_title_screen(self, widget=None):
        self.title_screen.show_all()
        self.game_screen.hide()plier = 1.0
        self.end_screen.hide()
        self.next_level_score = 100
        # Stop any running game False
        if self.is_running:able = False
            self._stop_game()None
        self.combo_label.hide()
    def _show_game_screen(self):
        self.title_screen.hide()number size based on screen dimensions
        self.game_screen.show_all()et_allocated_width()
        self.end_screen.hide()area.get_allocated_height()
        Number.size = min(width, height) / 12
    def _show_end_screen(self):
        self.title_screen.hide()
        self.game_screen.hide()xt(_("0"))
        self.end_screen.show_all()_("60"))
        self.health_label.set_text(_("100%"))
        # Update final score and stats"))
        self.final_score_label.set_markup(f"<span>Your score: {self.score}</span>")
        self.final_level_label.set_markup(f"<span>Highest Level: {self.level}</span>")
        self.final_combo_label.set_markup(f"<span>Max Combo: {self.max_combo}</span>")
        
        # Add success/failure style
        if self.health > 0:rue
            self.final_score_label.get_style_context().add_class("success-text")
        else:timeout_add(50, self._update_game)     # Update game every 50ms
            self.final_score_label.get_style_context().add_class("failure-text")current spawn rate
        GLib.timeout_add(500, self._check_level_up)   # Check for level up every 0.5 seconds
    def _on_start_game(self, widget):
        # Use default rule (even numbers) since we removed the selector, widget):
        self.rule_type = "even"
        self.rule_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        ext):
        # Reset game variables
        self.numbers = []located_width()
        self.score = 0d_height()
        self.health = 100
        self.game_time = 60an white background
        self.level = 17, 0.97)  # Very light gray
        self.combo_count = 0
        self.max_combo = 0context.fill()
        self.number_speed_multiplier = 1.0
        self.spawn_rate = 1500 lines for visual guidance
        self.next_level_score = 100urce_rgba(0, 0, 0, 0.03)
        self.slow_time_active = Falsewidth(1)
        self.power_up_available = False
        self.power_up_type = Noneines
        self.combo_label.hide()ight, 20):
o(0, y)
        # Calculate appropriate number size based on screen dimensions
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()
        Number.size = min(width, height) / 12
        
        # Update labelsight)
        self.score_label.set_text(_("0"))
        self.timer_label.set_text(_("60"))        context.stroke()
        self.health_label.set_text(_("100%"))
        self.level_label.set_text(_("1"))
        
        # Show game screen 0.9, 0.05)
        self._show_game_screen()    context.rectangle(0, 0, width, height)
        l()
        # Start the game loop
        self.is_running = True
        GLib.timeout_add(1000, self._update_timer)  # Update timer every second
        GLib.timeout_add(50, self._update_game)     # Update game every 50ms
        GLib.timeout_add(self.spawn_rate, self._add_number)    # Add numbers at current spawn rate
        GLib.timeout_add(500, self._check_level_up)   # Check for level up every 0.5 secondself, widget, event):
        
    def _on_play_again(self, widget):    return
        self._show_title_screen()
        was clicked
    def _on_draw(self, widget, context):ing
        # Get the dimensions of the drawing area
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
                    # Correct click
        # Clean white backgroundect_click(num)
        context.set_source_rgb(0.97, 0.97, 0.97)  # Very light gray
        context.rectangle(0, 0, width, height)            # Incorrect click
        context.fill()ct_click(num)
        click
        # Add subtle grid lines for visual guidance
        context.set_source_rgba(0, 0, 0, 0.03)
        context.set_line_width(1)# Remove the number from the game
        
        # Horizontal lines
        for y in range(0, height, 20):
            context.move_to(0, y)self.level
            context.line_to(width, y)
        
        # Vertical lines() / 1000000  # Convert to seconds
        for x in range(0, width, 20):nd current_time - self.last_correct_time < 2.0:
            context.move_to(x, 0)    self.combo_count += 1
            context.line_to(x, height)combo bonus
         (self.combo_count * 0.1))
        context.stroke()
        
        # Draw slow time effect - subtle blue tint    # Show combo indicator
        if self.slow_time_active:abel.set_markup(f"<span weight='bold' size='large' color='#FF9800'>Combo: {self.combo_count}x</span>")
            context.set_source_rgba(0.2, 0.4, 0.9, 0.05)
            context.rectangle(0, 0, width, height)
            context.fill()
            self.combo_count = 1
        # Draw all numbersabel.hide()
        for num in self.numbers:
            num.draw(context)
    f.max_combo:
    def _on_area_clicked(self, widget, event):
        if not self.is_running:
            returnrrect click for combo calculation
        self.last_correct_time = current_time
        # Check if any number was clicked
        for num in self.numbers[:]:  # Use a copy to safely remove while iterating
            if num.is_clicked(event.x, event.y):
                # Check if the number matches the rule    self.score_label.set_text(str(self.score))
                if self._check_rule(num.value):
                    # Correct clickailability
                    self._handle_correct_click(num)f.power_up_available and self.combo_count >= 5:
                else:    self._make_power_up_available()
                    # Incorrect click
                    self._handle_incorrect_click(num)
                return  # Exit after handling a click
    
    def _handle_correct_click(self, num):
        # Remove the number from the game
        self.numbers.remove(num)
        
        # Update score based on level
        points = 10 * self.level
        
        # Add combo bonus if applicable    
        current_time = GLib.get_monotonic_time() / 1000000  # Convert to seconds
        if self.combo_count > 0 and current_time - self.last_correct_time < 2.0:- 10)
            self.combo_count += 1xt(f"{self.health}%")
            # Exponential combo bonus
            combo_bonus = int(points * (self.combo_count * 0.1))
            points += combo_bonus
                self._end_game()
            # Show combo indicator
            self.combo_label.set_markup(f"<span weight='bold' size='large' color='#FF9800'>Combo: {self.combo_count}x</span>")
            self.combo_label.show()
        else:
            # Start new combo
            self.combo_count = 1
            self.combo_label.hide()
         self.rule_type == "prime":
        # Update max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
            or i in range(2, int(math.sqrt(value)) + 1):
        # Track time of correct click for combo calculation== 0:
        self.last_correct_time = current_time
        
        # Update scoreelif self.rule_type == "multiple3":
        self.score += points 3 == 0
        self.score_label.set_text(str(self.score))
        
        # Check for power-up availabilitye_power_up_available(self):
        if not self.power_up_available and self.combo_count >= 5:
            self._make_power_up_available()slow", "health", "clear"])
        
        # Queue redraw was removed, so we automatically apply the power-up
        self.drawing_area.queue_draw()_up(None)
        
    def _handle_incorrect_click(self, num):_activate_power_up(self, widget):
        # Remove the number
        self.numbers.remove(num)
        
        # Reset comboif self.power_up_type == "slow":
        self.combo_count = 0 slow time effect
        self.combo_label.hide()ue
            self.slow_time_remaining = 5  # 5 seconds of slow time
        # Reduce health
        self.health = max(0, self.health - 10)fect to all numbers
        self.health_label.set_text(f"{self.health}%")ers:
                num.speed *= 0.5
        # Check for game over
        if self.health <= 0:f slow time
            self._end_game()conds(5, self._end_slow_time) # 5 seconds of slow time
                    
        # Queue redraw_up_type == "health":
        self.drawing_area.queue_draw()
        
    def _check_rule(self, value):    
        if self.rule_type == "even":pe == "clear":
            return value % 2 == 0orrect numbers
        elif self.rule_type == "prime":numbers[:]:
            # Simple prime check    if not self._check_rule(num.value):
            if value < 2:lf.numbers.remove(num)
                return False
            for i in range(2, int(math.sqrt(value)) + 1):# Reset power-up
                if value % i == 0: False
                    return False
            return True
        elif self.rule_type == "multiple3":
            return value % 3 == 0
        return Falself):
        ng:
    def _make_power_up_available(self):
        self.power_up_available = True
        self.power_up_type = random.choice(["slow", "health", "clear"])False
        
        # Power button was removed, so we automatically apply the power-up
        self._activate_power_up(None)
        d *= 2.0
    def _activate_power_up(self, widget):
        if not self.power_up_available:
            return
        
        if self.power_up_type == "slow":
            # Activate slow time effect
            self.slow_time_active = True
            self.slow_time_remaining = 5  # 5 seconds of slow time    return False
            
            # Apply slow effect to all numbers
            for num in self.numbers: self.numbers[:]:  # Use a copy to safely remove while iterating
                num.speed *= 0.5    num.move()
                
            # Schedule end of slow timescreen
            GLib.timeout_add_seconds(5, self._end_slow_time) # 5 seconds of slow time.get_allocated_width() + num.size:
                
        elif self.power_up_type == "health":    
            # Restore healthpenalize
            self.health = min(100, self.health + 30)num.value):
            = max(0, self.health - 5)
        elif self.power_up_type == "clear":    self.health_label.set_text(f"{self.health}%")
            # Remove all incorrect numbers
            for num in self.numbers[:]:
                if not self._check_rule(num.value):    if self.health <= 0:
                    self.numbers.remove(num)
        rn False
        # Reset power-up
        self.power_up_available = Falseeue redraw
        
        # Queue redraw
        self.drawing_area.queue_draw()
        
    def _end_slow_time(self):
        if not self.is_running:    return False
            return False
        
        self.slow_time_active = Falsewidth = self.drawing_area.get_allocated_width()
        drawing_area.get_allocated_height()
        # Return numbers to normal speed
        for num in self.numbers:if width == 0 or height == 0:  # Not yet realized
            num.speed *= 2.0
        
        # Queue redrawumber
        self.drawing_area.queue_draw()value = random.randint(1, 20)
        return False  # Don't repeat
        # Calculate spawn position and speed
    def _update_game(self):
        if not self.is_running:r.size, height - Number.size)
            return False
            # Speed increases with level
        # Move all numbers.0 * self.number_speed_multiplier
        for num in self.numbers[:]:  # Use a copy to safely remove while iterating
            num.move()ed
            speed = base_speed * random.uniform(0.8, 1.2)
            # Check if number went off screen
            if num.x > self.drawing_area.get_allocated_width() + num.size:
                self.numbers.remove(num)e_active:
                speed *= 0.5
                # If it was a correct number, penalize
                if self._check_rule(num.value):
                    self.health = max(0, self.health - 5)umber(value, x, y, speed)
                    self.health_label.set_text(f"{self.health}%")number.size = Number.size  # Update with current size
                    
                    # Check for game over
                    if self.health <= 0:
                        self._end_game()rue
                        return False
        
        # Queue redraw
        self.drawing_area.queue_draw()
        return True  # Continue updating
        
    def _add_number(self):lf.game_time))
        if not self.is_running:
            return False
                self._end_game()
        # Get dimensionsse
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()
        
        if width == 0 or height == 0:  # Not yet realizedlf):
            return True
        
        # Create a new number
        value = random.randint(1, 20) self.next_level_score:
        
        # Calculate spawn position and speed
        x = -Number.size    self.level_label.set_text(str(self.level))
        y = random.uniform(Number.size, height - Number.size)
        xt level threshold
        # Speed increases with level    self.next_level_score = self.next_level_score + (self.level * 100)
        base_speed = 2.0 * self.number_speed_multiplier
        
        # Add some randomness to speed    self.number_speed_multiplier += 0.2
        speed = base_speed * random.uniform(0.8, 1.2)
        pawn rate (reduce time between spawns)
        # Slow time effect
        if self.slow_time_active:    
            speed *= 0.5
        umber)  # Remove old timer
        # Create and add the number    GLib.timeout_add(self.spawn_rate, self._add_number)
        new_number = Number(value, x, y, speed)
        new_number.size = Number.size  # Update with current size
        self.numbers.append(new_number)
        
        # Schedule next number spawn
        return Truecreen()
        
    def _update_timer(self):
        if not self.is_running:
            return False
            
        self.game_time -= 1if self.is_running:
        self.timer_label.set_text(str(self.game_time))
        
        if self.game_time <= 0:run_standalone(self):
            self._end_game()standalone, outside of Sugar."""
            return False()
            
        return True  # Continue timer.maximize()
        
    def _check_level_up(self):
        if not self.is_running:e__ == "__main__":
            return Falsealone mode
            ty(None)
        if self.score >= self.next_level_score:)            # Level up!            self.level += 1            self.level_label.set_text(str(self.level))                        # Update next level threshold            self.next_level_score = self.next_level_score + (self.level * 100)                        # Increase difficulty            self.number_speed_multiplier += 0.2                        # Increase spawn rate (reduce time between spawns)            self.spawn_rate = max(800, self.spawn_rate - 150)                        # Apply new spawn rate            GLib.source_remove_by_user_data(self._add_number)  # Remove old timer            GLib.timeout_add(self.spawn_rate, self._add_number)                    return True  # Continue checking            def _end_game(self):        self.is_running = False        self._show_end_screen()            def _stop_game(self):        self.is_running = False            def _cleanup(self, widget):        if self.is_running:            self._stop_game()                def run_standalone(self):        """Run the activity standalone, outside of Sugar."""        self._show_title_screen()        self.show_all()        self.maximize()        Gtk.main()if __name__ == "__main__":    # Run the activity in standalone mode    game = NumberNinjaActivity(None)    game.run_standalone()
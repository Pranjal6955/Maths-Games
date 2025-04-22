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
        self.color = (0.1, 0.1, 0.1)  # Dark gray
        self.alive = True
        
    def move(self):
        self.x += self.speed
        
    def is_clicked(self, click_x, click_y):
        # Check if the click is inside the number
        distance = math.sqrt((self.x - click_x)**2 + (self.y - click_y)**2)
        return distance < self.size / 2
        
    def draw(self, context):
        # Draw a circle
        context.set_source_rgb(0.8, 0.8, 0.8)  # Light gray background
        context.arc(self.x, self.y, self.size / 2, 0, 2 * math.pi)
        context.fill()
        
        # Draw the number
        context.set_source_rgb(*self.color)
        context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        context.set_font_size(self.size * 0.6)
        
        # Center the text
        text = str(self.value)
        x_bearing, y_bearing, width, height, x_advance, y_advance = context.text_extents(text)
        context.move_to(self.x - width / 2 - x_bearing, self.y - height / 2 - y_bearing)
        context.show_text(text)

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
        .stat-label {
            font-size: 16px;
            font-weight: bold;
            color: #000;
        }
        .header-label {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
            font-family: 'Sans', serif;
            color: #000;
        }
        .rule-label {
            font-size: 16px;
            font-weight: bold;
            color: #6a1b9a;
            background: linear-gradient(90deg, #fff8e1 60%, #f3e5f5 100%);
            padding: 8px 12px;
            border-radius: 10px;
            border: 1px dashed #ba68c8;
            box-shadow: 0 2px 8px rgba(186,104,200,0.08);
            margin-top: 5px;
            margin-bottom: 5px;
        }
        .success-text {
            color: #00bb00;
            font-weight: bold;
            background-color: #eafff5;
            padding: 8px;
            border-radius: 8px;
        }
        .failure-text {
            color: #ff0000;
            font-weight: bold;
            background-color: #fff0f0;
            padding: 8px;
            border-radius: 8px;
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
        
        # Logo label
        logo_label = Gtk.Label()
        logo_label.set_markup("<span weight='bold' foreground='#3E7D1C'>Number Ninja</span>")
        logo_label.get_style_context().add_class("header-label")
        self.title_screen.pack_start(logo_label, False, False, 10)
        
        # Rule selector in a more compact layout
        rule_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        rule_label = Gtk.Label(label=_("Select:"))
        rule_box.pack_start(rule_label, False, False, 5)
        
        self.rule_combo = Gtk.ComboBoxText()
        self.rule_combo.append_text(_("Even Numbers"))
        self.rule_combo.append_text(_("Prime Numbers"))
        self.rule_combo.append_text(_("Multiples of 3"))
        self.rule_combo.set_active(0)  # Default to even numbers
        self.rule_combo.connect("changed", self._on_rule_changed)  # Connect signal
        rule_box.pack_start(self.rule_combo, True, True, 0)
        
        self.title_screen.pack_start(rule_box, False, False, 5)
        
        # Instructions
        instructions = Gtk.Label()
        instructions.set_markup(_("<span>Click only on numbers that match the rule!</span>"))
        self.title_screen.pack_start(instructions, False, False, 5)
        
        # Show rule label below selector
        self.rule_preview_label = Gtk.Label()
        self.rule_preview_label.get_style_context().add_class("rule-label")
        self.title_screen.pack_start(self.rule_preview_label, False, False, 5)
        self._on_rule_changed(self.rule_combo)  # Set initial rule preview
        
        # Start button
        start_button = Gtk.Button(label=_("Start Game"))
        start_button.connect("clicked", self._on_start_game)
        self.title_screen.pack_start(start_button, False, False, 10)

    def _on_rule_changed(self, combo):
        rule_index = combo.get_active()
        if rule_index == 0:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        elif rule_index == 1:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on prime numbers</span>")
        else:
            self.rule_preview_label.set_markup("<span weight='bold'>Rule: Click on multiples of 3</span>")

    def _setup_game_screen(self):
        # Top bar with frames for stats (more compact)
        top_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        top_bar.set_hexpand(True)
        top_bar.set_vexpand(False)
        top_bar.set_homogeneous(True)

        # Score
        score_frame = Gtk.Frame(label="Score")
        score_frame.set_label_align(0.5, 0.5)
        score_frame.get_style_context().add_class("stat-frame")
        self.score_label = Gtk.Label(label=_("0"))
        self.score_label.get_style_context().add_class("stat-label")
        score_frame.add(self.score_label)
        top_bar.pack_start(score_frame, True, True, 0)

        # Timer
        timer_frame = Gtk.Frame(label="Time")
        timer_frame.set_label_align(0.5, 0.5)
        timer_frame.get_style_context().add_class("stat-frame")
        self.timer_label = Gtk.Label(label=_("60"))
        self.timer_label.get_style_context().add_class("stat-label")
        timer_frame.add(self.timer_label)
        top_bar.pack_start(timer_frame, True, True, 0)

        # Health
        health_frame = Gtk.Frame(label="Health")
        health_frame.set_label_align(0.5, 0.5)
        health_frame.get_style_context().add_class("stat-frame")
        self.health_label = Gtk.Label(label=_("100%"))
        self.health_label.get_style_context().add_class("stat-label")
        health_frame.add(self.health_label)
        top_bar.pack_start(health_frame, True, True, 0)

        self.game_screen.pack_start(top_bar, False, False, 5)
        
        # Game area (Drawing area)
        self.drawing_area = Gtk.DrawingArea()
        # Let it adapt to available space instead of fixed size
        self.drawing_area.connect("draw", self._on_draw)
        self.drawing_area.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button-press-event", self._on_area_clicked)
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        
        self.game_screen.pack_start(self.drawing_area, True, True, 0)
        
        # Current rule display
        self.rule_label = Gtk.Label()
        self.rule_label.set_markup("<span weight='bold'>Rule: Click on even numbers</span>")
        self.rule_label.get_style_context().add_class("rule-label")
        self.game_screen.pack_start(self.rule_label, False, False, 5)
        
    def _setup_end_screen(self):
        # End game title
        end_title = Gtk.Label()
        end_title.set_markup("<span weight='bold'>Game Over!</span>")
        end_title.get_style_context().add_class("header-label")
        self.end_screen.pack_start(end_title, False, False, 10)
        
        # Final score
        self.final_score_label = Gtk.Label()
        self.final_score_label.set_markup("<span>Your score: 0</span>")
        self.end_screen.pack_start(self.final_score_label, False, False, 5)
        
        # Play again button
        play_again_button = Gtk.Button(label=_("Play Again"))
        play_again_button.connect("clicked", self._on_play_again)
        self.end_screen.pack_start(play_again_button, False, False, 5)
        
        # Return to title button
        title_button = Gtk.Button(label=_("Return to Title"))
        title_button.connect("clicked", self._show_title_screen)
        self.end_screen.pack_start(title_button, False, False, 5)
        
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
        
        # Update final score
        self.final_score_label.set_markup(f"<span>Your score: {self.score}</span>")
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

        # Calculate appropriate number size based on screen dimensions
        width = self.drawing_area.get_allocated_width()
        height = self.drawing_area.get_allocated_height()
        Number.size = min(width, height) / 12
        
        # Update labels
        self.score_label.set_text(_("0"))
        self.timer_label.set_text(_("60"))
        self.health_label.set_text(_("100%"))
        
        # Show game screen
        self._show_game_screen()
        
        # Start the game loop
        self.is_running = True
        GLib.timeout_add(1000, self._update_timer)  # Update timer every second
        GLib.timeout_add(50, self._update_game)     # Update game every 50ms
        GLib.timeout_add(1500, self._add_number)    # Add a new number every 1.5 seconds
        
    def _on_play_again(self, widget):
        self._show_title_screen()
        
    def _on_draw(self, widget, context):
        # Get the dimensions of the drawing area
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        
        # Draw background image if loaded, else fallback to color
        if self.bg_pixbuf:
            # Scale image to fit the drawing area
            scaled = self.bg_pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
            Gdk.cairo_set_source_pixbuf(context, scaled, 0, 0)
            context.paint()
        else:
            context.set_source_rgb(0.9, 0.9, 1.0)  # Light blue background
            context.rectangle(0, 0, width, height)
            context.fill()
        
        # Draw all numbers
        for num in self.numbers:
            num.draw(context)
            
    def _on_area_clicked(self, widget, event):
        if not self.is_running:
            return
            
        # Check if any number was clicked
        for num in self.numbers[:]:  # Use a copy to safely remove while iterating
            if num.is_clicked(event.x, event.y):
                # Check if the number matches the rule
                if self._check_rule(num.value):
                    # Correct click
                    self.score += 10
                    self.score_label.set_text(_("Score: {}").format(self.score))
                else:
                    # Wrong click
                    self.health -= 20
                    if self.health < 0:
                        self.health = 0
                    self.health_label.set_text(_("Health: {}%").format(self.health))
                    
                    if self.health <= 0:
                        self._end_game()
                
                # Remove the number
                self.numbers.remove(num)
                self.drawing_area.queue_draw()
                break
                
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
        
        # Adjust speed based on screen width for consistent gameplay
        speed = random.uniform(width / 400, width / 200)
        
        # Add to the list
        new_number = Number(value, x, y, speed)
        new_number.size = Number.size  # Ensure the size is set for each number
        self.numbers.append(new_number)
        
        # Redraw
        self.drawing_area.queue_draw()
        
        # Continue the timeout
        return True
        
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
                    self.health_label.set_text(_("Health: {}%").format(self.health))
                    
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
        self.timer_label.set_text(_("Time: {}").format(self.game_time))
        
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
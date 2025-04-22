from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics.toolbutton import ToolButton

from gi.repository import Gtk, Gdk, GLib
import os
import subprocess
import threading
import time
import random

class MathGamesActivity(activity.Activity):

    def __init__(self, handle):
        super().__init__(handle)
        self.set_title("Math Games")

        # Set up toolbar
        toolbar_box = ToolbarBox()
        self.set_toolbar_box(toolbar_box)

        stop_button = ToolButton('activity-stop')
        stop_button.connect('clicked', self.__quit_cb)
        toolbar_box.toolbar.insert(stop_button, -1)
        toolbar_box.show_all()

        # Main layout container
        main_vbox = Gtk.VBox(spacing=20)
        main_vbox.set_border_width(20)
        main_vbox.set_name("math-games-window")

        # Animated emoji in header (simulate with changing emoji)
        header_frame = Gtk.Frame()
        header_frame.set_shadow_type(Gtk.ShadowType.NONE)
        header_label = Gtk.Label()
        header_label.set_markup(
            "<span font='32' weight='ultrabold' foreground='#ffffff'>🧮 Maths Games for Kids! <span>🎲</span></span>"
        )
        header_label.set_padding(15, 15)
        header_event = Gtk.EventBox()
        header_event.modify_bg(Gtk.StateFlags.NORMAL, Gdk.color_parse('#5b6ee1'))  # blue header
        header_event.add(header_label)
        header_frame.add(header_event)
        main_vbox.pack_start(header_frame, False, False, 0)

        # Fun emoji row above the grid
        emoji_row = Gtk.Label()
        emoji_row.set_markup(
            "<span font='28'>🎲 🧩 🧮 🗺️ 📐 ✨ 🥷🏻</span>"
        )
        main_vbox.pack_start(emoji_row, False, False, 0)

        # Grid layout for game buttons
        game_grid = Gtk.Grid()
        game_grid.set_row_spacing(20)
        game_grid.set_column_spacing(20)
        game_grid.set_border_width(10)
        game_grid.set_halign(Gtk.Align.CENTER)
        game_grid.set_valign(Gtk.Align.CENTER)

        game_list = [
            ("💣 Math Minesweeper", "games/math_minesweeper.py"),
            ("🧮 Broken Calculator", "games/broken_calculator.py"),
            ("🧩 Fifteen Puzzle", "games/fifteen_puzzle.py"),
            ("📐 Euclid's Game", "games/euclids_game.py"),
            ("🎲 Odd Scoring" , "games/OddScoring.py"),
            ("🥷🏻 Number Ninja  ", "games/number_ninja.py"),
        ]

        # Place buttons in a 2x2 grid
        self.buttons = []
        for idx, (name, path) in enumerate(game_list):
            button = Gtk.Button(label=name)
            button.connect("clicked", self.launch_game, path)
            button.set_size_request(200, 90)
            button.get_style_context().add_class("game-button")
            row, col = divmod(idx, 2)
            game_grid.attach(button, col, row, 1, 1)
            self.buttons.append((button, path))

        # Add Random Game button below the grid
        random_button = Gtk.Button(label="🎲 Random Game")
        random_button.set_size_request(200, 60)
        random_button.get_style_context().add_class("random-button")
        random_button.connect("clicked", self.launch_random_game)
        # Place random button below the grid, centered
        random_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        random_button_box.set_halign(Gtk.Align.CENTER)
        random_button_box.pack_start(random_button, False, False, 0)

        main_vbox.pack_start(game_grid, True, True, 0)
        main_vbox.pack_start(random_button_box, False, False, 0)

        # Tip of the Day
        tip_label = Gtk.Label()
        tip_label.set_markup(
            "<span font='15' foreground='#8f5be1'><b>Tip of the Day:</b> Try to beat your best time in the Fifteen Puzzle! 🕒</span>"
        )
        tip_label.set_justify(Gtk.Justification.CENTER)
        main_vbox.pack_start(tip_label, False, False, 0)

        # Friendly, colorful footer
        footer_label = Gtk.Label()
        footer_label.set_markup(
            "<span font='16' foreground='#ffffff' background='#8f5be1' style='italic'>🌈 Have fun learning maths! 🎉</span>"
        )
        main_vbox.pack_end(footer_label, False, False, 0)

        # Apply styles
        self.apply_css()

        self.set_canvas(main_vbox)
        main_vbox.show_all()

        # Animate header emoji (simulate by changing emoji every second)
        threading.Thread(target=self.animate_emoji, args=(header_label,), daemon=True).start()

    def animate_emoji(self, header_label):
        # Fix: Use GLib.idle_add instead of Gtk.idle_add
        # Also remove the id attribute which is causing an error
        emojis = ["🎲", "🧩", "🔢", "🎯", "🧮", "📏"]
        i = 0
        while True:
            emoji = emojis[i % len(emojis)]
            header_markup = f"<markup><span font='32' weight='ultrabold' foreground='#ffffff'>🧮 Maths Games for Kids! <span>{emoji}</span></span></markup>"
            GLib.idle_add(header_label.set_markup, header_markup)
            time.sleep(2)
            i += 1

    def launch_game(self, button, path):
        script_path = os.path.join(os.path.dirname(__file__), path)
        # Use Python's module importing mechanism instead of subprocess
        # This ensures that the game's environment is properly set up
        try:
            # Change directory to ensure relative paths work
            original_dir = os.getcwd()
            os.chdir(os.path.dirname(script_path))
            
            # Import the module dynamically
            import importlib.util
            spec = importlib.util.spec_from_file_location("game_module", script_path)
            game_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(game_module)
            
            # Call the run function if it exists, otherwise fall back to subprocess
            if hasattr(game_module, 'run'):
                game_module.run()
            else:
                subprocess.Popen(["python3", script_path])
                
            # Restore original directory
            os.chdir(original_dir)
        except Exception as e:
            print(f"Error launching game: {e}")
            # Fall back to the original method if there's an error
            subprocess.Popen(["python3", script_path])

    def launch_random_game(self, button):
        _, path = random.choice(self.buttons)
        self.launch_game(button, path)

    def __quit_cb(self, button):
        Gtk.main_quit()

    def apply_css(self):
        css = b"""
        /* General styles */
        * {
            font-family: 'Comic Sans MS', 'Segoe UI', sans-serif;
        }

        /* Game buttons */
        .game-button {
            font: 22px 'Comic Sans MS', Sans;
            background: linear-gradient(135deg, #5b6ee1, #8f5be1);
            color: #ffffff;
            border-radius: 25px;
            padding: 20px;
            border: 4px solid #b3c6ff;
            box-shadow: 0px 6px 16px rgba(91, 110, 225, 0.15);
            transition: background 0.2s, color 0.2s;
        }

        .game-button:hover {
            background: #6c8cff;
            color: #ffe082;
        }

        .game-button:active {
            background: #8f5be1;
            color: #ffd54f;
        }

        /* Random Game button */
        .random-button {
            font: 20px 'Comic Sans MS', Sans;
            background: linear-gradient(90deg, #ffe082, #8f5be1);
            color: #5b6ee1;
            border-radius: 20px;
            padding: 15px;
            border: 3px solid #ffd54f;
            box-shadow: 0px 4px 10px rgba(143, 91, 225, 0.12);
        }
        .random-button:hover {
            background: #ffd54f;
            color: #8f5be1;
        }

        /* Header background */
        frame > * > * {
            background: linear-gradient(90deg, #5b6ee1, #8f5be1);
            border-radius: 18px;
        }

        /* Toolbar */
        .toolbar {
            background: #5b6ee1;
        }

        /* Window background */
        #math-games-window {
            background: #e3f0ff;
            border-radius: 18px;
            padding: 20px;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

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

        # Main container with colorful background
        main_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_container.set_border_width(16)
        
        # Header with animated icon
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(16)
        
        # Animated icon with bouncing effect
        self.header_icon = Gtk.Label()
        self.header_icon.set_markup("<span font='24'>🧮</span>")
        header_box.pack_start(self.header_icon, False, False, 0)
        
        # Header text with colorful gradient
        header_text = Gtk.Label()
        header_text.set_markup("<span font='20' weight='bold' foreground='#FF6B6B'>Math Games</span>")
        header_box.pack_start(header_text, False, False, 0)
        
        main_container.pack_start(header_box, False, False, 0)
        
        # Subtitle with fun text
        subtitle = Gtk.Label()
        subtitle.set_markup("<span font='12' foreground='#6B5BFF' style='italic'>Fun math adventures await!</span>")
        subtitle.set_margin_bottom(12)
        main_container.pack_start(subtitle, False, False, 0)
        
        # Games grid
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        games_grid = Gtk.FlowBox()
        games_grid.set_valign(Gtk.Align.START)
        games_grid.set_halign(Gtk.Align.CENTER)
        games_grid.set_max_children_per_line(2)
        games_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        games_grid.set_homogeneous(True)
        games_grid.set_column_spacing(16)
        games_grid.set_row_spacing(16)
        
        # Game list with colorful icons
        game_list = [
            ("Math Minesweeper", "💣", "games/math_minesweeper.py", "#FF6B6B"),
            ("Broken Calculator", "🧮", "games/broken_calculator.py", "#4ECDC4"),
            ("Fifteen Puzzle", "🧩", "games/fifteen_puzzle.py", "#FF9F1C"),
            ("Euclid's Game", "📐", "games/euclids_game.py", "#A16AE8"),
            ("Odd Scoring", "🎲", "games/OddScoring.py", "#38B6FF"),
            ("Number Ninja", "🥷", "games/number_ninja.py", "#4CAF50"),
        ]
        
        # Create game buttons with fun effects
        self.buttons = []
        for name, icon, path, color in game_list:
            game_box = self.create_game_button(name, icon, path, color)
            games_grid.add(game_box)
            self.buttons.append((game_box, path))
        
        scrolled_window.add(games_grid)
        main_container.pack_start(scrolled_window, True, True, 0)
        
        # Random game button with sparkling effect
        random_button = Gtk.Button()
        random_button.set_size_request(200, 60)
        random_button.connect("clicked", self.launch_random_game)
        random_button.set_margin_top(12)
        
        # Add border container for rainbow effect
        border_container = Gtk.Box()
        border_container.get_style_context().add_class("rainbow-border")
        
        random_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        random_box.set_halign(Gtk.Align.CENTER)
        random_box.set_margin_top(4)
        random_box.set_margin_bottom(4)
        random_box.set_margin_start(8)
        random_box.set_margin_end(8)
        
        # Animated dice icon
        self.dice_icon = Gtk.Label()
        self.dice_icon.set_markup("<span font='18' color='white'>🎲</span>")
        random_box.pack_start(self.dice_icon, False, False, 0)
        
        random_label = Gtk.Label("Random Game")
        random_label.set_markup("<span font='16' weight='bold' color='white'>SURPRISE ME!</span>")
        random_box.pack_start(random_label, False, False, 0)
        
        # This is changed - we're nesting the button inside the border container
        random_button.add(random_box)
        random_button.get_style_context().add_class("random-button")
        
        # Add thread to animate rainbow border
        threading.Thread(target=self.animate_rainbow_border, daemon=True).start()
        
        main_container.pack_start(random_button, False, False, 0)
        
        # Tip of the day with rotating tips
        tip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        tip_box.set_margin_top(16)
        tip_box.get_style_context().add_class("tip-box")
        
        tip_icon = Gtk.Label()
        tip_icon.set_markup("<span font='16'>💡</span>")
        tip_box.pack_start(tip_icon, False, False, 0)
        
        self.tip_text = Gtk.Label()
        self.tip_text.set_markup("<span font='12' foreground='#6B5BFF'>Try to beat your best time in the Fifteen Puzzle!</span>")
        self.tip_text.set_line_wrap(True)
        tip_box.pack_start(self.tip_text, True, True, 0)
        
        main_container.pack_start(tip_box, False, False, 0)
        
        # Apply CSS
        self.apply_css()
        
        # Set up the main canvas
        self.set_canvas(main_container)
        main_container.show_all()
        
        # Start animation threads
        threading.Thread(target=self.animate_header_icon, daemon=True).start()
        threading.Thread(target=self.animate_dice_icon, daemon=True).start()
        threading.Thread(target=self.rotate_tips, daemon=True).start()
    
    def create_game_button(self, name, icon, path, color):
        # Create button container
        button = Gtk.Button()
        button.connect("clicked", self.launch_game, path)
        button.set_size_request(150, 150)
        button.get_style_context().add_class("game-button")
        
        # Add color class dynamically
        context = button.get_style_context()
        color_class = f"color-{color.replace('#', '')}"
        context.add_class(color_class)
        
        # Create vertical box for icon and label
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        button_box.set_halign(Gtk.Align.CENTER)
        button_box.set_valign(Gtk.Align.CENTER)
        
        # Game icon
        game_icon = Gtk.Label()
        game_icon.set_markup(f"<span font='36'>{icon}</span>")
        button_box.pack_start(game_icon, False, False, 0)
        
        # Game name with color
        game_label = Gtk.Label(name)
        game_label.set_markup(f"<span font='14' weight='bold' foreground='{color}'>{name}</span>")
        button_box.pack_start(game_label, False, False, 0)
        
        button.add(button_box)
        return button
    
    def animate_header_icon(self):
        # More diverse math emojis
        math_emojis = ["🧮", "🔢", "📏", "📐", "➗", "➕", "✖️", "🟰", "🧩", "🎲"]
        position = 0
        
        while True:
            # Change the emoji
            emoji = math_emojis[position % len(math_emojis)]
            
            # Simply update the emoji without bounce effect
            GLib.idle_add(self.header_icon.set_markup, f"<span font='24'>{emoji}</span>")
            
            position += 1
            time.sleep(1)
    
    def animate_dice_icon(self):
        # Dice faces
        dice_faces = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅", "🎲"]
        i = 0
        
        while True:
            face = dice_faces[i % len(dice_faces)]
            GLib.idle_add(self.dice_icon.set_markup, f"<span font='18'>{face}</span>")
            time.sleep(0.5)
            i += 1
    
    def rotate_tips(self):
        tips = [
            "Try to beat your best time in the Fifteen Puzzle!",
            "Math is fun when you play games!",
            "The Broken Calculator tests your problem-solving skills!",
            "Challenge a friend to play Euclid's Game with you!",
            "Number Ninja will make you faster at mental math!",
            "Can you solve the Math Minesweeper without exploding?",
            "Odd Scoring has strange rules. Can you figure them out?"
        ]
        
        tip_colors = ["#6B5BFF", "#FF6B6B", "#4ECDC4", "#FF9F1C", "#A16AE8", "#38B6FF", "#4CAF50"]
        
        i = 0
        while True:
            tip = tips[i % len(tips)]
            color = tip_colors[i % len(tip_colors)]
            GLib.idle_add(self.tip_text.set_markup, f"<span font='12' foreground='{color}'>{tip}</span>")
            time.sleep(5)
            i += 1
    
    def launch_game(self, button, path):
        script_path = os.path.join(os.path.dirname(__file__), path)
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
            font-family: 'Comic Sans MS', 'Poppins', sans-serif;
            color: #333333;
        }
        
        /* Window styling */
        window {
            background: linear-gradient(to bottom, #f9f9ff, #e6f7ff);
        }
        
        /* Game buttons */
        .game-button {
            background-color: #ffffff;
            border-radius: 20px;
            border: 4px solid #e0e0e0;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }
        
        .game-button:hover {
            background-color: #f8f8ff;
            box-shadow: 0 12px 20px rgba(0, 0, 0, 0.15);
            border-width: 4px;
        }
        
        .game-button:active {
            background-color: #f0f0ff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-top: 4px;
            margin-bottom: -4px;
        }
        
        /* Button color classes */
        .color-FF6B6B {
            border-color: #FF6B6B;
        }
        
        .color-4ECDC4 {
            border-color: #4ECDC4;
        }
        
        .color-FF9F1C {
            border-color: #FF9F1C;
        }
        
        .color-A16AE8 {
            border-color: #A16AE8;
        }
        
        .color-38B6FF {
            border-color: #38B6FF;
        }
        
        .color-4CAF50 {
            border-color: #4CAF50;
        }
        
        /* Random game button */
        .random-button {
            background: linear-gradient(45deg, #FF6B6B, #FF9F1C, #FF7F00);
            color: white;
            border-radius: 30px;
            border: 4px solid transparent;
            box-shadow: 0 8px 16px rgba(255, 107, 107, 0.3);
            font-weight: bold;
            background-clip: padding-box;
            margin: 2px;
        }
        
        /* Created separate class for the border effect */
        .rainbow-border {
            border: 4px solid;
            border-image: linear-gradient(45deg, 
                #FF0000, #FF7F00, #FFFF00, #00FF00, 
                #0000FF, #4B0082, #9400D3) 1;
            border-radius: 30px;
        }
        
        .random-button:hover {
            background: linear-gradient(45deg, #FF9F1C, #FF7F00, #FF6B6B);
            box-shadow: 0 12px 20px rgba(255, 159, 28, 0.4);
        }
        
        .random-button:active {
            background: linear-gradient(45deg, #FF7F00, #FF6B6B, #FF9F1C);
            box-shadow: 0 4px 8px rgba(255, 107, 107, 0.2);
            margin-top: 6px;
            margin-bottom: -2px;
        }
        
        /* Tip box */
        .tip-box {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
            border: 2px dashed #6B5BFF;
        }
        """
        
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
        )

    # Add new method to handle rainbow animation
    def animate_rainbow_border(self):
        colors = [
            "#FF0000", "#FF7F00", "#FFFF00", "#00FF00",
            "#0000FF", "#4B0082", "#9400D3"
        ]
        i = 0
        
        while True:
            # Rotate colors for rainbow effect
            color1 = colors[i % len(colors)]
            color2 = colors[(i + 1) % len(colors)]
            color3 = colors[(i + 2) % len(colors)]
            color4 = colors[(i + 3) % len(colors)]
            
            border_css = f"""
            .rainbow-border {{
                border: 4px solid;
                border-image: linear-gradient(45deg, {color1}, {color2}, {color3}, {color4}) 1;
            }}
            """
            
            # Apply the updated CSS
            GLib.idle_add(self._update_rainbow_css, border_css)
            
            time.sleep(0.2)
            i += 1
    
    def _update_rainbow_css(self, css_text):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css_text.encode())
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        return False
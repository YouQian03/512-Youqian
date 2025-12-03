import board
import busio
import displayio
import terminalio
from adafruit_display_text import label
import i2cdisplaybus
import adafruit_displayio_ssd1306
import time
from rotary_encoder import RotaryEncoder
import digitalio
import adafruit_adxl34x
import math
import neopixel
from rainbowio import colorwheel

# Initialize display
displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# Initialize rotary encoder (CLK=D3, DT=D2)
encoder = RotaryEncoder(board.D3, board.D2, pulses_per_detent=1)

# Initialize button (D1 pin)
button = digitalio.DigitalInOut(board.D1)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# Initialize accelerometer
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# Initialize NeoPixel
pixel_pin = board.D6
num_pixels = 1
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

# Game states
STATE_SPLASH = 0
STATE_DIFFICULTY_SELECT = 1
STATE_GAME_START = 2
STATE_GAME_PLAYING = 3
STATE_GAME_OVER = 4
STATE_RESULT = 5

current_state = STATE_SPLASH
selected_difficulty = 0
difficulties = ["EASY", "NORMAL", "HARD"]

# Game variables
current_level = 0
score = 0
countdown_time = 0
level_start_time = 0
player_x, player_y = 0, 0
exit_x, exit_y = 0, 0

# Encoder and button state
encoder_position = 0
last_encoder_position = 0
last_encoder_time = 0
encoder_debounce_ms = 80
button_pressed = False
last_button_value = button.value

# Direction detection variables
angle_threshold = 20
duration_threshold = 0.3
direction_start_time = {
    "up": None,
    "down": None, 
    "left": None,
    "right": None
}
last_direction_time = 0
direction_cooldown = 0.5

# Display related variables
current_display_group = None
maze_background_cache = {}  # Cache maze background element positions
current_maze_key = None

# Maze definitions
easy_levels = [
    [
        "########",
        "#S     #",
        "#      #",
        "#      #",
        "#      #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# ##   #",
        "#      #",
        "#      #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "#  ##  #",
        "#      #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# ###  #",
        "#      #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "#  ##  #",
        "#   #  #",
        "#   #  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "#  #   #",
        "#  #   #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "#  #   #",
        "#  ##  #",
        "#      #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# #### #",
        "#      #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "#  #####",
        "#      #",
        "# #### #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# ###  #",
        "#   #  #",
        "# ###  #",
        "#     E#",
        "########",
    ],
]

normal_levels = [
    [
        "########",
        "#     S#",
        "#      #",
        "#      #",
        "#      #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#   ## #",
        "#      #",
        "#      #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#  ##  #",
        "#      #",
        "#  ##  #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#  ### #",
        "#      #",
        "#  ##  #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#  ##  #",
        "#  #   #",
        "#  #   #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#   # S#",
        "#   #  #",
        "#   #  #",
        "#  ##  #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#   # S#",
        "#   #  #",
        "#  ##  #",
        "#      #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "# #### #",
        "#      #",
        "#  ##  #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#####  #",
        "#      #",
        "# #### #",
        "#E     #",
        "########",
    ],
    [
        "########",
        "#     S#",
        "#  ### #",
        "#  #   #",
        "#  ### #",
        "#E     #",
        "########",
    ],
]

hard_levels = [
    [
        "########",
        "#S     #",
        "# ###  #",
        "#      #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "#  ##  #",
        "#   #  #",
        "#   #  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "#  #   #",
        "#  #   #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "#  #   #",
        "#  ##  #",
        "#      #",
        "#    E #",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# #### #",
        "#      #",
        "#  ##  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "#  #####",
        "#      #",
        "# #### #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# ###  #",
        "#   #  #",
        "# ###  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S     #",
        "# ###  #",
        "#   #  #",
        "### #  #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "# # ## #",
        "# #  # #",
        "# #### #",
        "#     E#",
        "########",
    ],
    [
        "########",
        "#S #   #",
        "# ###  #",
        "#   #  #",
        "### #  #",
        "#     E#",
        "########",
    ],
]

# Organize levels by difficulty
maze_levels = [
    easy_levels,    # selected_difficulty == 0
    normal_levels,  # selected_difficulty == 1
    hard_levels,    # selected_difficulty == 2
]

# Set level time based on difficulty
level_times = {
    "EASY": 60,
    "NORMAL": 45, 
    "HARD": 30
}

def calculate_angles(x, y, z):
    """Calculate X-axis and Y-axis angles (relative to gravity direction)"""
    angle_x = math.atan2(x, math.sqrt(y*y + z*z)) * 180 / math.pi
    angle_y = math.atan2(y, math.sqrt(x*x + z*z)) * 180 / math.pi
    return angle_x, angle_y

def check_direction(angle_x, angle_y, current_time):
    """Detect if any of the four directions meet the conditions"""
    if current_time - last_direction_time < direction_cooldown:
        return None
    
    direction = None
    
    # Move up (negative X-axis direction)
    if angle_x < -angle_threshold:
        if direction_start_time["up"] is None:
            direction_start_time["up"] = current_time
        elif current_time - direction_start_time["up"] >= duration_threshold:
            direction = "UP"
    else:
        direction_start_time["up"] = None
    
    # Move down (positive X-axis direction)
    if angle_x > angle_threshold:
        if direction_start_time["down"] is None:
            direction_start_time["down"] = current_time
        elif current_time - direction_start_time["down"] >= duration_threshold:
            direction = "DOWN"
    else:
        direction_start_time["down"] = None
    
    # Move left (positive Y-axis direction)
    if angle_y > angle_threshold:
        if direction_start_time["left"] is None:
            direction_start_time["left"] = current_time
        elif current_time - direction_start_time["left"] >= duration_threshold:
            direction = "LEFT"
    else:
        direction_start_time["left"] = None
    
    # Move right (negative Y-axis direction)
    if angle_y < -angle_threshold:
        if direction_start_time["right"] is None:
            direction_start_time["right"] = current_time
        elif current_time - direction_start_time["right"] >= duration_threshold:
            direction = "RIGHT"
    else:
        direction_start_time["right"] = None
    
    return direction

def flash_led(color, times=2, delay=0.3):
    """Flash LED light"""
    for _ in range(times):
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(delay)

def rainbow_cycle(duration=3):
    """Rainbow color cycle"""
    start_time = time.monotonic()
    while time.monotonic() - start_time < duration:
        for j in range(255):
            if time.monotonic() - start_time >= duration:
                break
            pixels[0] = colorwheel(j & 255)
            pixels.show()
            time.sleep(0.01)

def create_splash_screen():
    """Create splash screen"""
    group = displayio.Group()
    
    title_label = label.Label(terminalio.FONT, text="Maze Run", x=35, y=15, scale=1)
    version_label = label.Label(terminalio.FONT, text="**********", x=30, y=30, scale=1)
    hint_label = label.Label(terminalio.FONT, text="START GAME", x=30, y=45, scale=1)
    
    group.append(title_label)
    group.append(version_label)
    group.append(hint_label)
    
    return group

def create_difficulty_screen():
    """Create difficulty selection screen"""
    group = displayio.Group()
    
    title_label = label.Label(terminalio.FONT, text="SELECT MODE", x=30, y=10, scale=1)
    group.append(title_label)
    
    y_pos = 30
    for i, difficulty in enumerate(difficulties):
        prefix = "> " if i == selected_difficulty else "  "
        diff_label = label.Label(terminalio.FONT, text=f"{prefix}{difficulty}", x=35, y=y_pos, scale=1)
        group.append(diff_label)
        y_pos += 15
    
    return group

def create_game_start_screen():
    """Create game start screen"""
    group = displayio.Group()
    
    difficulty_text = f"MODE: {difficulties[selected_difficulty]}"
    diff_label = label.Label(terminalio.FONT, text=difficulty_text, x=20, y=20, scale=1)
    start_label = label.Label(terminalio.FONT, text="GAME START!", x=25, y=40, scale=1)
    
    group.append(diff_label)
    group.append(start_label)
    
    return group

def create_game_screen():
    """Create game play screen - simplified version to reduce flickering"""
    global current_display_group, current_maze_key
    
    group = displayio.Group()
    maze_key = f"{selected_difficulty}_{current_level}"
    
    # Left side information area
    level_text = f"L:{current_level+1}/10"
    time_text = f"T:{int(countdown_time)}"
    score_text = f"S:{score}"
    
    level_label = label.Label(terminalio.FONT, text=level_text, x=5, y=10, scale=1)
    time_label = label.Label(terminalio.FONT, text=time_text, x=5, y=25, scale=1)
    score_label = label.Label(terminalio.FONT, text=score_text, x=5, y=40, scale=1)
    
    group.append(level_label)
    group.append(time_label)
    group.append(score_label)
    
    # Maze area - use cached background info if maze hasn't changed
    maze = maze_levels[selected_difficulty][current_level]
    
    # Maze drawing area parameters
    cell_size = 6
    start_x = 65
    start_y = 5
    
    # Draw maze (only update background when maze changes)
    if maze_key != current_maze_key or maze_key not in maze_background_cache:
        # Store maze background information
        maze_background_cache[maze_key] = []
        
        for row in range(min(len(maze), 7)):
            for col in range(min(len(maze[0]), 8)):
                x_pos = start_x + col * cell_size
                y_pos = start_y + row * cell_size
                
                cell_char = maze[row][col]
                if cell_char == '#':  # Wall
                    maze_background_cache[maze_key].append(("#", x_pos, y_pos))
                elif cell_char == 'E':  # Exit
                    maze_background_cache[maze_key].append(("E", x_pos, y_pos))
    
    # Draw cached maze background
    for char_type, x_pos, y_pos in maze_background_cache.get(maze_key, []):
        if char_type in ("#", "E"):
            char_label = label.Label(terminalio.FONT, text=char_type, x=x_pos, y=y_pos, scale=1)
            group.append(char_label)
    
    # Draw player position
    player_x_pos = start_x + player_x * cell_size
    player_y_pos = start_y + player_y * cell_size
    
    # Draw player position
    player_label = label.Label(terminalio.FONT, text="P", x=player_x_pos, y=player_y_pos, scale=1)
    group.append(player_label)
    
    # Draw brackets around selection box
    box_left = label.Label(terminalio.FONT, text="[", x=player_x_pos-2, y=player_y_pos, scale=1)
    box_right = label.Label(terminalio.FONT, text="]", x=player_x_pos+3, y=player_y_pos, scale=1)
    group.append(box_left)
    group.append(box_right)
    
    current_maze_key = maze_key
    current_display_group = group
    
    return group

def create_result_screen(is_victory):
    """Create result screen"""
    group = displayio.Group()
    
    result_text = "VICTORY!" if is_victory else "GAME OVER"
    result_label = label.Label(terminalio.FONT, text=result_text, x=35, y=10, scale=1)
    score_label = label.Label(terminalio.FONT, text=f"SCORE: {score}", x=35, y=25, scale=1)
    
    # Button selection
    buttons = ["RESTART"]
    y_pos = 40
    for i, btn in enumerate(buttons):
        prefix = "> " if i == selected_difficulty else "  "
        btn_label = label.Label(terminalio.FONT, text=f"{prefix}{btn}", x=20, y=y_pos, scale=1)
        group.append(btn_label)
        y_pos += 15
    
    group.append(result_label)
    group.append(score_label)
    
    return group

def load_level(level_index):
    """Load specified level"""
    global player_x, player_y, exit_x, exit_y, level_start_time, countdown_time
    
    maze = maze_levels[selected_difficulty][level_index]
    
    # Find start point (S) and end point (E)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'S':
                player_x, player_y = x, y
            elif cell == 'E':
                exit_x, exit_y = x, y
    
    level_start_time = time.monotonic()
    countdown_time = level_times[difficulties[selected_difficulty]]

def move_player(direction):
    """Move player"""
    global player_x, player_y, last_direction_time
    
    new_x, new_y = player_x, player_y
    
    if direction == "UP":
        new_y -= 1
    elif direction == "DOWN":
        new_y += 1
    elif direction == "LEFT":
        new_x -= 1
    elif direction == "RIGHT":
        new_x += 1
    
    # Check boundaries and walls
    maze = maze_levels[selected_difficulty][current_level]
    if (0 <= new_x < len(maze[0]) and 
        0 <= new_y < len(maze) and 
        maze[new_y][new_x] != '#'):
        player_x, player_y = new_x, new_y
        last_direction_time = time.monotonic()
        return True
    return False

def check_level_complete():
    """Check if level is completed"""
    return player_x == exit_x and player_y == exit_y

# Initial display
display.root_group = create_splash_screen()

print("Game Starting...")

# Main loop variables
last_display_update = 0
display_update_interval = 0.3  # Increase display update interval

while True:
    current_time = time.monotonic()
    current_ms = current_time * 1000
    
    # Check rotary encoder
    encoder_changed = encoder.update()
    if encoder_changed:
        if current_ms - last_encoder_time > encoder_debounce_ms:
            encoder_position = encoder.position
            last_encoder_time = current_ms
    
    # Check button
    current_button_value = button.value
    if last_button_value and not current_button_value:
        button_pressed = True
        print("Button pressed!")
    last_button_value = current_button_value
    
    # State machine processing
    if current_state == STATE_SPLASH:
        if button_pressed:
            current_state = STATE_DIFFICULTY_SELECT
            encoder_position = 0
            last_encoder_position = 0
            display.root_group = create_difficulty_screen()
            print("State changed: SPLASH -> DIFFICULTY_SELECT")
            button_pressed = False
    
    elif current_state == STATE_DIFFICULTY_SELECT:
        # Handle encoder rotation to select difficulty
        if encoder_position != last_encoder_position:
            selected_difficulty = (selected_difficulty + 1) % len(difficulties)
            display.root_group = create_difficulty_screen()
            print(f"Difficulty selected: {difficulties[selected_difficulty]}")
            last_encoder_position = encoder_position
        
        # Handle button confirmation
        if button_pressed:
            current_state = STATE_GAME_START
            display.root_group = create_game_start_screen()
            print(f"State changed: DIFFICULTY_SELECT -> GAME_START")
            button_pressed = False
    
    elif current_state == STATE_GAME_START:
        if button_pressed:
            # Initialize game variables
            current_level = 0
            score = 0
            load_level(current_level)
            current_state = STATE_GAME_PLAYING
            display.root_group = create_game_screen()
            print("State changed: GAME_START -> GAME_PLAYING")
            button_pressed = False
    
    elif current_state == STATE_GAME_PLAYING:
        # Update countdown
        elapsed_time = current_time - level_start_time
        countdown_time = max(0, level_times[difficulties[selected_difficulty]] - elapsed_time)
        
        # Reduce display update frequency to avoid flickering
        if current_time - last_display_update > display_update_interval:
            display.root_group = create_game_screen()
            last_display_update = current_time
        
        # Check if time is up
        if countdown_time <= 0:
            current_state = STATE_GAME_OVER
            flash_led((255, 0, 0), 2)
            selected_difficulty = 0
            display.root_group = create_result_screen(False)
            print("Game Over - Time's up!")
            continue
        
        # Get accelerometer data and process direction control
        x, y, z = accelerometer.acceleration
        angle_x, angle_y = calculate_angles(x, y, z)
        direction = check_direction(angle_x, angle_y, current_time)
        
        # Handle direction movement
        if direction:
            print(f"Moving: {direction}")
            if move_player(direction):
                # Update display immediately after moving
                display.root_group = create_game_screen()
                last_display_update = current_time
        
        # Check if reached the exit
        if button_pressed:
            if check_level_complete():
                # Level completed
                score += 10
                current_level += 1
                
                if current_level >= 10:
                    # All levels completed
                    current_state = STATE_RESULT
                    rainbow_cycle(3)
                    selected_difficulty = 0
                    display.root_group = create_result_screen(True)
                    print("All levels completed!")
                else:
                    # Move to next level
                    flash_led((0, 255, 0), 2)
                    load_level(current_level)
                    display.root_group = create_game_screen()
                    last_display_update = current_time
                    print(f"Level {current_level} completed! Moving to level {current_level + 1}")
            else:
                print("Not at exit position")
            
            button_pressed = False
    
    elif current_state == STATE_GAME_OVER:
        # Handle button selection on result screen
        if encoder_position != last_encoder_position:
            selected_difficulty = (selected_difficulty + 1) % 2
            display.root_group = create_result_screen(False)
            last_encoder_position = encoder_position
        
        if button_pressed:
            if selected_difficulty == 0:  # RESTART
                current_state = STATE_GAME_START
                display.root_group = create_game_start_screen()
    
    elif current_state == STATE_RESULT:
        # Handle button selection on victory result screen
        if encoder_position != last_encoder_position:
            selected_difficulty = (selected_difficulty + 1) % 2
            display.root_group = create_result_screen(True)
            last_encoder_position = encoder_position
        
        if button_pressed:
            if selected_difficulty == 0:  # RESTART
                current_state = STATE_GAME_START
                display.root_group = create_game_start_screen()
            else:  # MAIN MENU
                current_state = STATE_SPLASH
                display.root_group = create_splash_screen()
            button_pressed = False
    
    time.sleep(0.05)

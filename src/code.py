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

# 初始化显示
displayio.release_displays()
i2c = busio.I2C(board.SCL, board.SDA)
display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=64)

# 初始化旋转编码器（CLK=D3, DT=D2）
encoder = RotaryEncoder(board.D3, board.D2, pulses_per_detent=1)

# 初始化按钮（D1引脚）
button = digitalio.DigitalInOut(board.D1)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

# 初始化加速度计
accelerometer = adafruit_adxl34x.ADXL345(i2c)

# 初始化NeoPixel
pixel_pin = board.D6
num_pixels = 1
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.3, auto_write=False)

# 游戏状态
STATE_SPLASH = 0
STATE_DIFFICULTY_SELECT = 1
STATE_GAME_START = 2
STATE_GAME_PLAYING = 3
STATE_GAME_OVER = 4
STATE_RESULT = 5

current_state = STATE_SPLASH
selected_difficulty = 0
difficulties = ["EASY", "NORMAL", "HARD"]

# 游戏变量
current_level = 0
score = 0
countdown_time = 0
level_start_time = 0
player_x, player_y = 0, 0
exit_x, exit_y = 0, 0

# 编码器和按钮状态
encoder_position = 0
last_encoder_position = 0
last_encoder_time = 0
encoder_debounce_ms = 80
button_pressed = False
last_button_value = button.value

# 方向检测相关变量
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

# 显示相关变量
current_display_group = None
maze_background_cache = {}  # 缓存迷宫背景元素的位置信息
current_maze_key = None

# 迷宫定义
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

# 按照难度组织关卡
maze_levels = [
    easy_levels,    # selected_difficulty == 0
    normal_levels,  # selected_difficulty == 1
    hard_levels,    # selected_difficulty == 2
]

# 根据难度设置关卡时间
level_times = {
    "EASY": 60,
    "NORMAL": 45, 
    "HARD": 30
}

def calculate_angles(x, y, z):
    """计算X轴和Y轴的角度（相对于重力方向）"""
    angle_x = math.atan2(x, math.sqrt(y*y + z*z)) * 180 / math.pi
    angle_y = math.atan2(y, math.sqrt(x*x + z*z)) * 180 / math.pi
    return angle_x, angle_y

def check_direction(angle_x, angle_y, current_time):
    """检测四个方向是否满足条件"""
    if current_time - last_direction_time < direction_cooldown:
        return None
    
    direction = None
    
    # 向上移动（X轴负方向）
    if angle_x < -angle_threshold:
        if direction_start_time["up"] is None:
            direction_start_time["up"] = current_time
        elif current_time - direction_start_time["up"] >= duration_threshold:
            direction = "UP"
    else:
        direction_start_time["up"] = None
    
    # 向下移动（X轴正方向）
    if angle_x > angle_threshold:
        if direction_start_time["down"] is None:
            direction_start_time["down"] = current_time
        elif current_time - direction_start_time["down"] >= duration_threshold:
            direction = "DOWN"
    else:
        direction_start_time["down"] = None
    
    # 向左移动（Y轴正方向）
    if angle_y > angle_threshold:
        if direction_start_time["left"] is None:
            direction_start_time["left"] = current_time
        elif current_time - direction_start_time["left"] >= duration_threshold:
            direction = "LEFT"
    else:
        direction_start_time["left"] = None
    
    # 向右移动（Y轴负方向）
    if angle_y < -angle_threshold:
        if direction_start_time["right"] is None:
            direction_start_time["right"] = current_time
        elif current_time - direction_start_time["right"] >= duration_threshold:
            direction = "RIGHT"
    else:
        direction_start_time["right"] = None
    
    return direction

def flash_led(color, times=2, delay=0.3):
    """闪烁LED灯"""
    for _ in range(times):
        pixels.fill(color)
        pixels.show()
        time.sleep(delay)
        pixels.fill((0, 0, 0))
        pixels.show()
        time.sleep(delay)

def rainbow_cycle(duration=3):
    """彩虹色循环"""
    start_time = time.monotonic()
    while time.monotonic() - start_time < duration:
        for j in range(255):
            if time.monotonic() - start_time >= duration:
                break
            pixels[0] = colorwheel(j & 255)
            pixels.show()
            time.sleep(0.01)

def create_splash_screen():
    """创建开机画面"""
    group = displayio.Group()
    
    title_label = label.Label(terminalio.FONT, text="Maze Run", x=35, y=15, scale=1)
    version_label = label.Label(terminalio.FONT, text="**********", x=30, y=30, scale=1)
    hint_label = label.Label(terminalio.FONT, text="START GAME", x=30, y=45, scale=1)
    
    group.append(title_label)
    group.append(version_label)
    group.append(hint_label)
    
    return group

def create_difficulty_screen():
    """创建难度选择界面"""
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
    """创建游戏开始界面"""
    group = displayio.Group()
    
    difficulty_text = f"MODE: {difficulties[selected_difficulty]}"
    diff_label = label.Label(terminalio.FONT, text=difficulty_text, x=20, y=20, scale=1)
    start_label = label.Label(terminalio.FONT, text="GAME START!", x=25, y=40, scale=1)
    
    group.append(diff_label)
    group.append(start_label)
    
    return group

def create_game_screen():
    """创建游戏进行界面 - 简化版本，减少闪烁"""
    global current_display_group, current_maze_key
    
    group = displayio.Group()
    maze_key = f"{selected_difficulty}_{current_level}"
    
    # 左侧信息区域
    level_text = f"L:{current_level+1}/10"
    time_text = f"T:{int(countdown_time)}"
    score_text = f"S:{score}"
    
    level_label = label.Label(terminalio.FONT, text=level_text, x=5, y=10, scale=1)
    time_label = label.Label(terminalio.FONT, text=time_text, x=5, y=25, scale=1)
    score_label = label.Label(terminalio.FONT, text=score_text, x=5, y=40, scale=1)
    
    group.append(level_label)
    group.append(time_label)
    group.append(score_label)
    
    # 迷宫区域 - 如果迷宫没有变化，使用缓存的背景信息
    maze = maze_levels[selected_difficulty][current_level]
    
    # 迷宫绘制区域参数
    cell_size = 6
    start_x = 65
    start_y = 5
    
    # 绘制迷宫（只在迷宫变化时更新背景）
    if maze_key != current_maze_key or maze_key not in maze_background_cache:
        # 存储迷宫背景信息
        maze_background_cache[maze_key] = []
        
        for row in range(min(len(maze), 7)):
            for col in range(min(len(maze[0]), 8)):
                x_pos = start_x + col * cell_size
                y_pos = start_y + row * cell_size
                
                cell_char = maze[row][col]
                if cell_char == '#':  # 墙壁
                    maze_background_cache[maze_key].append(("#", x_pos, y_pos))
                elif cell_char == 'E':  # 终点
                    maze_background_cache[maze_key].append(("E", x_pos, y_pos))
    
    # 绘制缓存的迷宫背景
    for char_type, x_pos, y_pos in maze_background_cache.get(maze_key, []):
        if char_type in ("#", "E"):
            char_label = label.Label(terminalio.FONT, text=char_type, x=x_pos, y=y_pos, scale=1)
            group.append(char_label)
    
    # 绘制玩家位置
    player_x_pos = start_x + player_x * cell_size
    player_y_pos = start_y + player_y * cell_size
    
    # 绘制玩家位置
    player_label = label.Label(terminalio.FONT, text="P", x=player_x_pos, y=player_y_pos, scale=1)
    group.append(player_label)
    
    # 在选择框周围绘制方括号
    box_left = label.Label(terminalio.FONT, text="[", x=player_x_pos-2, y=player_y_pos, scale=1)
    box_right = label.Label(terminalio.FONT, text="]", x=player_x_pos+3, y=player_y_pos, scale=1)
    group.append(box_left)
    group.append(box_right)
    
    current_maze_key = maze_key
    current_display_group = group
    
    return group

def create_result_screen(is_victory):
    """创建结果界面"""
    group = displayio.Group()
    
    result_text = "VICTORY!" if is_victory else "GAME OVER"
    result_label = label.Label(terminalio.FONT, text=result_text, x=35, y=10, scale=1)
    score_label = label.Label(terminalio.FONT, text=f"SCORE: {score}", x=35, y=25, scale=1)
    
    # 按钮选择
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
    """加载指定关卡"""
    global player_x, player_y, exit_x, exit_y, level_start_time, countdown_time
    
    maze = maze_levels[selected_difficulty][level_index]
    
    # 查找起点(S)和终点(E)
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            if cell == 'S':
                player_x, player_y = x, y
            elif cell == 'E':
                exit_x, exit_y = x, y
    
    level_start_time = time.monotonic()
    countdown_time = level_times[difficulties[selected_difficulty]]

def move_player(direction):
    """移动玩家"""
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
    
    # 检查边界和墙壁
    maze = maze_levels[selected_difficulty][current_level]
    if (0 <= new_x < len(maze[0]) and 
        0 <= new_y < len(maze) and 
        maze[new_y][new_x] != '#'):
        player_x, player_y = new_x, new_y
        last_direction_time = time.monotonic()
        return True
    return False

def check_level_complete():
    """检查是否完成关卡"""
    return player_x == exit_x and player_y == exit_y

# 初始显示
display.root_group = create_splash_screen()

print("Game Starting...")

# 主循环变量
last_display_update = 0
display_update_interval = 0.3  # 增加显示更新间隔

while True:
    current_time = time.monotonic()
    current_ms = current_time * 1000
    
    # 检查旋转编码器
    encoder_changed = encoder.update()
    if encoder_changed:
        if current_ms - last_encoder_time > encoder_debounce_ms:
            encoder_position = encoder.position
            last_encoder_time = current_ms
    
    # 检查按钮
    current_button_value = button.value
    if last_button_value and not current_button_value:
        button_pressed = True
        print("Button pressed!")
    last_button_value = current_button_value
    
    # 状态机处理
    if current_state == STATE_SPLASH:
        if button_pressed:
            current_state = STATE_DIFFICULTY_SELECT
            encoder_position = 0
            last_encoder_position = 0
            display.root_group = create_difficulty_screen()
            print("State changed: SPLASH -> DIFFICULTY_SELECT")
            button_pressed = False
    
    elif current_state == STATE_DIFFICULTY_SELECT:
        # 处理编码器旋转选择难度
        if encoder_position != last_encoder_position:
            selected_difficulty = (selected_difficulty + 1) % len(difficulties)
            display.root_group = create_difficulty_screen()
            print(f"Difficulty selected: {difficulties[selected_difficulty]}")
            last_encoder_position = encoder_position
        
        # 处理按钮确认
        if button_pressed:
            current_state = STATE_GAME_START
            display.root_group = create_game_start_screen()
            print(f"State changed: DIFFICULTY_SELECT -> GAME_START")
            button_pressed = False
    
    elif current_state == STATE_GAME_START:
        if button_pressed:
            # 初始化游戏变量
            current_level = 0
            score = 0
            load_level(current_level)
            current_state = STATE_GAME_PLAYING
            display.root_group = create_game_screen()
            print("State changed: GAME_START -> GAME_PLAYING")
            button_pressed = False
    
    elif current_state == STATE_GAME_PLAYING:
        # 更新倒计时
        elapsed_time = current_time - level_start_time
        countdown_time = max(0, level_times[difficulties[selected_difficulty]] - elapsed_time)
        
        # 减少显示更新频率，避免闪烁
        if current_time - last_display_update > display_update_interval:
            display.root_group = create_game_screen()
            last_display_update = current_time
        
        # 检查时间到
        if countdown_time <= 0:
            current_state = STATE_GAME_OVER
            flash_led((255, 0, 0), 2)
            selected_difficulty = 0
            display.root_group = create_result_screen(False)
            print("Game Over - Time's up!")
            continue
        
        # 获取加速度计数据并处理方向控制
        x, y, z = accelerometer.acceleration
        angle_x, angle_y = calculate_angles(x, y, z)
        direction = check_direction(angle_x, angle_y, current_time)
        
        # 处理方向移动
        if direction:
            print(f"Moving: {direction}")
            if move_player(direction):
                # 移动后立即更新显示
                display.root_group = create_game_screen()
                last_display_update = current_time
        
        # 检查是否到达终点
        if button_pressed:
            if check_level_complete():
                # 完成关卡
                score += 10
                current_level += 1
                
                if current_level >= 10:
                    # 所有关卡完成
                    current_state = STATE_RESULT
                    rainbow_cycle(3)
                    selected_difficulty = 0
                    display.root_group = create_result_screen(True)
                    print("All levels completed!")
                else:
                    # 进入下一关
                    flash_led((0, 255, 0), 2)
                    load_level(current_level)
                    display.root_group = create_game_screen()
                    last_display_update = current_time
                    print(f"Level {current_level} completed! Moving to level {current_level + 1}")
            else:
                print("Not at exit position")
            
            button_pressed = False
    
    elif current_state == STATE_GAME_OVER:
        # 处理结果界面的按钮选择
        if encoder_position != last_encoder_position:
            selected_difficulty = (selected_difficulty + 1) % 2
            display.root_group = create_result_screen(False)
            last_encoder_position = encoder_position
        
        if button_pressed:
            if selected_difficulty == 0:  # RESTART
                current_state = STATE_GAME_START
                display.root_group = create_game_start_screen()
    
    elif current_state == STATE_RESULT:
        # 处理胜利结果的按钮选择
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


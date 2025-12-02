# 512-Youqian
----------------Maze Run Game----------------
A motion-controlled maze game built with CircuitPython, where players tilt the device to navigate through mazes.
Game Overview
Maze Run is an innovative motion-controlled maze game where players tilt the device to guide their character through mazes and reach the exit within a time limit. The game features three difficulty modes with a total of 30 carefully designed levels.
Hardware Requirements

Microcontroller: CircuitPython-compatible board (e.g., Adafruit Feather)
Display: SSD1306 OLED Display (128x64 pixels, I2C interface)
Accelerometer: ADXL345 3-axis accelerometer (I2C interface)
Rotary Encoder: Connected to D2 and D3 pins
Button: Connected to D1 pin (with pull-up resistor)
LED: WS2812 NeoPixel (connected to D6 pin)

Pin Connections
ComponentPinI2C SDAboard.SDAI2C SCLboard.SCLEncoder CLKD3Encoder DTD2ButtonD1NeoPixelD6
Game Mechanics
Control Methods

Rotary Encoder: Menu navigation (difficulty selection, result screen options)
Button: Confirm selection, start game, confirm reaching exit
Accelerometer: Control character movement by tilting the device

Tilt forward (X-axis negative) → Move up
Tilt backward (X-axis positive) → Move down
Tilt left (Y-axis positive) → Move left
Tilt right (Y-axis negative) → Move right



Motion Detection System
The game uses an intelligent tilt detection system:

Angle Threshold: Tilt angle must exceed 20 degrees
Duration Threshold: Must maintain tilt for 0.3 seconds or longer
Movement Cooldown: 0.5-second cooldown after each movement to prevent accidental inputs

This design ensures precise control and prevents unintended movements from minor device shake.
Game State Machine
The game uses 6 states to manage game flow:

STATE_SPLASH (Splash Screen): Game startup screen
STATE_DIFFICULTY_SELECT (Difficulty Selection): Choose game difficulty
STATE_GAME_START (Game Preparation): Display selected difficulty, prepare to start
STATE_GAME_PLAYING (Gameplay): Main game loop
STATE_GAME_OVER (Game Over): Failure screen when time runs out
STATE_RESULT (Victory): Victory screen after completing all levels

Game Modes
Difficulty Levels
DifficultyTime LimitLevelsFeaturesEASY60s/level10 levelsSimpler mazes, beginner-friendlyNORMAL45s/level10 levelsMirrored mazes, medium difficultyHARD30s/level10 levelsMost challenging levels, time pressure
Level Design

EASY Mode: 10 progressive levels, from simple to complex
NORMAL Mode: EASY levels horizontally mirrored, start and exit positions swapped
HARD Mode: EASY levels 4-10 (harder levels) + 3 brand new challenging levels

Scoring System

Each completed level awards 10 points
Maximum score: 100 points (complete all 10 levels)
If time runs out, game ends and displays current score

Visual Feedback
LED Effects
The game provides rich visual feedback through NeoPixel LED:

Level Complete: Green flash (2 times)
Game Over: Red flash (2 times)
All Levels Complete: Rainbow cycle animation (3 seconds)

Display Interface
Gameplay Interface Layout (128x64 OLED):
Left Info Panel:        Right Maze Area:
L:1/10                  ########
T:60                    #P.....#
S:0                     #.###..#
                        #.....E#
                        ########
                    
[P] = Player position (with selection box)
[E] = Exit
[#] = Wall
[.] = Path
Gameplay Flow

Start Game: Display splash screen, press button to continue
Select Difficulty: Rotate encoder to choose, press button to confirm
Prepare to Start: Display selected mode, press button to start Level 1
Gameplay:

Tilt device to move character
Avoid walls, find the exit
Press button after reaching exit to confirm
Complete level before time runs out


Complete Level: Green LED flash, automatically proceed to next level
Game End:

Complete all 10 levels → Victory screen + rainbow LED effect
Time runs out → Game over screen + red LED flash


Select Action: Restart or Return to main menu

Technical Features
Performance Optimization

Display Update Throttling: Game interface updates every 0.5 seconds to reduce flickering
Instant Feedback: Display refreshes immediately after character movement for smooth operation
Memory Management: Reuses DisplayGroups to avoid repeated object creation
Debouncing: Encoder input uses 80ms debounce to prevent false triggers

Code Architecture

State Machine Pattern: Clear game state management
Modular Functions: Each function independently encapsulated
Extensible Design: Easy to add new levels and difficulty modes

Dependencies
pythonadafruit_display_text
adafruit_displayio_ssd1306
adafruit_adxl34x
neopixel
rainbowio
rotary_encoder (custom library)
Gameplay Tips

Control Technique: Maintain steady tilt, avoid frequent shaking
Plan Your Route: Observe maze structure before moving, plan the shortest path
Time Management: Watch the countdown, don't waste time in dead ends
Confirm Action: Must press button after reaching exit (E) to proceed to next level

Top Left L: Current Level / Total Levels
Left T: Remaining Time (seconds)
Bottom Left S: Current Score
Right Side: Real-time maze map, square brackets [P] indicate current position


----------------Enclosure Design Overview----------------

This project's enclosure employs a dual-layer modular design, aiming to securely house electronic components, provide an optimal interactive experience, and facilitate future maintenance and debugging.

(1) Upper Layer (Interactive Layer)

The blue upper module houses all user interaction components:
    • Rotary encoder
    • Game confirmation button
    • NeoPixel indicator window
    • OLED display viewing window

These elements allow players to conveniently operate knobs and buttons while viewing the OLED game display. Adequate spacing between the rotary encoder and buttons prevents operational interference.

Additionally, ventilation openings are reserved at the top of the upper layer to provide moderate cushioning for internal wiring and modules.

(2) Lower Structure (Main Chamber)

The lower layer consists of a gray module designed to house:
    •    Xiao ESP32C3 main control board
    •    ADXL345 accelerometer
	•    NeoPixel
    •    LiPo battery
    •    Power switch
    •    Jumpers and female header pins

The lower layer employs a sealed enclosure structure to securely anchor electronic modules, preventing vibration from affecting accelerometer readings. Internal clearance facilitates wiring, while side openings ensure external access to the USB-C port, meeting course requirements.

(3) Serviceability and Detachable Design

The upper and lower shell sections feature a snap-fit assembly that separates easily. This allows users to inspect internal wiring, replace sensor modules, or adjust battery positioning without compromising the overall structure, facilitating debugging and maintenance.

"""
Includes global setting values
"""

# debug constants
JOYSTICK_MANAGER_DEBUG = False
PRINT_ASSET_EXISTENCE = False
SHOW_PERFORMANCE = True

# physic constants
G = 1

# delta-time
ALLOW_SPEED_UP = False
FPS_CAP = False
V_SYNC = True
from global_values import DISPLAY_HZS
DELTA_FPS = DISPLAY_HZS[0] if V_SYNC else 60
SET_FPS = DELTA_FPS * FPS_CAP

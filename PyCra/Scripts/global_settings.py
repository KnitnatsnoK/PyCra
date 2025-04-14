"""
Includes global setting values
"""

from global_variables import Variable, set_global

# debug constants
JOYSTICK_MANAGER_DEBUG = False
JOYSTICK_WINDOW = False
PRINT_ASSET_EXISTENCE = False
SHOW_PERFORMANCE = Variable(True)

# physic constants
G = Variable(1.0)
set_global("G", G)

# delta-time
ALLOW_SPEED_UP = False
FPS_CAP = False
V_SYNC = True
from global_values import DISPLAY_HZS
DELTA_FPS = DISPLAY_HZS[0] if V_SYNC else 60
SET_FPS = DELTA_FPS * FPS_CAP

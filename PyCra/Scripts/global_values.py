"""
Includes all globals and assets.py
"""

from assets import *

MONITORS:list[screeninfo.Monitor] = screeninfo.get_monitors()
MAIN_MONITOR:screeninfo.Monitor = MONITORS[0]
MAIN_MONITOR_SIZE = vec2(MAIN_MONITOR.width, MAIN_MONITOR.height)
DISPLAY_HZS = pg.display.get_desktop_refresh_rates()

PROJECT_FOLDERS = ["Assets", "Scenes", "Scripts"]

CIRCLE_BUTTON = "Circle_Button"
RECT_BUTTON = "Rect_Button"
SCROLL_WHEEL = "Scroll_Wheel"
CHECK_BOX = "Check_Box"

RES_SD = vec2(640, 480)
RES_HD = vec2(1280, 720)
RES_FULLHD = vec2(1920, 1080)
RES_QHD = vec2(2560, 1440)
RES_2K = vec2(2048, 1080)
RES_4K = vec2(3840, 2160)
RES_8K = vec2(7680, 4320)

if __name__ == "__main__":
    from assets import *

from value_assets import *

# window functions
class Window_Manager:
    def __init__(self, window:Window, manual_render:bool=False):
        self.window = window
        self.window_size = vec2(window.size)
        self.renderer = Renderer(window, accelerated=1)
        self.UI_elements:list = []
        self.second_UI_elements:list = []
        self.second_UI_elements_parent = None
        self.manual_render = manual_render

        self.last_action_element = None
        self.fullscreen = False
        self.saved_window_size = copy(self.window_size)

    def set_window_size(self, size:vec2, engine_change=False):
        if not engine_change and RUN_BY_ENGINE:
            return
        center = vec2(self.window.position)+vec2(self.window.size)/2
        self.window.size = size
        self.saved_window_size = copy(self.window_size)
        self.window_size = size
        self.window.position = center_vec2(size, center)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.set_window_size(MAIN_MONITOR_SIZE)
        else:
            self.set_window_size(copy(self.saved_window_size))

ALL_WINDOW_MANAGERS:list[Window_Manager] = []
top_window:Window = None

def quit_engine():
    pg.quit()
    sys.exit()

def set_top_window(window):
    global top_window
    top_window = window

from pygame.locals import WINDOWPOS_UNDEFINED
pycra_icon = load_image("Assets\\PyCra Icon.jpg")
def create_window(title:str, size:vec2, pos:vec2=WINDOWPOS_UNDEFINED, icon:pg.Surface=pycra_icon, manual_render:bool=False, **flags:bool) -> tuple[Window, Window_Manager]:
    window = Window(title, size, pos, **flags)
    window.set_icon(icon)
    window_manager = Window_Manager(window, manual_render=manual_render)
    ALL_WINDOW_MANAGERS.append(window_manager)
    set_top_window(window)
    return window, window_manager

def center_vec2(size:vec2, center:vec2=MAIN_MONITOR_SIZE/2) -> vec2:
    return center - size/2

def center_window(window:Window, screen_size:vec2=MAIN_MONITOR_SIZE):
    window.position = center_vec2(window.size, screen_size/2)

def set_window_size(window:Window, size:vec2, engine_change=False):
    if not engine_change and RUN_BY_ENGINE:
        return
    center = vec2(window.position)+vec2(window.size)/2
    window.size = size
    window.position = center_vec2(size, center)

def window_to_top(window:Window):
    window.always_on_top = True
    window.always_on_top = False
    set_top_window(window)

def delete_window(window:Window):
    for window_manager in ALL_WINDOW_MANAGERS:
        if window_manager.window == window:
            ALL_WINDOW_MANAGERS.remove(window_manager)
            break
    window.destroy()
    if len(ALL_WINDOW_MANAGERS) == 0:
        quit_engine()

def delete_top_window():
    global top_window
    delete_window(top_window)
from value_assets import *
from window_manager import Window_Manager, center_vec2, quit_engine
from imports import KEYS, MOUSE, render_text, load_image, random_vec3, create_project, open_project, run_project, center, create_surface, create_boundary
from objects import SCENES, SCENE_NAMES, SCENE, LAYERS, save_scene, save_new_scene, load_scene

class UI_Element:
    def __init__(self, window_manager:Window_Manager, pos:vec2, size:vec2|None, action:list|int|None=None):
        self.id = id(self)

        self.anti = False
        self.render = True
        self.project_dependend = False

        self.window_manager = window_manager
        self.window_size = self.window_manager.window_size

        self.pos = pos
        self.size = size

        self.action:list[UI_Element]|int|None = action
        self.is_second_UI = False
        self.second_UI_parent = None
        if isinstance(action, list):
            for ui_element in action:
                ui_element:UI_Element
                ui_element.is_second_UI = True
                ui_element.second_UI_parent = self

        # image
        if type(self) == UI_Element:
            self.image_update_needed = False
            self.update_image()

    def update_image(self):
        surf = create_surface(self.size)

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        if MOUSE.down_buttons[0]:
            if (self.pos.x < MOUSE.position.x < self.pos.x + self.size.x) and (self.pos.y < MOUSE.position.y < self.pos.y + self.size.y):
                if not type(self.window_manager.last_action_element) == Pop_up:
                    self.window_manager.last_action_element = self

    def handle_action(self):
        if isinstance(self.action, int):
            self.handle_int_action()
        elif isinstance(self.action, list):
            if self.window_manager.second_UI_elements == self.action:
                self.window_manager.second_UI_elements = []
                return

            if self in self.window_manager.second_UI_elements:
                pos = self.pos + vec2(self.size.x, 0)
            else:
                pos = self.pos + vec2(0, self.size.y)
            for ui_element in self.action:
                ui_element:UI_Element
                ui_element.pos = pos
                pos = pos + vec2(0, ui_element.size.y)
                self.window_manager.second_UI_elements.append(ui_element)

            self.window_manager.second_UI_elements_parent = self
        else:
            self.action()

    def handle_int_action(self):
        if self.action == QUIT_ENGINE:
            quit_engine()
        elif self.action == OPEN_PROJECT:
            open_project(self.window_manager, initial_directory="Projects\\")
        elif self.action == COLOR_TEST:
            random_color = random_vec3(0, 255)
            self.set_colors(random_color, vec3(255)-random_color)
        elif self.action == CREATE_PROJECT:
            project_name = input("Enter a project name: ")
            if project_name != "":
                create_project(project_name)
                open_project(self.window_manager, folder_path=f"Projects\\{project_name}")
            else:
                print("No project was created")
        elif self.action == CHANGE_NEXT_SCENE:
            set_global("<Scene>", (get_global("<Scene>").value + 1)%len(get_global("<SCENES>").value))
            set_global("<Game Objects>", f"Game Objects: {len(get_global("<SCENES>").value[get_global("<Scene>").value])}")
            
            set_global("<Loaded Scene>", f"Scene: {get_global("<Scene>").value+1}/{len(get_global("<SCENES>").value)}")
        elif self.action == SAVE_SCENE:
            save_scene(SCENE.value, LAYERS[SCENE.value], path=f'Projects\\{get_global("<Project_Opened>").value}\\Scenes\\', name=SCENE_NAMES[SCENE.value])
            print(f"Saved {SCENE_NAMES[SCENE.value]}")
        elif self.action == CREATE_SCENE:
            scene_name = input("Enter a scene name: ")
            if scene_name != "":
                new_scene_index = len(get_global("<SCENES>").value)
                new_scene = []
                new_layers = ["game_objects"]
                if save_new_scene(new_scene, new_layers, f'Projects\\{get_global("<Project_Opened>").value}\\Scenes\\', scene_name):
                    get_global("<SCENES>").value.append(new_scene)
                    get_global("<Scene_Names>").value.append(scene_name)
                    get_global("<LAYERS>").value.append(new_layers)
                    load_scene(new_scene_index, f"Projects\\{get_global("<Project_Opened>").value}\\Scenes\\", scene_name)
                    set_global("<Scene>", new_scene_index)

                    set_global("<Loaded Scene>", f"Scene: {get_global("<Scene>").value+1}/{len(get_global("<SCENES>").value)}")
                elif not PRINT_ASSET_EXISTENCE:
                    print(f"The scene '{scene_name}' already exists.")
            else:
                print("No scene was created")
        elif self.action == RUN_PROJECT:
            run_project(self.window_manager)

    def draw(self):
        if self.image_update_needed:
            self.image_update_needed = False
            self.update_image()
        self.image.draw(dstrect=(self.pos, self.size))

    def tick(self):
        if self.action is not None:
            self.check_for_action()

class Text_Element(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2, size:vec2|None=None, bg_color:vec3=vec3(50), text_color:vec3=None, text:str|Variable="", font:str|None="Comic Sans", font_size:int=18, action:list|int|None=None):
        super().__init__(window_manager, pos, size, action)

        self.original_size = size
        self.boundary_size = vec2(4)
        self.bg_color = bg_color
        self.text_color = vec3(255) - bg_color if text_color == None else text_color
        self.text = text
        self.font = font
        self.font_size = font_size

        self.action = action

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        text = self.text if isinstance(self.text, str) else self.text.value

        if self.original_size == None:
            if type(self) == Pop_up:
                text_surf = render_text(text, self.font, self.font_size, self.text_color, None, None, window_width=self.window_size.x)
            else:
                text_surf = render_text(text, self.font, self.font_size, self.text_color, None, None)
            self.size = vec2(text_surf.get_size()) + self.boundary_size*2
        elif self.original_size.y < 0:
            text_surf = render_text(text, self.font, self.font_size, self.text_color, self.size.x-self.boundary_size.x*2, None)
            self.size = vec2(text_surf.get_size()) + self.boundary_size*2
        else:
            text_surf = render_text(text, self.font, self.font_size, self.text_color, *(self.size-self.boundary_size*2))
        
        surf = create_boundary(self.bg_color, self.size, self.boundary_size)
        surf.blit(text_surf, self.boundary_size)

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def draw(self):
        if isinstance(self.text, Variable):
            self.update_image()
        elif self.image_update_needed:
            self.image_update_needed = False
            self.update_image()
        self.image.draw(dstrect=(self.pos, self.size))

class Text_Box(Text_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2, size:vec2|None=None, bg_color:vec3=vec3(50), text_color:vec3=None, text:str|Variable="", font:str|None="Comic Sans", font_size:int=18, action:list|int|None=None, **kwargs):
        super().__init__(window_manager, pos, size, bg_color, text_color, text, font, font_size, action)
        
        self.pos = center(self.pos, self.size, **kwargs)

    def set_colors(self, bg_color:vec3, text_color:vec3):
        self.bg_color = bg_color
        self.text_color = text_color
        self.image_update_needed = True

    def set_bg_color(self, bg_color:vec3):
        self.bg_color = bg_color
        self.image_update_needed = True

    def set_text_color(self, text_color:vec3):
        self.text_color = text_color
        self.image_update_needed = True

class Pop_up(Text_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None=None, size:vec2|None=None, bg_color:vec3=vec3(50), text_color:vec3=None, text:str="", font:str|None="Comic Sans", font_size:int=18):
        self.first_frame = True
        
        super().__init__(window_manager, pos, size, bg_color, text_color, text, font, font_size, 0)
        self.pos = center_vec2(self.size, self.window_size/2) if self.pos == None else self.pos

    def check_for_action(self):
        if self.first_frame:
            self.first_frame = False
            return
        if KEYS.any_down:
            self.window_manager.last_action_element = self
        
    def handle_action(self):
        self.window_manager.UI_elements.remove(self)

class Scroll_Wheel(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, size:vec2, wheel_color:vec3=vec3(50), bar_color:vec3=None):
        super().__init__(window_manager, pos, size, None)
        self.action = 0

        self.scroll_bar = copy(pos)
        self.scroll_dir = 0 if self.size.x > self.size.y else 1

        self.wheel_color = wheel_color
        self.bar_color = vec3(255) - wheel_color if bar_color == None else bar_color

        self.bar_size = vec2(min(self.size.x, self.size.y*2), min(self.size.y, self.size.x*2))
        self.scroll = Variable(0)
        set_UI_global(SCROLL_WHEEL, self.id, self.scroll)
        self.calculate_scroll()

        # image
        self.image_update_needed = False
        self.update_image()

    def calculate_scroll(self):
        if self.scroll_dir == 0:
            self.scroll.value = (self.scroll_bar.x - self.pos.x) / (self.size.x - self.bar_size.x)
        else:
            self.scroll.value = (self.scroll_bar.y - self.pos.y) / (self.size.y - self.bar_size.y)

    def update_image(self):
        surf = create_surface(self.size)

        pg.draw.rect(surf, self.wheel_color, (0, 0, *self.size))
        pg.draw.rect(surf, self.bar_color, (*(self.scroll_bar-self.pos), *self.bar_size))

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        scrolling = (self.scroll_dir == 0 and MOUSE.wheel.x != 0) or (self.scroll_dir == 1 and MOUSE.wheel.y != 0)
        if scrolling:
            if not type(self.window_manager.last_action_element) == Pop_up:
                self.window_manager.last_action_element = self
        
    def handle_action(self):
        scroll_speed = max(self.size.x, self.size.y) / 80
        self.scroll_bar -= vec2(0 if not self.scroll_dir == 0 else MOUSE.wheel.x, 0 if not self.scroll_dir == 1 else MOUSE.wheel.y) * scroll_speed
        if self.scroll_dir == 0:
            self.scroll_bar.x = min(self.pos.x+self.size.x-self.bar_size.x, max(self.pos.x, self.scroll_bar.x))
        else:
            self.scroll_bar.y = min(self.pos.y+self.size.y-self.bar_size.y, max(self.pos.y, self.scroll_bar.y))

        self.calculate_scroll()
        self.image_update_needed = True

class Check_Box(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, size:vec2, bg_color:vec3=vec3(50), checked_color:vec3=None, checked:bool=False):
        super().__init__(window_manager, pos, size, None)
        self.action = 0
        self.checked:Variable = Variable(checked)
        set_UI_global(CHECK_BOX, self.id, self.checked)

        self.bg_color = bg_color
        self.checked_color = vec3(255) - self.bg_color if checked_color == None else checked_color

        self.boundary_size = vec2(max(1, int((self.size.x + self.size.y)/2 / 20)))

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = create_surface(self.size)

        pg.draw.rect(surf, self.checked_color, (0, 0, *self.size))
        pg.draw.rect(surf, self.bg_color, (*self.boundary_size, *(self.size-self.boundary_size*2)))
        if self.checked.value:
            d = int((self.size.x + self.size.y)/2 / 7)
            pg.draw.line(surf, self.checked_color, (vec2(d)+self.boundary_size), self.size-vec2(d)-self.boundary_size, d)
            pg.draw.line(surf, self.checked_color, (d+self.boundary_size.x, self.size.y-d-self.boundary_size.y), (self.size.x-d-self.boundary_size.x, d+self.boundary_size.y), d)

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)
        
    def handle_action(self):
        self.checked.value = not self.checked.value
        self.image_update_needed = True

class Icon(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None=None, size:vec2|None=None, default_bg:bool=False, image_path:str="PyCra Icon.jpg", project_path:bool=False, action:list|int|None=None):
        super().__init__(window_manager, pos, (None if type(size) in [int, float] else size), action)
        self.image_path = image_path
        self.project_path = project_path

        self.project_dependend = True if project_path else False

        self.saved_size = size
        self.placeholder_size = False
        self.size_scale = 1 if not type(size) in (int, float) else size
        self.default_bg = default_bg

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        if get_placeholder_status(Icon, get_global("<Project_Opened>").value, (self.image_path, self.project_path)):
            self.image:Texture|Image = try_UI_tex_cache(Icon, None)
            if self.size == None:
                self.placeholder_size = True
                self.size = vec2(self.image.width, self.image.height)
            return
        self.image:Texture|Image = try_UI_tex_cache(Icon, (self.default_bg, self.size, self.image_path, self.project_path))
        if self.image:
            if self.size == None:
                self.size = vec2(self.image.width, self.image.height) * self.size_scale
            elif self.placeholder_size:
                self.placeholder_size = False
                self.size = vec2(self.image.width, self.image.height) * self.size_scale
            return

        placeholder = False
        try:
            if self.default_bg:
                surf = create_boundary(vec3(50), self.size, vec2(4))
                if self.project_path:
                    surf.blit(load_image(f"Projects\\{get_global("<Project_Opened>").value}\\Assets\\{self.image_path}", self.size))
                else:
                    surf.blit(load_image(f"Assets\\{self.image_path}", self.size))
            else:
                if self.project_path:
                    surf = load_image(f"Projects\\{get_global("<Project_Opened>").value}\\Assets\\{self.image_path}", self.size)
                else:
                    surf = load_image(f"Assets\\{self.image_path}", self.size)
            
        except FileNotFoundError:
            placeholder = True
            surf = load_image(f"Assets\\Placeholder.png", self.size)
            self.size = None
        
        if self.size == None:
            if placeholder:
                self.placeholder_size = True
                self.size = vec2(surf.size) if not isinstance(self.saved_size, vec2) else self.saved_size
            else:
                self.size = vec2(surf.size) * self.size_scale if not isinstance(self.saved_size, vec2) else self.saved_size
        elif self.placeholder_size and not placeholder:
            self.placeholder_size = False
            self.size = vec2(surf.size) * self.size_scale if not isinstance(self.saved_size, vec2) else self.saved_size

        if placeholder:
            set_placeholder(Icon, get_global("<Project_Opened>").value, (self.image_path, self.project_path))
            self.image:Texture|Image = cached_UI_tex_load(self.window_manager.renderer, surf, Icon, None)
        else:
            self.image:Texture|Image = cached_UI_tex_load(self.window_manager.renderer, surf, Icon, (self.default_bg, self.size, self.image_path, self.project_path))

def create_Text_Box(window_m:Window_Manager, pos:vec2, size:vec2|None=None, bg_color:vec3=vec3(50), text_color:vec3=vec3(255), text:str="", font:str="Comic Sans", font_size:int=18, action:list|int|None=None, user_creation=True, **kwargs):
    text_box = Text_Box(window_m, pos, size, bg_color, text_color, text, font, font_size, action, **kwargs)
    if RUN_BY_PROJECT or not user_creation:
        window_m.UI_elements.append(text_box)
    return text_box

def create_Pop_up(window_m:Window_Manager, pos:vec2|None=None, size:vec2|None=None, bg_color:vec3=vec3(50), text_color:vec3=vec3(255), text:str="", font:str="Comic Sans", font_size:int=18, user_creation=True):
    pop_up = Pop_up(window_m, pos, size, bg_color, text_color, text, font, font_size)
    if RUN_BY_PROJECT or not user_creation:
        window_m.UI_elements.append(pop_up)
    return pop_up
set_global("<(func) create_Pop_up>", create_Pop_up)

def create_Scroll_Wheel(window_m:Window_Manager, pos:vec2|None, size:vec2, wheel_color:vec3=vec3(50), bar_color:vec3=None, user_creation=True):
    scroll_wheel = Scroll_Wheel(window_m, pos, size, wheel_color, bar_color)
    if RUN_BY_PROJECT or not user_creation:
        window_m.UI_elements.append(scroll_wheel)
    return scroll_wheel

def create_Check_Box(window_m:Window_Manager, pos:vec2|None, size:vec2, bg_color:vec3=vec3(50), checked_color:vec3=None, checked:bool=False, user_creation=True):
    check_box = Check_Box(window_m, pos, size, bg_color, checked_color, checked)
    if RUN_BY_PROJECT or not user_creation:
        window_m.UI_elements.append(check_box)
    return check_box

def create_Icon(window_m:Window_Manager, pos:vec2|None, size:vec2, default_bg:bool=False, image_path:str="PyCra Icon.jpg", project_path:bool=False, action:list|int|None=None, user_creation=True):
    icon = Icon(window_m, pos, size, default_bg, image_path, project_path, action)
    if RUN_BY_PROJECT or not user_creation:
        window_m.UI_elements.append(icon)
    return icon

def create_toolbar(window_m:Window_Manager, pos:vec2, UI_elements:list[UI_Element], user_creation=True):
    for ui_element in UI_elements:
        ui_element.pos = copy(pos)
        if not user_creation or RUN_BY_PROJECT:
            window_m.UI_elements.append(ui_element)
        pos += vec2(ui_element.size.x, 0)

def tick_main_UI_elements(window_m:Window_Manager):
    tick_UI_elements(window_m.UI_elements)

def draw_main_UI_elements(window_m:Window_Manager):
    draw_UI_elements(window_m.UI_elements)

def tick_UI_elements(UI_elements:list[UI_Element|Text_Element]):
    for element in UI_elements:
        if element is None or type(element) == Pop_up: # no pop-ups
            continue
        element.tick()
    for element in UI_elements:
        if element is None or not element.anti: # only anti-elements
            continue
        element.tick()
    for element in UI_elements:
        if element is None or type(element) != Pop_up:# only pop-ups
            continue
        element.tick()

def draw_UI_elements(UI_elements:list[UI_Element|Text_Element]):
    for element in UI_elements:
        if element is None or not element.render or type(element) == Pop_up: # no pop-ups
            continue
        element.draw()
    for element in UI_elements:
        if element is None or not element.render or not element.anti: # only anti-elements
            continue
        element.draw()
    for element in UI_elements:
        if element is None or type(element) != Pop_up:# only pop-ups
            continue
        element.draw()

def handle_top_action(window_m:Window_Manager):
    action_element:UI_Element = window_m.last_action_element

    if not isinstance(action_element, Pop_up) and len(window_m.second_UI_elements) and KEYS.any_down:
        if action_element == None:
            window_m.second_UI_elements = []
            window_m.second_UI_elements_parent = None
            window_m.last_action_element = None
            return
        elif not action_element.is_second_UI:
            if not isinstance(action_element.action, list) or window_m.second_UI_elements == action_element.action:
                window_m.second_UI_elements = []
                window_m.second_UI_elements_parent = None
                window_m.last_action_element = None
                return
            else:
                window_m.second_UI_elements = []
                window_m.second_UI_elements_parent = None
        elif window_m.second_UI_elements_parent in window_m.second_UI_elements and not action_element.second_UI_parent in window_m.second_UI_elements:
            for _ in range(len(window_m.second_UI_elements_parent.action)):
                window_m.second_UI_elements.pop(-1)
            if window_m.second_UI_elements_parent == action_element:
                window_m.second_UI_elements_parent = None
                window_m.last_action_element = None
                return

    if action_element is not None:
        action_element.handle_action()
        window_m.last_action_element = None

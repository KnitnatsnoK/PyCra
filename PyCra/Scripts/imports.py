from value_assets import *

# window manager
from window_manager import *

def change_main_window_name(name, user_change=True):
    if (not user_change) or RUN_BY_PROJECT:
        set_global("<main_window_name>", name)

# Camera
class Camera:
    def __init__(self, binded_obj=None):
        self.binded_obj = binded_obj
        self.pos:vec2 = vec2(0)

        self.smoothness = 6
        self.dead_zone:vec2 = vec2(100, 70)
        self.last_mouse_pos:vec2 = None

    def update(self, fps_factor:float):
        if self.binded_obj is None:
            return
        if RUN_BY_PROJECT:
            if self.binded_obj.scene != get_global("<Scene>").value:
                return
            offset = self.calculate_offset()
            # only apply changes for axis outside the dead zone
            offset.x *= abs(offset.x) > self.dead_zone.x/2
            offset.y *= abs(offset.y) > self.dead_zone.y/2

            dead_offset = abs(self.dead_zone/2 - abs(offset))
            new_offset = offset * (fps_factor / self.smoothness)
            new_offset = vec2(min(dead_offset.x, max(-dead_offset.x, new_offset.x)), min(dead_offset.y, max(-dead_offset.y, new_offset.y)))
            
            self.pos += new_offset
            return
        
        if MOUSE.pressed_buttons[2]:
            if self.last_mouse_pos is not None:
                self.pos += self.last_mouse_pos - MOUSE.position
            self.last_mouse_pos = MOUSE.position
        else:
            self.last_mouse_pos = None

    def calculate_offset(self):
        return (self.binded_obj.center - self.binded_obj.window_manager.window_size/2) - self.pos

    def bind_object(self, obj, auto_snap=True):
        self.binded_obj = obj
        if auto_snap:
            self.pos += self.calculate_offset()

CAMERA = Camera()
set_global("<Camera>", CAMERA)

# key functions
def listlike_to_array(keys) -> np.ndarray:
    return np.array([keys[i] for i in range(len(keys))])

class Keys:
    def __init__(self):
        self.pressed = listlike_to_array(pg.key.get_pressed())
        self.down = np.zeros_like(self.pressed, dtype=bool)
        self.up = np.zeros_like(self.pressed, dtype=bool)
        self.last_pressed = self.pressed

        self.extra_keys = []
        self.extra_changes = {}

        self.pressed_extra = {}
        self.down_extra = {}
        self.up_extra = {}

        self.any_down = False

    def get_key_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.pressed = listlike_to_array(pg.key.get_pressed())
        self.down = self.pressed & ~self.last_pressed
        self.up = ~self.pressed & self.last_pressed

        self.last_pressed = self.pressed

        return self.pressed, self.down, self.up
    
    def down_extra_key(self, key_id):
        self.extra_changes[key_id] = True
        if key_id not in self.extra_keys:
            self.extra_keys.append(key_id)

    def up_extra_key(self, key_id):
        self.extra_changes[key_id] = False
        if key_id not in self.extra_keys:
            self.extra_keys.append(key_id)
    
    def update_extra_keys(self):
        for key_id in self.extra_keys:
            if key_id in self.extra_changes:
                if self.extra_changes[key_id]: # down
                    self.down_extra[key_id] = True
                    self.pressed_extra[key_id] = True
                else: # up
                    self.up_extra[key_id] = True
                    self.pressed_extra[key_id] = False
            else:
                self.down_extra[key_id] = False
                self.up_extra[key_id] = False
        
        self.extra_changes.clear()

    def check_pressed(self, key_id) -> bool:
        if key_id >= len(self.pressed):
            if key_id in self.pressed_extra:
                return self.pressed_extra[key_id]
            else:
                return False
        else:
            return self.pressed[key_id]
        
    def check_down(self, key_id) -> bool:
        if key_id >= len(self.down):
            if key_id in self.down_extra:
                return self.down_extra[key_id]
            else:
                return False
        else:
            return self.down[key_id]
        
    def check_up(self, key_id) -> bool:
        if key_id >= len(self.up):
            if key_id in self.up_extra:
                return self.up_extra[key_id]
            else:
                return False
        else:
            return self.up[key_id]

KEYS = Keys()
set_global("KEYS", KEYS)

# mouse functions
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class Mouse:
    def __init__(self):
        self.pressed_buttons:tuple[bool,bool,bool,bool,bool] = listlike_to_array(pg.mouse.get_pressed(5))
        self.down_buttons:tuple[bool,bool,bool,bool,bool] = np.zeros_like(self.pressed_buttons, dtype=bool)
        self.up_buttons:tuple[bool,bool,bool,bool,bool] = np.zeros_like(self.pressed_buttons, dtype=bool)
        self.last_pressed_buttons = self.pressed_buttons

        self.wheel:vec2 = vec2(0)

        self.position:vec2 = self.get_position()
        self.global_position:vec2 = self.get_global_position()
        self.scene_position:vec2 = self.get_scene_position()

    def get_data(self):
        self.get_position()
        self.get_global_position()
        self.get_scene_position()
        self.get_button_data()

    def get_position(self) -> vec2:
        self.position = vec2(pg.mouse.get_pos())
        return self.position
    
    def get_global_position(self) -> vec2:
        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        self.global_position = vec2(pt.x, pt.y)
        return self.global_position

    def get_scene_position(self) -> vec2:
        self.scene_position = self.position + CAMERA.pos
        return self.scene_position

    def get_button_data(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        self.pressed_buttons = listlike_to_array(pg.mouse.get_pressed(5))
        self.down_buttons = self.pressed_buttons & ~self.last_pressed_buttons
        self.up_buttons = ~self.pressed_buttons & self.last_pressed_buttons

        self.last_pressed_buttons = self.pressed_buttons

        return self.pressed_buttons, self.down_buttons, self.up_buttons
    
    def handle_wheel(self, event:pg.Event) -> vec2:
        self.wheel = vec2(event.precise_x, event.precise_y)
        return self.wheel

MOUSE = Mouse()
set_global("MOUSE", MOUSE)

# flatten
def double_flatten(list_of_lists:list[list]):
    return list(set([item for sub_list in list_of_lists for item in sub_list]))

# median
def calculate_median(numbers, sorted=True):
    if not sorted:
        sorted_numbers = sorted(numbers)
    else:
        sorted_numbers = numbers
    n = len(sorted_numbers)
    middle = n // 2

    if n % 2 == 1:  # Odd number of elements
        return sorted_numbers[middle]
    else:           # Even number of elements
        return (sorted_numbers[middle - 1] + sorted_numbers[middle]) / 2

# vector functions
def pointing_amount(vector:vec2, origin:vec2, target:vec2):
    # Calculate the dot product between the two normalized vectors
    alignment = dot(normalize(vector), normalize(target - origin))
    return alignment

# randomization
def random_vec2(min:int, max:int):
    return vec2(randint(min, max), randint(min, max))

def random_vec3(min:int, max:int):
    return vec3(randint(min, max), randint(min, max), randint(min, max))

def random_vec2_max2(min:int, max0:int, max1:int):
    return vec2(randint(min, max0), randint(min, max1))

def random_vec2_minmax2(min0:int, min1:int, max0:int, max1:int):
    return vec2(randint(min0, max0), randint(min1, max1))

# surface functions
def try_loading_image(image_path:str, project_dependend:bool, size:vec2=None) -> tuple[pg.Surface, bool]:
    placeholder = False
    try:
        if project_dependend:
            if RUN_BY_PROJECT:
                surf = load_image(f"Assets\\{image_path}", size)
            else:
                surf = load_image(f'Projects\\{get_global("<Project_Opened>").value}\\Assets\\{image_path}', size)
        else:
            surf = load_image(f"Assets\\{image_path}", size)
    except FileNotFoundError:
        placeholder = True
        surf = load_image(f"Assets\\Placeholder.png", size)
    
    return surf, placeholder

def surf_screenshot(window_manager:Window_Manager):
	return window_manager.renderer.to_surface()

def texture_screenshot(window_manager:Window_Manager):
	return Texture.from_surface(window_manager.renderer, surf_screenshot(window_manager))

# center functions
def center(pos:vec2, size:vec2, **kwargs) -> vec2:
    if "center" in kwargs and kwargs["center"]:
        pos += -size/2
    elif "left" in kwargs and kwargs["left"]:
        pos += vec2(0, -size.y/2)
    elif "right" in kwargs and kwargs["right"]:
        pos += vec2(-size.x, -size.y/2)
    elif "bottom" in kwargs and kwargs["bottom"]:
        pos += vec2(-size.x/2, -size.y)
    elif "bottomleft" in kwargs and kwargs["bottomleft"]:
        pos += vec2(0, -size.y)
    elif "bottomright" in kwargs and kwargs["bottomright"]:
        pos += vec2(-size.x, -size.y)
    elif "top" in kwargs and kwargs["top"]:
        pos += vec2(-size.x/2, 0)
    elif "topleft" in kwargs and kwargs["topleft"]:
        pos += vec2(0, 0)
    elif "topright" in kwargs and kwargs["topright"]:
        pos += vec2(-size.x, 0)

    return pos

# file dialogs
def file_dialog(initial_directory:str|None=None, file:bool=True, file_types:list[tuple[str, str]]=[]):
    if file:
        file_path = filedialog.askopenfilename(
        initialdir=initial_directory,
        title="Select a file",
        filetypes=[*file_types, ("All files", "*.*")]
        )
        return file_path
    return filedialog.askdirectory(initialdir=initial_directory) # Folder

# Error Message
def Raise_Error(window_m:Window_Manager, error_message:str):
    get_global("<(func) create_Pop_up>").value(window_m, text_color=vec3(225, 64, 64), text=error_message, font_size=20, user_creation=False)

# script functions
def run_script(window_m:Window_Manager, file_path:str):
    if not os.path.isfile(file_path):
        Raise_Error(window_m, f"The file '{file_path}' does not exist.")
        return
    
    try:
        result = subprocess.run([sys.executable, os.path.join(os.getcwd(), file_path)], check=True)
        # print(f"Script finished with return code: {result.returncode}")
        # print(f"Standard Output:\n{result.stdout}")
        # print(f"Standard Error:\n{result.stderr}")

    except subprocess.CalledProcessError as e:
        Raise_Error(window_m, f"Error running the script: {e}")
        # print(f"An error occurred: {e}")
        # print(f"Return code: {e.returncode}")
        # print(f"Output: {e.output}")
        # print(f"Error Output: {e.stderr}")

# function overwrite
def bind_function_to_class(old_function_name, new_function, class_instance):
	setattr(class_instance, old_function_name, types.MethodType(new_function, class_instance))

# default program for file extension
def get_default_windows_app(ext):
    try:  # UserChoice\ProgId lookup initial
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\{}\UserChoice'.format(ext)) as key:
            progid = winreg.QueryValueEx(key, 'ProgId')[0]
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Classes\{}\shell\open\command'.format(progid)) as key:
            path = winreg.QueryValueEx(key, '')[0]
    except:  # UserChoice\ProgId not found
        try:
            class_root = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, ext)
            if not class_root:  # No reference from ext
                class_root = ext  # Try direct lookup from ext
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'{}\shell\open\command'.format(class_root)) as key:
                path = winreg.QueryValueEx(key, '')[0]
        except:  # Ext not found
            path = None
    # Path clean up, if any
    if path:  # Path found
        path = os.path.expandvars(path)  # Expand env vars, e.g. %SystemRoot% for ext .txt
        path = shlex.split(path, posix=False)[0]  # posix False for Windows operation
        path = path.strip('"')  # Strip quotes
    return path

def open_file(file_path:str):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == ".py":
        default_program = os.path.basename(get_default_windows_app(file_extension))
        if default_program in ["python.exe", "pycharm64.exe"]: # we don't want to run the file, just open it
            Raise_Error(ALL_WINDOW_MANAGERS[0], f"Your default program for {file_extension}-files is {default_program}.\nChange the default program to something else like an editor or the file will always be opened by notepad.")
            subprocess.run(["notepad", file_path])
            return
    os.startfile(file_path)

# Project Managment
def create_folder(path:str, name:str):
    folder_path = path + name
    try:
        os.mkdir(folder_path)
    except FileExistsError:
        if PRINT_ASSET_EXISTENCE:
            print(f"The folder '{folder_path}' already exists.")

def create_file(path:str, name:str, contents:list=None):
    file_path = path + name
    if os.path.exists(file_path):
        if PRINT_ASSET_EXISTENCE:
            print(f"The file '{file_path}' already exists.")
    else:
        with open(file_path, 'w') as file:
            if contents is not None:
                lines = [line + "\n" for line in contents]
                file.writelines(lines)

def copy_file(source_file:str, destination_folder:str, overwrite:bool=False):
    destination_file = os.path.join(destination_folder, os.path.basename(source_file))
    if os.path.exists(destination_file):
        if PRINT_ASSET_EXISTENCE:
            print(f"The file '{destination_file}' already exists.")
    else:
        shutil.copy(source_file, destination_file)

def relative_format_paths(target_directory: str, format:str=".py"):
    """
    Get relative paths of all specified format files (e.g. .py) inside the specified folder.

    Parameters:
    - target_directory (str): The path to the target directory.

    Returns:
    - List[str]: A list of relative file paths to .py files.
    """
    relative_paths = []

    # Walk through the directory
    for root, dirs, files in os.walk(target_directory):
        for file in files:
            if file.endswith(format):
                # Get the relative path
                relative_path = os.path.relpath(os.path.join(root, file), target_directory)
                relative_paths.append(relative_path)

    return relative_paths

def sort_files_by_modification_date(directory:str, last_updated_first=True):
    entries = [entry for entry in os.scandir(directory) if entry.is_file()]
    return sorted(entries, key=lambda entry: entry.stat().st_mtime, reverse=last_updated_first)

def get_latest_file_time(folder):
    latest_time = 0
    for entry in os.scandir(folder.path):
        if entry.is_file():
            latest_time = max(latest_time, entry.stat().st_mtime)
        elif entry.is_dir():  # If it's a subfolder, recursively check inside it
            latest_time = max(latest_time, get_latest_file_time(entry))
    return latest_time

def sort_folders_by_modification_date(directory:str, last_updated_first=True):
    entries = [entry for entry in os.scandir(directory) if entry.is_dir()]
    return sorted(entries, key=get_latest_file_time, reverse=last_updated_first)

from objects import save_new_scene, save_scene, load_scene, create_Game_Object, create_Dynamic_Object

def create_project(name:str):
    print(f"Creating project {name}...")
    # Folder structure
    create_folder("Projects\\", name)
    project_path = "Projects\\" + name + "\\"
    for needed_folder in PROJECT_FOLDERS:
        create_folder(project_path, needed_folder)

    # Default files
    create_file(project_path + "Scripts\\", "main.py", contents=['# You can import necessary modules or functions from .py files in the "Scripts" folder',
                                                                 '',
                                                                 "# This function runs every frame, so don't do any 'while True - loops' if possible",
                                                                 'def tick():',
                                                                 '\tpass',
                                                                 ])

    # Default Assets
    copy_file("Assets\\Placeholder.png", project_path + "Assets\\")
    copy_file("Assets\\PyCra Icon.jpg", project_path + "Assets\\")

    # Script Assets
    py_file_paths = relative_format_paths("Scripts", format=".py")
    py_file_paths.remove("main.py")
    for py_file_path in py_file_paths:
        copy_file(f"Scripts\\{py_file_path}", project_path + "Scripts\\", overwrite=True)

    # Scenes
    main_window_manager = ALL_WINDOW_MANAGERS[0]
    example_scene = [create_Game_Object(None, "game_objects", main_window_manager, vec2(480, 465), vec2(500, 50), user_creation=False, center=True),
                     create_Dynamic_Object(None, "game_objects", main_window_manager, vec2(480, 15), vec2(30), user_creation=False, center=True),
                     ]
    example_layers = ["game_objects"]

    save_new_scene(example_scene, example_layers, f"Projects\\{name}\\Scenes\\", "test_scene")
    
    print(f"Finished creating project {name}")

def reload_project_dependend_assets(window_m:Window_Manager):
    print("Reloading project dependencies...")
    get_global("<(cache) PLACEHOLDER_CACHE>").value.pop(get_global("<Project_Opened>").value, None)
    project_dependend = 0
    for ui_element in window_m.UI_elements:
        if ui_element.project_dependend:
            project_dependend += 1
            ui_element.image_update_needed = True
    
    for scene in range(len(get_global("<SCENES>").value)):
        for game_obj in get_global("<SCENES>").value[scene]:
            if game_obj.project_dependend:
                project_dependend += 1
                game_obj.image_update_needed = True
    print(f"Reloaded {project_dependend} project dependend assets")

def load_project(window_m:Window_Manager):
    print("Loading Scenes...")

    if RUN_BY_PROJECT:
        scenes_path = "Scenes"
    else:
        scenes_path = f'Projects\\{get_global("<Project_Opened>").value}\\Scenes'

    scenes = sort_files_by_modification_date(scenes_path)
    scene_names = [os.path.splitext(os.path.splitext(entry.name)[0])[0] for entry in scenes]

    get_global("<SCENES>").value.clear()
    get_global("<Scene_Names>").value.clear()
    get_global("<Scene>").value = 0
    get_global("<LAYERS>").value.clear()

    for i, scene_name in enumerate(scene_names):
        load_scene(i, scenes_path + "\\", scene_name)

    reload_project_dependend_assets(window_m)
    print("Finished loading Scenes...")

set_global("<Update_tick_func>", None)
set_global("<Project_Opened>", None)
def open_project(window_m:Window_Manager, initial_directory:str|None=None, folder_path:str=None):
    if folder_path is None:
        folder_path = filedialog.askdirectory(initialdir=initial_directory)
    if folder_path == "":
        return

    folders_in_project = []
    files_in_project = []
    for entry in os.listdir(folder_path):
        full_path = os.path.join(folder_path, entry)
        if os.path.isfile(full_path):
            files_in_project.append(entry)
        elif os.path.isdir(full_path):
            folders_in_project.append(entry)

    needed_folders = copy(PROJECT_FOLDERS)
    for folder in folders_in_project:
        if folder in needed_folders:
            needed_folders.remove(folder)
    if len(needed_folders) > 0:
        Raise_Error(window_m, f"Path '{folder_path}' is not a valid project\nFolder/s: {needed_folders} is/are missing")
        return
    
    folder_name = os.path.basename(folder_path)
    set_global("<Project_Opened>", folder_name)

    print(f"Opening Project '{get_global("<Project_Opened>").value}'...")
    load_project(window_m)
    print(f"Opened Project '{get_global("<Project_Opened>").value}'")

    # reassign tick-function in main.py
    file_path = os.path.join(os.getcwd(), f'Projects\\{get_global("<Project_Opened>").value}', "Scripts", "main.py")
    spec = importlib.util.spec_from_file_location("main", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    set_global("<Update_tick_func>", module.tick)

    # test
    file_path = f"Projects\\{folder_name}\\Scripts\\main.py"
    open_file(file_path)

def run_project(window_m:Window_Manager):
    if get_global("<Project_Opened>").value is None:
        Raise_Error(window_m, "No project is currently opened")
        return
    print(f"Running '{get_global("<Project_Opened>").value}'...\n")

    # run project here
    start_time = perf_counter()
    run_script(window_m, f'Projects\\{get_global("<Project_Opened>").value}\\Scripts\\game_handler.py')

    print(f"\nFinished running '{get_global("<Project_Opened>").value}' with {perf_counter()-start_time:2f}s runtime")

# render functions
def render_text_line(text:str, font:str=None, font_size:int=18, text_color:vec3=vec3(255)) -> pg.Surface:
    font = pg.font.SysFont(font, font_size)
    text_surface = font.render(text, True, text_color)
    return text_surface

text_surf_cache:dict[tuple[str,str,int,vec3,int,int], pg.Surface] = {}
def render_text(text:str, font:str=None, font_size:int=18, text_color:vec3=vec3(255), max_width:int=None, max_height:int=None, window_width:int=None) -> pg.Surface:
    cache_key = (text, font, font_size, text_color, max_width, max_height)
    if cache_key in text_surf_cache:
        return text_surf_cache[cache_key]

    fit_height = False
    if max_width == None and max_height == None:
        if window_width == None:
            text_surface = render_text_line(text, font, font_size, text_color)
        else:
            text_surface = render_text(text, font, font_size, text_color, max_width=window_width)
        text_surf_cache[cache_key] = text_surface
        return text_surface
    elif max_height == None:
        fit_height = True
        max_height = 9999
    
    font = pg.font.SysFont(font, font_size)
    lines = text.split('\n')

    text_surface = create_surface(vec2(max_width, max_height), (0, 0, 0, 0), pg.SRCALPHA)
    
    line_height = font.get_linesize()
    x_offset = 0
    y_offset = 0
    
    for line in lines:
        words = line.split(' ')
        current_line = ""
        for word in words:
            space = " " if len(words) > 1 else ""
            test_line = current_line + word + space
            
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
                x_offset = max(x_offset, font.size(test_line)[0]+1)
            else:
                rendered_line = font.render(current_line.strip(), True, text_color)
                x_offset = max(x_offset, rendered_line.size[0]+1)
                text_surface.blit(rendered_line, (0, y_offset))
                y_offset += line_height
                current_line = word + " "
                if y_offset + line_height > max_height:
                    if fit_height:
                        return text_surface.subsurface((0, 0, x_offset, y_offset))
                    return text_surface
        
        rendered_line = font.render(current_line.strip(), True, text_color)
        text_surface.blit(rendered_line, (0, y_offset))
        y_offset += line_height
        
        if y_offset > max_height:
            break

    text_surf_cache[cache_key] = text_surface
    if fit_height:
        return text_surface.subsurface((0, 0, x_offset, y_offset))
    return text_surface

def draw_circle(surf:pg.Surface, color:vec3, center:vec2, radius:int, anti_aliasing=False):
    if anti_aliasing:
        pg.draw.aacircle(surf, color, center, radius-1)
    else:
        pg.draw.circle(surf, color, center, radius)

def draw_anti_circle(wm:Window_Manager, pos:vec2=None, radius:int=20, color:vec3=vec3(0, 0, 0), alpha:int=0, circle_alpha:int=255):
    pos = MOUSE.position if pos == None else pos
    surf_size = vec2(wm.window.size)
    surf = create_surface(surf_size, (*color, 255-alpha), pg.SRCALPHA)

    # Draw a transparent circle
    draw_circle(surf, (0, 0, 0, 255-circle_alpha), pos, radius, anti_aliasing=True)

    return surf

def draw_rect(surf:pg.Surface, pos:vec2, size:vec2, color:vec3=vec3(0, 0, 0), rect_alpha:int=255):
    pg.draw.rect(surf, (*color, rect_alpha), (*pos, *size))

def draw_rect_outline(surf:pg.Surface, pos:vec2, size:vec2, color:vec3=vec3(0, 0, 0), rect_alpha:int=255, width:int=1):
    pg.draw.rect(surf, (*color, rect_alpha), (*pos, *size), width)

def draw_anti_rect(wm:Window_Manager, pos:vec2, size:vec2, color:vec3=vec3(0, 0, 0), alpha:int=0, rect_alpha:int=255):
    surf_size = vec2(wm.window.size)
    surf = create_surface(surf_size, (*color, 255-alpha), pg.SRCALPHA)

    # draw a transparent rect
    pg.draw.rect(surf, (0, 0, 0, 255-rect_alpha), (*pos, *size))

    return surf

boundary_cache:dict[tuple[vec3, vec2, vec2], pg.Surface] = {}
def create_boundary(bg_color:vec3, size:vec2, boundary_size:vec2) -> pg.Surface:
    if (bg_color, size, boundary_size) in boundary_cache:
        return copy(boundary_cache[(bg_color, size, boundary_size)])
    
    surf = create_surface(size)
    pg.draw.rect(surf, vec3(255)-bg_color, (0, 0, *size))
    pg.draw.rect(surf, bg_color, (*(boundary_size/2), *(size-boundary_size)))
    boundary_cache[(bg_color, size, boundary_size)] = copy(surf)
    return surf

def draw_boundary(surf:pg.Surface, bg_color:vec3, size:vec2, boundary_size:vec2):
    pg.draw.rect(surf, vec3(255)-bg_color, (0, 0, *size))
    pg.draw.rect(surf, bg_color, (*(boundary_size/2), *(size-boundary_size)))

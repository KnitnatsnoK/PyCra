from value_assets import *
from window_manager import Window_Manager, ALL_WINDOW_MANAGERS
from imports import MOUSE, KEYS, center, random_vec2, random_vec3, pointing_amount, try_loading_image, fetch_texture

class GameObject:
    G = G
    def __init__(self, window_manager:Window_Manager, scene:int, layer:int|str, pos:vec2, size:vec2, user_creation=True, physics_obj:bool=True, solid:bool=True, mass:float=inf, **kwargs):
        # parameters for saving
        self.engine_generated = not user_creation
        self.parameters = [type(self), ALL_WINDOW_MANAGERS.index(window_manager), kwargs, layer, copy(pos), copy(size), user_creation, physics_obj, (solid,)]
        
        # parameters
        self.id = id(self)

        if not hasattr(self, "project_dependend"):
            self.project_dependend = False

        self.scene = scene
        self.layer = layer
        self.window_manager = ALL_WINDOW_MANAGERS[window_manager] if isinstance(window_manager, int) else window_manager

        self.static = True
        self.pos = center(copy(pos), size, **kwargs)
        self.size = size
        self.physics_obj = physics_obj
        self.solid = solid

        # for physics
        self.vel = vec2(0)
        self.saved_vel = copy(self.vel)
        self.mass = mass
        self.e = 0
        
        self.center = self.pos + self.size*0.5

        # image
        self.animation_manager:AnimationManager|None = None

        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        self.image:Texture|Image = try_UI_tex_cache(GameObject, ())
        if self.image:
            return
        
        surf = create_surface(self.size, color=vec3(255))

        self.image:Texture|Image = cached_UI_tex_load(self.window_manager.renderer, surf, GameObject, ())

    def get_window_pos(self) -> vec2:
        return self.pos - get_global("<Camera>").value.pos

    def draw(self):
        window_pos = self.get_window_pos()
        if not ((-self.size.x < window_pos.x < self.window_manager.window_size.x) and (-self.size.y < window_pos.y < self.window_manager.window_size.y)):
            return
        if self.image_update_needed:
            self.image_update_needed = False
            self.update_image()
        self.image.draw(dstrect=(window_pos, self.size))

    def handle_animation(self, delta_time:float):
        if self.animation_manager is not None:
            self.animation_manager.update(delta_time)

    def inputs(self, fps_factor:float):
        pass

    def physics(self, fps_factor:float):
        pass

    def tick(self, fps_factor:float):
        self.inputs(fps_factor)
        if self.physics_obj and not self.static:
            self.physics(fps_factor)

    def position_at(self, pos:vec2):
        self.pos = center(copy(pos), self.size, **self.parameters[2])

class DynamicObject(GameObject):
    def __init__(self, window_manager:Window_Manager, scene:int, layer:int|str, pos:vec2, size:vec2, user_creation=True, physics_obj:bool=True, mass:float=None, e:float=0, **kwargs):
        if not isinstance(self, DynamicTextureObject):
            self.color = random_vec3(0, 255)
        mass = mass if mass is not None else size.x * size.y / 1000
        
        window_manager = ALL_WINDOW_MANAGERS[window_manager] if isinstance(window_manager, int) else window_manager
        super().__init__(window_manager, scene, layer, pos, size, user_creation, physics_obj, False, mass, **kwargs)
        self.parameters = [type(self), ALL_WINDOW_MANAGERS.index(window_manager), kwargs, layer, copy(pos), copy(size), user_creation, physics_obj, (mass, e)]

        self.static = False
        self.acc = vec2(0)
        self.e = e
        self.ground = False

    def update_image(self):
        self.image:Texture|Image = try_UI_tex_cache(DynamicObject, ())
        if self.image:
            return
        
        surf = create_surface(self.size, color=self.color)

        self.image:Texture|Image = cached_UI_tex_load(self.window_manager.renderer, surf, DynamicObject, (self.color))

    def inputs(self, fps_factor:float):
        pass

    def physics(self, fps_factor:float):
        self.acc.y = GameObject.G * (0.6 + self.mass*0.4)
        self.ground = False

        self.vel += self.acc * fps_factor
        self.saved_vel = copy(self.vel)

        self.pos += self.vel * fps_factor
        if False:
            if self.pos.x < 0:
                self.pos.x = 0
                self.vel *= 0.7
                self.vel.x *= -1
            elif self.pos.x + self.size.x > self.window_manager.window_size.x:
                self.pos.x = self.window_manager.window_size.x - self.size.x
                self.vel *= 0.7
                self.vel.x *= -1

            if self.pos.y < 0:
                self.pos.y = 0
                self.vel *= 0.7
                self.vel.y *= -1
            elif self.pos.y + self.size.y > self.window_manager.window_size.y:
                self.pos.y = self.window_manager.window_size.y - self.size.y
                self.vel *= 0.7
                self.vel.y *= -1

        self.center = self.pos + self.size*0.5

class TextureObject(GameObject):
    def __init__(self, window_manager:Window_Manager, scene:int, layer:int|str, pos:vec2, size:vec2, user_creation=True, image_path:str="PyCra Icon.jpg", project_path:bool=True, **kwargs):
        self.image_path = image_path
        self.project_dependend = project_path

        size = size * vec2(try_loading_image(image_path, self.project_dependend)[0].size) if isinstance(size, int) else (vec2(try_loading_image(image_path, self.project_dependend)[0].size) if size is None else size)

        window_manager = ALL_WINDOW_MANAGERS[window_manager] if isinstance(window_manager, int) else window_manager
        super().__init__(window_manager, scene, layer, pos, size, user_creation, False, **kwargs)
        self.parameters = [type(self), ALL_WINDOW_MANAGERS.index(window_manager), kwargs, layer, copy(pos), copy(size), user_creation, False, (image_path, project_path)]

    def update_image(self):
        if get_placeholder_status(TextureObject, get_global("<Project_Opened>").value, (self.image_path, self.project_dependend)):
            self.image:Texture|Image = try_UI_tex_cache(TextureObject, None)
            return
        
        self.image = fetch_texture(self.window_manager, self.image_path, self.project_dependend)

    def get_window_pos(self):
        return self.pos

class BackgroundObject(TextureObject):
    def __init__(self, window_manager:Window_Manager, scene:int, layer:int|str, pos:vec2, size:vec2, user_creation=True, depth:float=0, x_axis:bool=True, y_axis:bool=True, image_path:str="PyCra Icon.jpg", project_path:bool=True, **kwargs):
        self.project_dependend = project_path
        self.depth = depth
        self.x_axis = x_axis
        self.y_axis = y_axis

        size = size * vec2(try_loading_image(image_path, self.project_dependend)[0].size) if isinstance(size, int) else (vec2(try_loading_image(image_path, self.project_dependend)[0].size) if size is None else size)
        
        window_manager = ALL_WINDOW_MANAGERS[window_manager] if isinstance(window_manager, int) else window_manager
        super().__init__(window_manager, scene, layer, pos, size, user_creation, image_path, project_path, **kwargs)
        self.parameters = [type(self), ALL_WINDOW_MANAGERS.index(window_manager), kwargs, layer, copy(pos), copy(size), user_creation, False, (depth, x_axis, y_axis, image_path, project_path)]

    def draw(self):
        window_pos = self.get_window_pos()

        start_x = window_pos.x%self.size.x - self.size.x
        start_y = window_pos.y%self.size.y - self.size.y

        cols = int(self.window_manager.window_size.x // self.size.x) + 2
        rows = int(self.window_manager.window_size.y // self.size.y) + 2

        if self.image_update_needed:
            self.image_update_needed = False
            self.update_image()

        for col in range(cols):
            for row in range(rows):
                pos = vec2(start_x + col * self.size.x, start_y + row * self.size.y)
                if not ((-self.size.x < pos.x < self.window_manager.window_size.x) and (-self.size.y < pos.y < self.window_manager.window_size.y)):
                    continue
                self.image.draw(dstrect=(pos, self.size))

    def get_window_pos(self):
        cam_pos:vec2 = get_global("<Camera>").value.pos / self.depth
        return self.pos - vec2(cam_pos.x*self.x_axis, cam_pos.y*self.y_axis)

class DynamicTextureObject(DynamicObject):
    def __init__(self, window_manager:Window_Manager, scene:int, layer:int|str, pos:vec2, size:vec2, user_creation=True, physics_obj:bool=True, mass:float=None, e:float=0, image_path:str="PyCra Icon.jpg", project_path:bool=True, **kwargs):
        self.image_path = image_path
        self.project_dependend = project_path

        size = size * vec2(try_loading_image(self.image_path, self.project_dependend)[0].size) if isinstance(size, int) else (vec2(try_loading_image(self.image_path, self.project_dependend)[0].size) if size is None else size)

        window_manager = ALL_WINDOW_MANAGERS[window_manager] if isinstance(window_manager, int) else window_manager
        super().__init__(window_manager, scene, layer, pos, size, user_creation, physics_obj, mass, e, **kwargs)
        self.parameters = [type(self), ALL_WINDOW_MANAGERS.index(window_manager), kwargs, layer, copy(pos), copy(size), user_creation, physics_obj, (mass, e, image_path, project_path)]

    def update_image(self):
        if get_placeholder_status(DynamicTextureObject, get_global("<Project_Opened>").value, (self.image_path, self.project_dependend)):
            self.image:Texture|Image = try_UI_tex_cache(DynamicTextureObject, None)
            return
        
        self.image = fetch_texture(self.window_manager, self.image_path, self.project_dependend)

SCENES:list[list[GameObject]] = [] # no scenes
set_global("<SCENES>", SCENES)
SCENE_NAMES:list[str] = [] # no scene names
set_global("<Scene_Names>", SCENE_NAMES)
SCENE = Variable(0)
set_global("<Scene>", SCENE)

LAYERS:list[list[str]] = [] # no layers
set_global("<LAYERS>", LAYERS)

def add_layer(layer_name:str, index:int=None, scene:int=None):
    layer_scene = scene if isinstance(scene, int) else SCENE.value
    if layer_name in LAYERS[layer_scene]:
        LAYERS[layer_scene].remove(layer_name)
    if index is None:
        LAYERS[layer_scene].append(layer_name)
        return
    
    for _ in range(index-len(LAYERS[layer_scene])):
        LAYERS[layer_scene].append("")
    if index < len(LAYERS[layer_scene]):
        if LAYERS[layer_scene][index] == "":
            LAYERS[layer_scene][index] = layer_name
            return
    LAYERS[layer_scene].insert(index, layer_name)

def rename_layer(old_layer_name:str, new_layer_name:str, scene:int=None):
    layer_scene = scene if isinstance(scene, int) else SCENE.value
    if old_layer_name in LAYERS[layer_scene]:
        if new_layer_name not in LAYERS[layer_scene]:
            LAYERS[layer_scene].insert(LAYERS[layer_scene].index(old_layer_name), new_layer_name)
        LAYERS[layer_scene].remove(old_layer_name)

        for game_obj in SCENES[layer_scene]:
            if game_obj.layer == old_layer_name:
                game_obj.layer = new_layer_name

def delete_layer(layer_name:str, scene:int=None, replacement_layer:str|int=0):
    layer_scene = scene if isinstance(scene, int) else SCENE.value
    if layer_name in LAYERS[layer_scene]:
        layer_index = LAYERS[layer_scene].index(layer_name) - 1
        LAYERS[layer_scene].remove(layer_name)
        while layer_index >= 0 and LAYERS[layer_scene][layer_index] == "":
            LAYERS[layer_scene].pop(layer_index)
            layer_index -= 1

        replacement_layer_name = LAYERS[layer_scene][replacement_layer] if isinstance(replacement_layer, int) else replacement_layer
        for game_obj in SCENES[layer_scene]:
            if game_obj.layer == layer_name:
                game_obj.layer = replacement_layer_name

class Animation:
    def __init__(self, frames, frame_duration:list[float]|float, loop=True):
        self.frames:list[Texture] = frames
        self.frame_durations = frame_duration if isinstance(frame_duration, list) else [frame_duration for _ in range(len(frames))]
        self.loop = loop

        self.current_frame = 0
        self.time_accumulator = 0

        self.finish = False

    def update(self, delta_time):
        self.time_accumulator += delta_time
        if self.time_accumulator >= self.frame_durations[self.current_frame]:
            self.time_accumulator -= self.frame_durations[self.current_frame]
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0 if self.loop or self.finish else len(self.frames) - 1
            return True
        return False

    def get_frame(self):
        return self.frames[self.current_frame]
    
class AnimationManager:
    def __init__(self, game_obj:GameObject, animations:dict[str, Animation]={}):
        self.game_obj = game_obj
        self.animations = animations
        self.current_animation = None

        self.await_finish = False

        # fix lazyness
        for animation in self.animations.values():
            for i, frame in enumerate(animation.frames):
                if isinstance(frame, str):
                    animation.frames[i] = fetch_texture(self.game_obj.window_manager, frame)

    def add_animation(self, name:str, animation:Animation):
        self.animations[name] = animation

        # fix lazyness
        for i, frame in enumerate(animation.frames):
            if isinstance(frame, str):
                animation.frames[i] = fetch_texture(self.game_obj.window_manager, frame)

    def play(self, name:str):
        """Switch to a different animation."""
        if RUN_BY_PROJECT and name in self.animations:
            if self.current_animation != self.animations[name]:
                if self.current_animation is not None:
                    self.current_animation.finish = False
                self.await_finish = False

                self.current_animation = self.animations[name]
                self.current_animation.current_frame = 0
                self.current_animation.time_accumulator = 0

    def stop(self, finish_animation=False, return_idle=False):
        if self.current_animation is None or (finish_animation and self.await_finish):
            return
        if finish_animation:
            self.current_animation.finish = True
            self.await_finish = (return_idle,)
        else:
            self.interrupt_current_animation(return_idle)

    def interrupt_current_animation(self, return_idle=False):
        self.current_animation.finish = False
        self.current_animation = None
        if return_idle:
            self.game_obj.image_update_needed = True

    def update(self, delta_time:float):
        if self.current_animation is not None:
            if self.current_animation.update(delta_time):
                if self.current_animation.current_frame == 0:
                    if not self.current_animation.loop or self.await_finish:
                        self.interrupt_current_animation(self.await_finish[0])
                        self.await_finish = False
                        return
                self.game_obj.image = self.current_animation.get_frame()

def change_to_scene(scene:int|str, engine_change=False):
    if engine_change or RUN_BY_PROJECT:
        SCENE.value = scene if isinstance(scene, int) else SCENE_NAMES.index(scene)

def get_valid_scene(scene:int|str|None):
    return scene if isinstance(scene, int) else (SCENE.value if scene is None else SCENE_NAMES.index(scene))

def get_valid_layer(scene:int, layer:str|int):
    return layer if isinstance(layer, int) else LAYERS[scene].index(layer)

set_global("<Last_Added_Game_Object>", None)
def add_game_object_to_scene(obj_scene:int, game_object:GameObject):
    set_global("<Last_Added_Game_Object>", game_object)
    if len(SCENES[obj_scene]) == 0:
        SCENES[obj_scene].append(game_object)
        return
    
    game_object_layer = get_valid_layer(obj_scene, game_object.layer)
    for i, game_obj in enumerate(SCENES[obj_scene]):
        if i == len(SCENES[obj_scene])-1:
            SCENES[obj_scene].insert(len(SCENES[obj_scene]), game_object)
            return
        elif get_valid_layer(game_obj.scene, game_obj.layer) > game_object_layer:
            SCENES[obj_scene].insert(i, game_object)
            return

def delete_game_object(game_object:GameObject):
    if game_object == get_global("<Selected_Object>").value:
        set_global("<Selected_Object>", None)
    SCENES[game_object.scene].remove(game_object)

def create_Game_Object(scene:int|str|None, layer:int|str, window_manager:int, pos:vec2, size:vec2, user_creation=True, physics_obj:bool=True, **kwargs):
    obj_scene = get_valid_scene(scene)
    game_object = GameObject(window_manager, obj_scene, layer, pos, size, user_creation, physics_obj, **kwargs)
    if scene is not None:
        add_game_object_to_scene(obj_scene, game_object)
    return game_object

def create_Dynamic_Object(scene:int|str|None, layer:int|str, window_manager:int, pos:vec2, size:vec2, mass:float=None, e:float=0, user_creation=True, physics_obj:bool=True, **kwargs):
    obj_scene = get_valid_scene(scene)
    dynamic_object = DynamicObject(window_manager, obj_scene, layer, pos, size, user_creation, physics_obj, mass, e, **kwargs)
    if scene is not None:
        add_game_object_to_scene(obj_scene, dynamic_object)
    return dynamic_object

def create_Texture_Object(scene:int|str|None, layer:int|str, window_manager:int, pos:vec2, size:vec2, image_path:str="PyCra Icon.jpg", project_path:bool=True, user_creation=True, **kwargs):
    obj_scene = get_valid_scene(scene)
    texture_object = TextureObject(window_manager, obj_scene, layer, pos, size, user_creation, image_path, project_path, **kwargs)
    if scene is not None:
        add_game_object_to_scene(obj_scene, texture_object)
    return texture_object

def create_Background_Object(scene:int|str|None, layer:int|str, window_manager:int, pos:vec2, size:vec2, depth:float=0, x_axis:bool=True, y_axis:bool=True, image_path:str="PyCra Icon.jpg", project_path:bool=True, user_creation=True, **kwargs):
    obj_scene = get_valid_scene(scene)
    background_object = BackgroundObject(window_manager, obj_scene, layer, pos, size, user_creation, depth, x_axis, y_axis, image_path, project_path, **kwargs)
    if scene is not None:
        add_game_object_to_scene(obj_scene, background_object)
    return background_object

def create_Dynamic_Texture_Object(scene:int|str|None, layer:int|str, window_manager:int, pos:vec2, size:vec2, mass:float=None, e:float=0, image_path:str="PyCra Icon.jpg", project_path:bool=True, user_creation=True, physics_obj:bool=True, **kwargs):
    obj_scene = get_valid_scene(scene)
    dynamic_texture_object = DynamicTextureObject(window_manager, obj_scene, layer, pos, size, user_creation, physics_obj, mass, e, image_path, project_path, **kwargs)
    if scene is not None:
        add_game_object_to_scene(obj_scene, dynamic_texture_object)
    return dynamic_texture_object

def create_Object_from_parameters(parameters:tuple, scene:int|str|None) -> GameObject:
    obj_scene = get_valid_scene(scene)
    GameObjectClass, Window_Manager_index, kwargs, layer, pos, size, user_creation, physics_obj, parameters = parameters
    game_object = GameObjectClass(ALL_WINDOW_MANAGERS[Window_Manager_index], obj_scene, layer, pos, size, user_creation, physics_obj, *parameters, **kwargs)
    if obj_scene is not None:
        add_game_object_to_scene(obj_scene, game_object)
    return game_object

def sweep_and_prune_x(obj_list:list[GameObject]):
    sorted_game_objects = []
    active_group = []
    max_active = float('-inf')
    
    objs = sorted(obj_list, key=lambda obj: obj.pos.x)  # Sort objects by x-position
    
    for game_object in objs:
        game_object_min = game_object.pos.x
        game_object_max = game_object.pos.x + game_object.size.x
        
        # Check if the current object overlaps with the active group
        if active_group and game_object_min <= max_active:
            active_group.append(game_object)
            max_active = max(max_active, game_object_max)  # Extend active boundary
        else:
            # Save the current group if it has more than one object and start a new group
            if len(active_group) > 1:
                sorted_game_objects.append(active_group)
            active_group = [game_object]
            max_active = game_object_max
    
    # Add the last group if it has more than one object
    if len(active_group) > 1:
        sorted_game_objects.append(active_group)

    if MOUSE.down_buttons[2]:
        print(sorted_game_objects)
    
    return sorted_game_objects

def sweep_and_prune_y(obj_list:list[GameObject]):
    sorted_game_objects = []
    active_group = []
    max_active = float('-inf')
    
    objs = sorted(obj_list, key=lambda obj: obj.pos.y)  # Sort objects by x-position
    
    for game_object in objs:
        game_object_min = game_object.pos.y
        game_object_max = game_object.pos.y + game_object.size.y
        
        # Check if the current object overlaps with the active group
        if active_group and game_object_min <= max_active:
            active_group.append(game_object)
            max_active = max(max_active, game_object_max)  # Extend active boundary
        else:
            # Save the current group if it has more than one object and start a new group
            if len(active_group) > 1:
                sorted_game_objects.append(active_group)
            active_group = [game_object]
            max_active = game_object_max
    
    # Add the last group if it has more than one object
    if len(active_group) > 1:
        sorted_game_objects.append(active_group)

    if MOUSE.down_buttons[2]:
        print(sorted_game_objects)

    return sorted_game_objects

def check_AABB(pos0: vec2, size0: vec2, pos1: vec2, size1: vec2):
    return (pos0.x < pos1.x + size1.x and
            pos0.x + size0.x > pos1.x and
            pos0.y < pos1.y + size1.y and
            pos0.y + size0.y > pos1.y)

def resolve_AABB(obj0:DynamicObject, obj1:DynamicObject, pos0: vec2, size0: vec2, pos1: vec2, size1: vec2, must_collide=False):
    # Calculate the half extents
    half_size0 = size0 * 0.5
    half_size1 = size1 * 0.5

    # Calculate the difference between centers
    delta = (pos0 + half_size0) - (pos1 + half_size1)

    # Calculate the total extents
    total_extents = half_size0 + half_size1

    # Check for collision
    if must_collide or (abs(delta.x) < total_extents.x and abs(delta.y) < total_extents.y):
        # collision resolution: find the minimum translation vector
        overlap_x = total_extents.x - abs(delta.x)
        overlap_y = total_extents.y - abs(delta.y)

        e = min(obj0.e, obj1.e)
        normal = normalize(vec2(overlap_x, 0)) if overlap_x < overlap_y else normalize(vec2(0, overlap_y)) #normalize(obj0.center - obj1.center)
        vel_rel = dot(obj0.saved_vel - obj1.saved_vel, normal)
        j = -(1 + e) * vel_rel / (1/obj0.mass + 1/obj1.mass)

        impulse = j * normal
        obj0.vel += impulse / obj0.mass
        obj1.vel -= impulse / obj1.mass

        if overlap_x < overlap_y:
            if delta.x > 0:
                pos0.x += overlap_x  # Move pos0 to the right
            else:
                pos0.x -= overlap_x  # Move pos0 to the left
        else:
            if delta.y > 0:
                pos0.y += overlap_y  # Move pos0 down
            else:
                pos0.y -= overlap_y  # Move pos0 up
                obj0.ground = True
        if RUN_BY_ENGINE:
            obj0.parameters[4] = copy(obj0.pos + obj0.size/2)
        
        return True

    return False

def Broad_Phase_Detection(obj_list:list[GameObject]):
    #game_object_pairs = []

    # coords:dict[vec2, list[GameObject]] = {}
    # GRID_SIZE = 100
    # def get_pos_coord(pos:vec2):
    #     return vec2((int(pos.x/GRID_SIZE)), int(pos.y/GRID_SIZE))
    
    # def add_obj_to_coord(pos:vec2, game_obj):
    #     coordinate = get_pos_coord(pos)
    #     if coordinate in coords:
    #         coords[coordinate].append(game_obj)
    #     else:
    #         coords[coordinate] = [game_obj]

    # for obj0 in obj_list:
    #     if obj0.physics_obj:
    #         add_obj_to_coord(obj0.center, obj0)

    #print(coords)

    for obj0 in obj_list:
        if obj0.static or not obj0.physics_obj:
            continue
        for obj1 in obj_list:
            if obj0 == obj1 or not obj1.physics_obj:
                continue
            if check_AABB(obj0.pos, obj0.size, obj1.pos, obj1.size): # Narrow Phase Detection
                pair:tuple[DynamicObject, DynamicObject] = (obj0, obj1)
                #game_object_pairs.append(pair)
                
                pointer = None
                if RUN_BY_ENGINE and SELECTED_OBJ is not None:
                    if SELECTED_OBJ == pair[0]:
                        pointer = 0
                    elif SELECTED_OBJ == pair[1]:
                        pointer = 1
                if pointer is None:
                    pointer = 0 if pair[1].solid or pointing_amount(pair[0].saved_vel, pair[0].pos, pair[1].center) > pointing_amount(pair[1].saved_vel, pair[1].pos, pair[0].center) else 1
                resolve_AABB(pair[pointer], pair[1-pointer], pair[pointer].pos, pair[pointer].size, pair[1-pointer].pos, pair[1-pointer].size)
        # for offset in [vec2(-1, -1), vec2(0, -1), vec2(1, -1),
        #                vec2(-1, 0) , vec2(0, 0) , vec2(1, 0),
        #                vec2(-1, 1) , vec2(0, 1) , vec2(1, 1)]:
        #     coord = get_pos_coord(obj0.center) + offset
        #     if coord not in coords:
        #         continue
        #     for obj1 in coords[coord]:
        #         if obj0 == obj1 or not obj1.physics_obj:
        #             continue
        #         if check_AABB(obj0.pos, obj0.size, obj1.pos, obj1.size): # Narrow Phase Detection
        #             pair:tuple[DynamicObject, DynamicObject] = (obj0, obj1)
        #             #game_object_pairs.append(pair)
                    
        #             pointer = None
        #             if RUN_BY_ENGINE and SELECTED_OBJ is not None:
        #                 if SELECTED_OBJ == pair[0]:
        #                     pointer = 0
        #                 elif SELECTED_OBJ == pair[1]:
        #                     pointer = 1
        #             if pointer is None:
        #                 pointer = 0 if pair[1].solid or pointing_amount(pair[0].saved_vel, pair[0].pos, pair[1].center) > pointing_amount(pair[1].saved_vel, pair[1].pos, pair[0].center) else 1
        #             resolve_AABB(pair[pointer], pair[1-pointer], pair[pointer].pos, pair[pointer].size, pair[1-pointer].pos, pair[1-pointer].size)

    #return game_object_pairs

def Narrow_Phase_Detection(game_object_pairs:list[tuple[DynamicObject, DynamicObject]]):
    for pair in game_object_pairs:
        pointer = 0 if pair[1].solid or pointing_amount(pair[0].saved_vel, pair[0].pos, pair[1].center) > pointing_amount(pair[1].saved_vel, pair[1].pos, pair[0].center) else 1
        resolve_AABB(pair[pointer], pair[1-pointer], pair[pointer].pos, pair[pointer].size, pair[1-pointer].pos, pair[1-pointer].size)

SELECTED_OBJ = Variable(None)
TICK_GAME_OBJECTS = Variable(True)
set_global("TICK_GAME_OBJECTS", TICK_GAME_OBJECTS)
def tick_game_objects(fps_factor:float, delta_time:float, update=True):
    global SELECTED_OBJ
    if MOUSE.down_buttons[0] and KEYS.check_pressed(pg.K_SPACE) and ALL_WINDOW_MANAGERS[0].last_action_element is None:
        if not KEYS.check_pressed(pg.K_LSHIFT):
            create_Dynamic_Texture_Object(SCENE.value, "game_objects", ALL_WINDOW_MANAGERS[0], copy(MOUSE.scene_position), vec2(40), user_creation=False, center=True)
        else:
            for _ in range(5):
                create_Dynamic_Object(SCENE.value, "game_objects", ALL_WINDOW_MANAGERS[0], copy(MOUSE.scene_position+random_vec2(-100, 100)), vec2(30), user_creation=False, center=True)
        SELECTED_OBJ.value = get_global("<Last_Added_Game_Object>").value

        set_global("<Game Objects>", f"Game Objects: {len(SCENES[SCENE.value])}")

    if update and TICK_GAME_OBJECTS.value:
        for game_object in SCENES[SCENE.value]:
            game_object.tick(fps_factor)

    if not MOUSE.pressed_buttons[0]:
        SELECTED_OBJ.value = None
    if SELECTED_OBJ.value is not None:
        if RUN_BY_PROJECT:
            SELECTED_OBJ.value.vel = MOUSE.scene_position-SELECTED_OBJ.value.center
        else:
            SELECTED_OBJ.value.position_at(MOUSE.scene_position)
            SELECTED_OBJ.value.vel = vec2(0)
            SELECTED_OBJ.value.parameters[4] = copy(MOUSE.scene_position)
    
    saved_time = perf_counter()
    #game_object_pairs = Broad_Phase_Detection(SCENES[SCENE.value])
    Broad_Phase_Detection(SCENES[SCENE.value])
    if MOUSE.down_buttons[1]:
        print("Broad Phase", f"{(perf_counter()-saved_time)*1000:.2f}ms")

    # saved_time = perf_counter()
    # Narrow_Phase_Detection(game_object_pairs)
    # if MOUSE.down_buttons[1]:
    #     print("Narrow Phase", f"{(perf_counter()-saved_time)*1000:.2f}ms")
    
    handle_selected_objects = MOUSE.down_buttons[0] and ALL_WINDOW_MANAGERS[0].last_action_element is None and RUN_BY_ENGINE
    if handle_selected_objects:
        old_selected_obj = get_global("<Selected_Object>").value
        set_global("<Selected_Object>", None)
    for game_object in SCENES[SCENE.value]:
        game_object.center = game_object.pos + game_object.size*0.5
        game_object.handle_animation(delta_time)
        game_object.draw()

        if handle_selected_objects:
            window_pos = game_object.get_window_pos()
            if (window_pos.x < MOUSE.position.x < window_pos.x + game_object.size.x) and (window_pos.y < MOUSE.position.y < window_pos.y + game_object.size.y):
                if old_selected_obj == game_object:
                    set_global("<Selected_Object>", None)
                else:
                    set_global("<Selected_Object>", game_object)

def save_new_scene(scene:int|list[GameObject], layers:None|list[str], path:str, name:str):
    scene_path = path + name + ".pkl.gz"
    if os.path.exists(scene_path):
        if PRINT_ASSET_EXISTENCE:
            print(f"The scene '{name}' already exists.")
        return False
    else:
        if isinstance(scene, int):
            game_objects = SCENES[scene]
            layers = LAYERS[scene]
        else:
            game_objects = scene
            layers = layers
        with gzip.open(scene_path, 'wb') as file:
            pickle.dump((layers, [game_object.parameters for game_object in game_objects if game_object.engine_generated]), file)
        return True

def save_scene(scene:int|list[GameObject], layers:None|list[str], path:str, name:str):
    scene_path = path + name + ".pkl.gz"
    if isinstance(scene, int):
        game_objects = SCENES[scene]
        layers = LAYERS[scene]
    else:
        game_objects = scene
        layers = layers
    with gzip.open(scene_path, 'wb') as file:
        pickle.dump((layers, [game_object.parameters for game_object in game_objects if game_object.engine_generated]), file)

def load_scene(scene:int, path:str, name:str):
    saved_time = perf_counter()
    scene_path = path + name + ".pkl.gz"
    with gzip.open(scene_path, 'rb') as file:
        while len(SCENES) <= scene:
            SCENES.append([])
            SCENE_NAMES.append("")
            LAYERS.append([])
        set_global("<Loaded Scene>", f"Scene: {SCENE.value+1}/{len(SCENES)}")
        
        loaded_file = pickle.load(file)
        LAYERS[scene] = loaded_file[0]
        SCENES[scene] = [create_Object_from_parameters(parameters, scene=scene) for parameters in loaded_file[1]]
        SCENE_NAMES[scene] = name

    set_global("<Game Objects>", f"Game Objects: {len(SCENES[scene])}")

    print(f"Scene load time: {(perf_counter()-saved_time)*1000:.2f}ms")

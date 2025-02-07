if __name__ == "__main__":
    from assets import *

from value_assets import *
from imports import *
from UI import *
from CUUI import *
from objects import tick_game_objects, create_Object_from_parameters, GameObject, SCENES, SCENE_NAMES, SCENE, SELECTED_OBJ
from joystick_manager import reset_axes_changes, handle_joystick_event, apply_joystick_changes, render_joysticks_input, joystick_managers

WINDOW_SIZE = MAIN_MONITOR_SIZE / 2
main_window, main_window_manager = create_window("PyCra Engine -- beta", WINDOW_SIZE)
main_window_name = set_global("<main_window_name>", main_window.title)

set_global("main_window_manager", main_window_manager)
test_project_name = "Test Project"
create_project(test_project_name)
open_project(main_window_manager, folder_path=f"Projects\\{test_project_name}")

for jm in joystick_managers:
    window_to_top(jm.window_manager.window)

create_Rect_Outline(main_window_manager, ALL_WINDOW_MANAGERS[0].window_size/2, vec2(200, 100), vec3(0, 0, 255), width=4, action=0, center=True)

create_toolbar(main_window_manager, vec2(0), [Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Project", font_size=16, action=[   Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Open", font_size=16, action=1),
                                                                                                                                                    Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Save", font_size=16, action=2),
                                                                                                                                                    Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Create", font_size=16, action=3),
                                                                                                                                                    ]),
                                              Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Quit", font_size=16, action=0),
                                              Icon(main_window_manager, vec2(0), vec2(31), default_bg=True, image_path="run_button.png", action=0),
                                              Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text=set_global("<Game Objects>", f"Game Objects: {len(SCENES[SCENE.value])}"), font_size=16),
                                              Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text=set_global("<Loaded Scene>", f"Scene: {SCENE.value+1}/{len(SCENES)}"), font_size=16, action=[   Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Next Scene", font_size=16, action=4),
                                                                                                                                                                                                                Text_Box(main_window_manager, vec2(0), text_color=vec3(225), text="Create Scene", font_size=16, action=5),
                                                                                                                                                                                                                ]),
                                              ], user_creation=False)

def tick(): # for the Python Interpreter :P
    pass

def handle_tick():
    global tick
    if get_global("<Update_tick_func>").value is not None:
        tick = get_global("<Update_tick_func>").value
        set_global("<Update_tick_func>", None)
    # tick()

def handle_events():
    MOUSE.wheel = vec2(0)
    reset_axes_changes()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            quit_engine()
        elif event.type == pg.WINDOWFOCUSGAINED:
            set_top_window(event.window)
        elif event.type == pg.JOYBUTTONDOWN:
            handle_joystick_event(event)
        elif event.type == pg.JOYBUTTONUP:
            handle_joystick_event(event)
        elif event.type == pg.JOYAXISMOTION:
            handle_joystick_event(event)
        elif event.type == pg.JOYHATMOTION:
            handle_joystick_event(event)
        elif event.type == pg.MOUSEWHEEL:
            MOUSE.handle_wheel(event)
        elif event.type == pg.KEYDOWN:
            if event.key >= len(KEYS.down):
                KEYS.down_extra_key(event.key)
        elif event.type == pg.KEYUP:
            if event.key >= len(KEYS.up):
                KEYS.up_extra_key(event.key)
        else:
            pass

    apply_joystick_changes()
    render_joysticks_input()

COPY = None
def handle_keymouse_input():
    global COPY
    KEYS.get_key_data()
    KEYS.update_extra_keys()
    MOUSE.get_data()
    if KEYS.down[pg.K_ESCAPE]:
        delete_top_window()
    if RUN_BY_ENGINE:
        if KEYS.check_pressed(pg.K_F5):
            run_project(main_window_manager)
        if KEYS.check_pressed(pg.K_LCTRL):
            if KEYS.down[pg.K_r]:
                reload_project_dependend_assets(main_window_manager)
            if KEYS.down[pg.K_s]:
                save_scene(SCENES[SCENE.value], f"Projects\\{get_global("<Project_Opened>").value}\\Scenes\\", SCENE_NAMES[SCENE.value])
                print(f"Saved {SCENE_NAMES[SCENE.value]}")
            if KEYS.down[pg.K_c]:
                selected_obj:GameObject = get_global("<Selected_Object>").value
                if not selected_obj.engine_generated:
                    Raise_Error(main_window_manager, "Game Objects generated by code can't be copied")
                elif selected_obj is not None:
                    COPY = selected_obj
            if KEYS.down[pg.K_v]:
                if isinstance(COPY, GameObject):
                    parameters = copy(COPY.parameters)
                    parameters[3] = MOUSE.scene_position
                    new_game_object = create_Object_from_parameters(parameters, SCENE.value)
                    SELECTED_OBJ.value = new_game_object

    KEYS.any_down = np.any(KEYS.down) or np.any(MOUSE.down_buttons)

dt = 0 if SET_FPS == 0 else 1 / SET_FPS
fps_factor = 1
def tick_scene():
    global dt, fps_factor
    dt = min(dt, 1/(DELTA_FPS-2))
    if ALLOW_SPEED_UP:
        dt = 1/DELTA_FPS
    fps_factor=60*dt
    tick_game_objects(fps_factor, update=False) # no update for engine pre-view
    CAMERA.update(fps_factor)

def draw_all_windows():
    for wm in ALL_WINDOW_MANAGERS:
        if wm.manual_render:
            continue
        wm.renderer.clear()
        tick_main_UI_elements(wm)
        tick_UI_elements(wm.second_UI_elements)
        tick_scene()
        draw_main_UI_elements(wm)
        draw_UI_elements(wm.second_UI_elements)
        
        handle_top_action(wm)
        wm.renderer.present()

fps_update_frequency = 0.5
last_fps_time = time() - fps_update_frequency
last_time = perf_counter()
def handle_fps_count():
    global last_fps_time, last_time, dt
    dt = perf_counter() - last_time
    last_time = perf_counter()
    clock.tick(SET_FPS)
    if not SHOW_PERFORMANCE:
        return
    if time() - last_fps_time >= fps_update_frequency:
        last_fps_time = time()
        opened_project_name = "No project opened" if get_global("<Project_Opened>").value is None else get_global("<Project_Opened>").value
        if dt == 0:
            main_window.title = main_window_name.value + f" -- {opened_project_name} --" + f" 0ms | infinite FPS"
        else:
            main_window.title = main_window_name.value + f" -- {opened_project_name} --" + f" {dt*1000:.1f}ms | {1/dt:.1f} FPS"

print("SET FPS:", SET_FPS)
clock = pg.time.Clock()
while True:
    handle_events()
    handle_keymouse_input()
    handle_tick()
    draw_all_windows()
    handle_fps_count()
from assets import *
project_name = os.path.basename(project_root)

from value_assets import *
from imports import *
from UI import *
from CUUI import *
from objects import tick_game_objects, SCENES, SCENE_NAMES, SCENE
from joystick_manager import reset_axes_changes, handle_joystick_event, apply_joystick_changes, render_joysticks_input, joystick_managers

WINDOW_SIZE = MAIN_MONITOR_SIZE / 2
main_window, main_window_manager = create_window("Example Game -- beta", WINDOW_SIZE)
main_window_name = set_global("<main_window_name>", main_window.title)
set_global("main_window_manager", main_window_manager)

load_project(main_window_manager)

from main import tick

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

def handle_keymouse_input():
    KEYS.get_key_data()
    KEYS.update_extra_keys()
    MOUSE.get_data()
    if KEYS.down[pg.K_ESCAPE]:
        delete_top_window()
    if RUN_BY_ENGINE:
        if KEYS.down[pg.K_r]:
            reload_project_dependend_assets(main_window_manager)
        if KEYS.down[pg.K_s]:
            save_scene(SCENES[SCENE.value], f"Projects\\{get_global("<Project_Opened>").value}\\Scenes\\", SCENE_NAMES[SCENE.value])
            print(f"Saved {SCENE_NAMES[SCENE.value]}")
    KEYS.any_down = np.any(KEYS.down) or np.any(MOUSE.down_buttons)

dt = 0 if SET_FPS == 0 else 1 / SET_FPS
fps_factor = 1
def tick_scene():
    global dt, fps_factor
    dt = min(dt, 1/(DELTA_FPS-2))
    if ALLOW_SPEED_UP:
        dt = 1/DELTA_FPS
    fps_factor=60*dt
    tick_game_objects(fps_factor)
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
        if dt == 0:
            main_window.title = main_window_name.value + f" 0ms | infinite FPS"
        else:
            main_window.title = main_window_name.value + f" {dt*1000:.1f}ms | {1/dt:.1f} FPS"

print("SET FPS:", SET_FPS)
clock = pg.time.Clock()
while True:
    handle_events()
    handle_keymouse_input()
    tick()
    draw_all_windows()
    handle_fps_count()
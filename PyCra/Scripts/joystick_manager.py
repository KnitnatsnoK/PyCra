from value_assets import *
from window_manager import create_window, ALL_WINDOW_MANAGERS
from CUUI import create_Circle_Button, create_Rect_Button
from UI import tick_UI_elements, draw_UI_elements
from imports import bvec2

joystick_count = pg.joystick.get_count()
if JOYSTICK_MANAGER_DEBUG:
    print(f'Connected joysticks: {joystick_count}')

def list_hid_devices(print_ids=True):
    products = []
    for device in hid.enumerate():
        vendor_id = device['vendor_id']
        product_id = device['product_id']
        product_name = device['product_string']
        manufacturer_name = device['manufacturer_string']

        products.append((hex(vendor_id), hex(product_id), product_name, manufacturer_name))
        
        if print_ids:
            print(f"Vendor ID: {hex(vendor_id)}, Product ID: {hex(product_id)}")
            if manufacturer_name:
                print(f"Manufacturer: {manufacturer_name}")
            if product_name:
                print(f"Product: {product_name}")
            print("-" * 40)
    if print_ids:
        print("Products:", products)
    return products

if __name__ == "__main__":
    products = list_hid_devices(print_ids=False)

# Initialize all joysticks
class JoyStickManager:
    window_size = vec2(500, 300) # vec2(630, 300)
    button_pos_size = {"Nintendo Switch Joy-Con (R)": [vec3(vec2(145, 0), 15), vec3(vec2(120, 25), 15), vec3(vec2(120, -25), 15), vec3(vec2(95, 0), 15), None, vec3(vec2(-80, -20), 15), vec3(vec2(175, -40), 10), vec3(vec2(0), 30), None, vec4(-65, -65, 30, 8), vec4(110, -65, 30, 8), None, None, None, None, None, vec4(215, 0, 8, 40), None, vec4(230, 0, 10, 45)],
                       "Nintendo Switch Joy-Con (L)": [vec3(vec2(145, 0), 15), vec3(vec2(120, 25), 15), vec3(vec2(120, -25), 15), vec3(vec2(95, 0), 15), None, vec4(vec2(185, -30), 15, 15), vec4(vec2(-55, -20), 5, 15), vec3(vec2(0), 30), None, vec4(5, -65, 30, 8), vec4(160, -65, 30, 8), None, None, None, None, None, None, vec4(-85, 0, 8, 40), None, vec4(-100, 0, 10, 45)],
                        #"Xbox Series X Controller": [],
                        }
    button_type = {"Nintendo Switch Joy-Con (R)": [0, 0, 0, 0, None, 0, 0, 0, None, 1, 1, None, None, None, None, None, 1, None, 1],
                   "Nintendo Switch Joy-Con (L)": [0, 0, 0, 0, None, 1, 1, 0, None, 1, 1, None, None, None, None, None, None, 1, None, 1],
                    #"Xbox Series X Controller": [],
                    }
    joystick_counts = {
                    "Nintendo Switch Joy-Con (R)": 1,
                    "Nintendo Switch Joy-Con (L)": 1,
                    "Nintendo Switch Joy-Con (L/R)": 2,
                    "Nintendo Switch Pro Controller": 2,
                    "Xbox Series X Controller": 2,
                    "Xbox Wireless Controller": 2,  # Xbox One or generic Xbox
                    "Xbox 360 Wireless Receiver": 2,
                    "Sony DualShock 4": 2,
                    "Wireless Controller": 2,  # Bluetooth name for PS4/PS5 controllers on Windows
                    "Sony PS5 DualSense Wireless Controller": 2,
                    "Nintendo Wii U Pro Controller": 2,
                    "Logitech F310": 2,
                }

    def __init__(self, joystick_id:int):
        self.joystick = pg.joystick.Joystick(joystick_id)
        if JOYSTICK_WINDOW:
            _, self.window_manager = create_window(f"{self.joystick.get_name()} | ID {j}", JoyStickManager.window_size, manual_render=True)
        self.name = self.joystick.get_name()
        
        self.axes:vec2|vec4 = vec2(0) if self.name not in JoyStickManager.joystick_counts or JoyStickManager.joystick_counts[self.name] == 1 else vec4(0)
        self.axes_deltas:vec2|vec4 = copy(self.axes)
        self.inputs = [False for _ in range(self.joystick.get_numbuttons())]
        self.shoulder_buttons = vec2(0)
        self.numpad = vec2(0)

        self.GUID = self.joystick.get_guid()

        self.name_in_list = self.name in JoyStickManager.button_pos_size
        if not self.name_in_list or not JOYSTICK_WINDOW:
            return

        for i, delta_pos in enumerate(JoyStickManager.button_pos_size[self.name]):
            if not isinstance(delta_pos, vec2) and not isinstance(delta_pos, vec3) and not isinstance(delta_pos, vec4):
                self.window_manager.UI_elements.append(None)
                continue

            create_function_index = JoyStickManager.button_type[self.name][i]
            if create_function_index == 0:
                create_Circle_Button(self.window_manager, vec2(self.window_manager.window.size)/2 + delta_pos.xy, delta_pos.z, manual=True, user_creation=False)
            elif create_function_index == 1:
                create_Rect_Button(self.window_manager, vec2(self.window_manager.window.size)/2 + delta_pos.xy, delta_pos.zw, manual=True, user_creation=False)

        self.sum_changes = (vec4(0), vec4(0), vec2(0), vec2(0))

joystick_managers:list[JoyStickManager] = []
for j in range(joystick_count):
    joystick_manager = JoyStickManager(j)
    if JOYSTICK_MANAGER_DEBUG:
        print(f'Joystick {j}: {joystick_manager.name}')

    joystick_managers.append(joystick_manager)

if JOYSTICK_WINDOW:
    for i, jm in enumerate(joystick_managers):
        jm.window_manager.window.position = MAIN_MONITOR_SIZE/2 - JoyStickManager.window_size/2 + vec2(JoyStickManager.window_size.x*(-(joystick_count-1)/2 + i), 0)

def exists_controller(controller_id:int=0):
    return controller_id < len(joystick_managers)

def get_controller_button(controller_id:int=0, input_index:int=0):
    if not exists_controller(controller_id):
        return None
    return joystick_managers[controller_id].inputs[input_index]

def input_match_threshold(input: vec2, equals: bool = False, under: bool = False, over: bool = False, threshold: float = 0.0):
    x, y = input.x, input.y
    return bvec2(
        (not equals or x == threshold) and (not under or x < threshold) and (not over or x > threshold),
        (not equals or y == threshold) and (not under or y < threshold) and (not over or y > threshold)
    )

def get_controller_joystick(controller_id:int=0, joystick_index:int=0):
    if not exists_controller(controller_id):
        return None
    if joystick_index == 0:
        return joystick_managers[controller_id].axes.xy
    elif joystick_index == 1:
        return joystick_managers[controller_id].axes.wz

def controller_joystick_match_threshold(controller_id:int=0, joystick_index:int=0, equals:bool=False, under:bool=False, over:bool=False, threshold:float=0.0):
    joystick = get_controller_joystick(controller_id, joystick_index)
    return input_match_threshold(joystick, equals, under, over, threshold) if joystick is not None else bvec2(False, False)

def get_controller_shoulder_buttons(controller_id:int=0):
    if not exists_controller(controller_id):
        return None
    return joystick_managers[controller_id].shoulder_buttons

def controller_shoulder_buttons_match_threshold(controller_id:int=0, equals:bool=False, under:bool=False, over:bool=False, threshold:float=0.0):
    shoulder_buttons = get_controller_shoulder_buttons(controller_id)
    return input_match_threshold(shoulder_buttons, equals, under, over, threshold) if shoulder_buttons is not None else bvec2(False, False)

def get_controller_numpad(controller_id:int=0):
    if not exists_controller(controller_id):
        return None
    return joystick_managers[controller_id].numpad

def controller_numpad_match_threshold(controller_id:int=0, equals:bool=False, under:bool=False, over:bool=False, threshold:float=0.0):
    numpad = get_controller_numpad(controller_id)
    return input_match_threshold(numpad, equals, under, over, threshold) if numpad is not None else bvec2(False, False)

def get_controller_input(controller_id:int=0, input_type:int=BUTTONS, input_index:int=None):
    if controller_id >= len(joystick_managers):
        return None
    if input_type == BUTTONS:
        return joystick_managers[controller_id].inputs[input_index]
    elif input_type == JOYSTICK:
        return joystick_managers[controller_id].axes.xy
    elif input_type == JOYSTICK2:
        return joystick_managers[controller_id].axes.zw
    elif input_type == SHOULDER_BUTTONS:
        return joystick_managers[controller_id].shoulder_buttons
    elif input_type == NUMPAD:
        return joystick_managers[controller_id].numpad

def reset_axes_changes():
    for jm in joystick_managers:
        jm.sum_changes = (vec4(0), vec4(0), vec2(0), vec2(0))

def show_joystick_input(joy_stick_offset:vec2|vec4, joystick_manager:JoyStickManager, offset_len:float=25):
    window_manager = joystick_manager.window_manager
    renderer = window_manager.renderer
    window_size = vec2(window_manager.window.size)
    display = pg.Surface(window_size)
    display.set_colorkey(vec3(0))
    axes_deltas = joystick_manager.axes_deltas

    stick_size = 25
    border_size = 3

    if isinstance(joy_stick_offset, vec2):
        color = vec3(255) if axes_deltas.x or axes_deltas.y else vec3(100)
        center = window_size/2
        if not joystick_manager.name_in_list:
            pg.draw.circle(display, vec3(125), center, 30)
        pg.draw.circle(display, color-vec3(45), center+joy_stick_offset.xy * offset_len, stick_size)
        pg.draw.circle(display, color, center+joy_stick_offset.xy * offset_len, stick_size-border_size)
    elif isinstance(joy_stick_offset, vec4):
        color = vec3(255) if axes_deltas.x or axes_deltas.y else vec3(100)
        center = window_size/2 - vec2(stick_size + offset_len + 5, 0)
        if not joystick_manager.name_in_list:
            pg.draw.circle(display, vec3(125), center, 30)
        pg.draw.circle(display, color-vec3(45), center+joy_stick_offset.xy * offset_len, stick_size)
        pg.draw.circle(display, color, center+joy_stick_offset.xy * offset_len, stick_size-border_size)

        color = vec3(255) if axes_deltas.z or axes_deltas.w else vec3(100)
        center = window_size/2 + vec2(stick_size + offset_len + 5, 0)
        if not joystick_manager.name_in_list:
            pg.draw.circle(display, vec3(125), center, 30)
        pg.draw.circle(display, color-vec3(45), center+joy_stick_offset.zw * offset_len, stick_size)
        pg.draw.circle(display, color, center+joy_stick_offset.zw * offset_len, stick_size-border_size)

    renderer.blit(Texture.from_surface(renderer, display))

def handle_joystick_event(event):
    controller:int = event.joy
    sum_change = joystick_managers[controller].sum_changes
    if event.type == pg.JOYBUTTONDOWN:
        if JOYSTICK_MANAGER_DEBUG:
            print(f'Button {event.button} pressed down on {event.joy}')
        joystick_managers[controller].inputs[event.button] = True

        if joystick_managers[controller].name_in_list:
            joystick_managers[controller].window_manager.UI_elements[event.button].pressed.value = True
            joystick_managers[controller].window_manager.UI_elements[event.button].image_update_needed = True
    elif event.type == pg.JOYBUTTONUP:
        if JOYSTICK_MANAGER_DEBUG:
            print(f'Button {event.button} pressed up on {event.joy}')
        joystick_managers[controller].inputs[event.button] = False

        if joystick_managers[controller].name_in_list:
            joystick_managers[controller].window_manager.UI_elements[event.button].pressed.value = False
            joystick_managers[controller].window_manager.UI_elements[event.button].image_update_needed = True
    elif event.type == pg.JOYAXISMOTION:
        if JOYSTICK_MANAGER_DEBUG and False:
            print(f'Axis {event.axis} pressed with strength {event.value}')
        if event.axis == 0:
            sum_change[0].x += event.value
            sum_change[1].x += 1
        elif event.axis == 1:
            sum_change[0].y += event.value
            sum_change[1].y += 1
        elif event.axis == 2:
            sum_change[0].z += event.value
            sum_change[1].z += 1
        elif event.axis == 3:
            sum_change[0].w += event.value
            sum_change[1].w += 1
        elif event.axis == 4:
            sum_change[2].x += event.value
            sum_change[3].x += 1
        elif event.axis == 5:
            sum_change[2].y += event.value
            sum_change[3].y += 1
    elif event.type == pg.JOYHATMOTION:
        if JOYSTICK_MANAGER_DEBUG:
            print("Numpad", vec2(event.value))
        joystick_managers[controller].numpad = vec2(event.value)
    else:
        pass
        #print(event)

def apply_joystick_changes():
    for joystick_manager in joystick_managers:
        sum_change = joystick_manager.sum_changes

        if sum_change[1].x > 0:
            joystick_manager.axes.x = sum_change[0].x/sum_change[1].x
            joystick_manager.axes_deltas.x = int(abs(joystick_manager.axes.x) > 0.25)
        if sum_change[1].y > 0:
            joystick_manager.axes.y = sum_change[0].y/sum_change[1].y
            joystick_manager.axes_deltas.y = int(abs(joystick_manager.axes.y) > 0.25)

        if sum_change[1].z > 0 or sum_change[1].w > 0:
            if isinstance(joystick_manager.axes, vec2):
                joystick_manager.axes = vec4(joystick_manager.axes, 0, 0)
                joystick_manager.axes_deltas = vec4(joystick_manager.axes_deltas, 0, 0)

        if sum_change[1].z > 0:
            joystick_manager.axes.z = sum_change[0].z/sum_change[1].z
            joystick_manager.axes_deltas.z = int(abs(joystick_manager.axes.z) > 0.25)
        if sum_change[1].w > 0:
            joystick_manager.axes.w = sum_change[0].w/sum_change[1].w
            joystick_manager.axes_deltas.w = int(abs(joystick_manager.axes.w) > 0.25)
        
        if sum_change[3].x > 0:
            joystick_manager.shoulder_buttons.x = sum_change[2].x/sum_change[3].x
        if sum_change[3].y > 0:
            joystick_manager.shoulder_buttons.y = sum_change[2].y/sum_change[3].y
        if JOYSTICK_MANAGER_DEBUG and (sum_change[3].x > 0 or sum_change[3].y > 0):
            print("Shoulder Buttons:", joystick_manager.shoulder_buttons)

def render_joysticks_input():
    for joystick_manager in joystick_managers:
        if not joystick_manager.window_manager in ALL_WINDOW_MANAGERS:
            continue
        joystick_manager.window_manager.renderer.clear()

        tick_UI_elements(joystick_manager.window_manager.UI_elements)

        joystick_manager.window_manager.renderer.target = joystick_manager.window_manager.target_texture
        #tick_scene()
        joystick_manager.window_manager.renderer.target = None
        joystick_manager.window_manager.target_texture.draw(dstrect=(0, 0, *(joystick_manager.window_manager.window_size)))
        
        draw_UI_elements(joystick_manager.window_manager.UI_elements)
        show_joystick_input(joystick_manager.axes, joystick_manager)
        
        joystick_manager.window_manager.renderer.present()

"""
Custom User Interface
"""

from value_assets import *
from window_manager import Window_Manager
from imports import KEYS, MOUSE, draw_circle, draw_rect, draw_rect_outline, draw_anti_circle, draw_anti_rect, center, create_surface
from UI import UI_Element, Pop_up

class Circle_Button(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, radius:int, manual:bool=False, pressed:bool=False):
        super().__init__(window_manager, pos, vec2(radius*2), None)
        self.action = None if manual else 0
        self.radius = radius
        self.pressed = Variable(pressed)
        set_UI_global(CIRCLE_BUTTON, self.id, self.pressed)
        self.pos -= radius

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = create_surface(self.size)
        surf.set_colorkey(vec3(0))
        if self.pressed.value:
            draw_circle(surf, vec3(255), vec2(self.radius), self.radius, anti_aliasing=True)
        else:
            draw_circle(surf, vec3(125), vec2(self.radius), self.radius, anti_aliasing=True)

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        if MOUSE.down_buttons[0]:
            if distance(self.pos + self.radius, MOUSE.position) <= self.radius:
                if not type(self.window_manager.last_action_element) == Pop_up:
                    self.window_manager.last_action_element = self
        
    def handle_action(self):
        self.pressed.value = not self.pressed.value
        self.image_update_needed = True

set_global("<Selected_Object>", None)
class Rect_Outline(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, size:vec2, color:vec3=vec3(0, 0, 0), alpha:int=255, width:int=1, action:int=None, **kwargs):
        super().__init__(window_manager, pos, size, action)
        
        self.pos = center(self.pos, self.size, **kwargs)
        
        self.color = color
        self.alpha = alpha
        self.width = width
        self.render = False

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = create_surface(self.size, flags=(0 if self.alpha == 255 else pg.SRCALPHA))
        surf.set_colorkey(vec3(0))

        draw_rect_outline(surf, vec2(0), self.size, self.color, self.alpha, self.width)

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        selected_obj = get_global("<Selected_Object>").value
        self.render = selected_obj is not None
        if self.render:
            if self.size != selected_obj.size + vec2(4):
                self.image_update_needed = True
                self.size = selected_obj.size + vec2(4)
            self.pos = center(selected_obj.get_window_pos()+selected_obj.size/2, self.size, **{"center":True})

class Rect_Button(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, size:vec2, manual:bool=False, pressed:bool=False):
        super().__init__(window_manager, pos, size, None)
        self.action = None if manual else 0
        self.pressed = Variable(pressed)
        set_UI_global(RECT_BUTTON, self.id, self.pressed)
        if manual:
            if self.size.x > self.size.y:
                self.pos -= vec2(size.x/2, size.y)
            else:
                self.pos -= vec2(size.x, size.y/2)

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = create_surface(self.size)

        if self.pressed.value:
            draw_rect(surf, vec2(0), self.size, vec3(255))
        else:
            draw_rect(surf, vec2(0), self.size, vec3(125))

        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)
        
    def handle_action(self):
        self.pressed.value = not self.pressed.value
        self.image_update_needed = True

class Anti_Circle(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, radius:int, color:vec3=vec3(0, 0, 0), alpha:int=0, circle_alpha:int=255):
        super().__init__(window_manager, vec2(0), vec2(window_manager.window.size), None)
        self.anti = True
        self.anti_radius = radius
        self.anti_pos = pos

        self.color = color
        self.alpha = alpha
        self.circle_alpha = circle_alpha

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = draw_anti_circle(self.window_manager, self.anti_pos, self.anti_radius, self.color, self.alpha, self.circle_alpha)
        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        pass
        
    def handle_action(self):
        pass

class Anti_Rect(UI_Element):
    def __init__(self, window_manager:Window_Manager, pos:vec2|None, size:vec2, color:vec3=vec3(0, 0, 0), alpha:int=0, rect_alpha:int=255, **kwargs):
        super().__init__(window_manager, vec2(0), vec2(window_manager.window.size), None)
        self.anti = True
        self.anti_size = size
        self.anti_pos = pos
        self.anti_pos = center(self.anti_pos, self.anti_size, **kwargs)

        self.color = color
        self.alpha = alpha
        self.rect_alpha = rect_alpha

        # image
        self.image_update_needed = False
        self.update_image()

    def update_image(self):
        surf = draw_anti_rect(self.window_manager, self.anti_pos, self.anti_size, self.color, self.alpha, self.rect_alpha)
        self.image:Texture|Image = Texture.from_surface(self.window_manager.renderer, surf)

    def check_for_action(self):
        pass
        
    def handle_action(self):
        pass

def create_Circle_Button(window_m:Window_Manager, pos:vec2|None, radius:int, manual:bool=False, pressed:bool=False):
    circle_button = Circle_Button(window_m, pos, radius, manual, pressed)
    window_m.UI_elements.append(circle_button)
    return circle_button

def create_Rect_Outline(window_m:Window_Manager, pos:vec2|None, size:vec2, color:vec3=vec3(0, 0, 0), alpha:int=255, width:int=1, action:int=None, **kwargs):
    rect_outline = Rect_Outline(window_m, pos, size, color, alpha, width, action, **kwargs)
    window_m.UI_elements.append(rect_outline)
    return rect_outline

def create_Rect_Button(window_m:Window_Manager, pos:vec2|None, size:vec2):
    rect_button = Rect_Button(window_m, pos, size)
    window_m.UI_elements.append(rect_button)
    return rect_button

def create_Anti_Circle(window_m:Window_Manager, pos:vec2|None, radius:int, color:vec3=vec3(0, 0, 0), alpha:int=0, circle_alpha:int=255):
    circle_button = Anti_Circle(window_m, pos, radius, color, alpha, circle_alpha)
    window_m.UI_elements.append(circle_button)
    return circle_button

def create_Anti_Rect(window_m:Window_Manager, pos:vec2|None, size:vec2, color:vec3=vec3(0, 0, 0), alpha:int=0, rect_alpha:int=255, **kwargs):
    rect_button = Anti_Rect(window_m, pos, size, color, alpha, rect_alpha, **kwargs)
    window_m.UI_elements.append(rect_button)
    return rect_button
"""
Includes caches (mostly for rendering) and assets.py
"""

from assets import *
from global_variables import set_global

new_surface_cache:dict[tuple[vec2, vec4, int], pg.Surface] = {}
def create_surface(size:vec2, color:vec4=(0, 0, 0, 255), flags:int=0):
    if (size, color, flags) in new_surface_cache:
        return copy(new_surface_cache[size, color, flags])
    
    surf = pg.Surface(size=size, flags=flags)
    surf.fill(color)
    new_surface_cache[size, color, flags] = surf
    return copy(surf)

image_cache:dict[tuple[str, vec2|None], pg.Surface] = {}
def load_image(image_path:str, preferred_size:vec2|None=None):
    if (image_path, preferred_size) in image_cache:
        return copy(image_cache[(image_path, preferred_size)])
    
    image = pg.image.load(image_path)
    if preferred_size is not None:
        if preferred_size.x < image.size[0] or preferred_size.y < image.size[1]:
            image = pg.transform.smoothscale(image, preferred_size)
    image_cache[(image_path, preferred_size)] = image
    return copy(image)

# placeholder cache
placeholder_cache:dict[tuple, set] = {}
set_global("<(cache) PLACEHOLDER_CACHE>", placeholder_cache)
def get_placeholder_status(UI_type, open_project:str, input:tuple):
    return (open_project in placeholder_cache) and ((UI_type, input) in placeholder_cache[open_project])

def set_placeholder(UI_type, open_project:str, input:tuple):
    if not open_project in placeholder_cache:
        placeholder_cache[open_project] = set()
    placeholder_cache[open_project].add((UI_type, input))

# takes in the UI_type and several properties of an UI-Element to save it to a cache
UI_tex_cache:dict[tuple[int, tuple], Texture] = {}
def cached_UI_tex_load(renderer:Renderer, surf:pg.Surface, UI_type, input:tuple, new_texture=False) -> Texture:
    if (UI_type, input) in UI_tex_cache and not new_texture:
        return UI_tex_cache[(UI_type, input)]
    
    UI_tex_cache[(UI_type, input)] = Texture.from_surface(renderer, surf)
    return UI_tex_cache[(UI_type, input)]

# takes in the UI_type and several properties of an UI-Element to return a Texture if its in the cache, else False
def try_UI_tex_cache(UI_type, input:tuple) -> Texture:
    if (UI_type, input) in UI_tex_cache:
        return UI_tex_cache[(UI_type, input)]
    return False

texture_cache:dict[tuple, Texture] = {}
def cached_texture_load(renderer:Renderer, surf:pg.Surface, key:tuple, new_texture=False) -> Texture:
    if key in texture_cache and not new_texture:
        return texture_cache[key]
    
    texture_cache[key] = Texture.from_surface(renderer, surf)
    return texture_cache[key]

def try_texture_cache(key:tuple) -> Texture:
    if key in texture_cache:
        return texture_cache[key]
    return False

# class decoder
decoder_cache:dict[tuple[str, str], type] = {}
def decode_class(class_name:str, module:str) -> type:
    if (class_name, module) in decoder_cache:
        return decoder_cache[(class_name, module)]
    
    class_type = getattr(__import__(module, fromlist=[class_name]), class_name)
    decoder_cache[(class_name, module)] = class_type
    return class_type

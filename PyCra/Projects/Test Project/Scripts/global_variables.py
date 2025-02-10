"""
Includes global variable management
"""

class Variable:
    def __init__(self, value):
        self.value = value

GLOBALS:dict[str, Variable] = {}

def set_global(key:str, value):
    if key in GLOBALS:
        GLOBALS[key].value = value.value if type(value) == Variable else value
    else:
        GLOBALS[key] = value if type(value) == Variable else Variable(value)
    return GLOBALS[key]

def get_global(key:str) -> Variable:
    if key not in GLOBALS:
        return None #Variable(None)
    return GLOBALS[key]

def delete_global(key:str) -> Variable:
    if key not in GLOBALS:
        return None
    return GLOBALS.pop(key)

def set_UI_global(UI_type:str, id:int, value):
    set_global(f"<{UI_type} at {id}>", value)

def get_UI_global(UI_type:str, id:int) -> Variable:
    return get_global(f"<{UI_type} at {id}>")
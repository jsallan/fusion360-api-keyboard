from . import class_defs

def keyhole_factory(component, key, x, y, z):
    new_key = class_defs.Keyhole(component, f"row{key}", x, y, z,)
    new_key.create_keyhole()
    return new_key
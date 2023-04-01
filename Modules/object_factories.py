from . import class_defs

def keyhole_factory(component, key, x, y, z, rot):
    new_key = class_defs.Keyhole(component, f"row{key}", x, y, z, rot)
    new_key.create_keyhole()
    return new_key

def box_factory(component, name, height, width, depth, rot, x_center=0.0, y_center=0.0, z_center=0.0):
    new_box = class_defs.Box(component, height, width, depth, name, rotation=rot, x_center=x_center, y_center=y_center, z_center=z_center)
    new_box.create()
    return new_box

def matrix_factory(parent_comp, name):
    new_matrix = class_defs.Matrix(parent_comp, name)
    new_matrix.create()
    return new_matrix

def thumbs_factory(parent_comp, name, col, place_func):
    new_thumbs = class_defs.Thumbs(parent_comp, name, col=0, placement_function=place_func)
    new_thumbs.create()
    return new_thumbs

def elec_cutter_factory(parent_comp, name, cutter_dims, rot, start_tl=[0, 0, 0]):
    new_mcu_cutter = class_defs.Electronics_cutter(parent_comp, name, cutter_dims, rot=rot, start_tl=start_tl)
    new_mcu_cutter.create()
    return new_mcu_cutter
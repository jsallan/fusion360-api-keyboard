import adsk.core, adsk.fusion, adsk.cam, traceback
from . import config
import math

mm = 0.1

def minidox_thumbs(col):
    alpha = math.degrees(math.asin((config.minidox_key_space / 2) / config.minidox_radius))
    key_locs = {}
    key_rots = list()
    for key in range(config.minidox_num_thumb_keys):
        key_locs[key] = {
            "x" : (config.minidox_radius * math.cos(math.radians(2 * alpha * key + config.minidox_key1_angle)) + config.minidox_over), 
            "y" : (config.minidox_radius * math.sin(math.radians(2 * alpha * key + config.minidox_key1_angle)) + config.minidox_up),
            "z" : 0
            }
        key_rots.append(2 * alpha * key + config.minidox_key1_angle)
    return key_locs, key_rots


def place_matrix_keys(col):
    key_locs = {}
    key_rots = list()
    x_key_spacing = config.keyhole_width + config.keyhole_rim_width*2 + config.col_space
    y_key_center_offset = config.keyhole_height + config.keyhole_rim_width*2 + config.key_vert_space
    y_col_stagger = config.col_stagger
    for key in range(config.num_rows):
            key_locs[key] = {
                "x" : col * x_key_spacing, 
                "y" : key * y_key_center_offset + y_col_stagger[col],
                "z" : 0
                }
            key_rots.append(0)

    return key_locs, key_rots


def rotate_component(parent_comp, thing, rot_angle, rot_axis: list):
    rotation_axis = adsk.core.Vector3D.create(rot_axis[0], rot_axis[1], rot_axis[2])
    comp = parent_comp.occurrences.itemByName(f"{thing.component.name}:1")
    comp_transform = comp.transform
    rotation_matrix = adsk.core.Matrix3D.create()
    rotation_matrix.setToRotation(math.radians(rot_angle), rotation_axis, adsk.core.Point3D.create(1,2,3))
    comp_transform.transformBy(rotation_matrix)
    comp.transform = comp_transform
    update_corners(thing, rotate=[rot_axis[i]*rot_angle for i in range(len(rot_axis))])

def move_component(parent_comp, thing, translate: list):
    comp = parent_comp.occurrences.itemByName(f"{thing.name}:1")
    new_position = adsk.core.Vector3D.create(translate[0], translate[1], translate[2])  
    comp_transform = comp.transform
    comp_transform.translation = new_position
    comp.transform = comp_transform
    update_corners(thing, translate=translate)

def update_corners(thing, translate: list=[0,0,0], rotate: list=[0,0,0]):
    '''Updates the corners attribute of thing object given a translation and rotation.'''
    update_functions = [rotate_point, translate_point]
    corner_rot_trans = [rotate, translate]
    for index1, update_function in enumerate(update_functions):
        for corner, point in thing.corners.items():
            new_point = update_function(point, corner_rot_trans[index1])
            for index2 in range(len(point)):
                point[index2] = new_point[index2]
            thing.corners[corner] = point


def translate_point(point:list, translate:list) -> list:
    return [point[i]+translate[i] for i in range(len(point))]


def rotate_point(point:list, rotation:list) -> list:
    """
    Rotates a point `[x, y, z]` around the x-axis, y-axis, and z-axis by the angles `a`, `b`, and `c` respectively.
    """
    # Convert angles to radians
    alpha, beta, gamma = [math.radians(rotation[i]) for i in range(3)]
    
    # Calculate the rotation matrix for rotation around x-axis
    Rx = [[1, 0, 0],
          [0, math.cos(alpha), -math.sin(alpha)],
          [0, math.sin(alpha), math.cos(alpha)]]
    
    # Calculate the rotation matrix for rotation around y-axis
    Ry = [[math.cos(beta), 0, math.sin(beta)],
          [0, 1, 0],
          [-math.sin(beta), 0, math.cos(beta)]]
    
    # Calculate the rotation matrix for rotation around z-axis
    Rz = [[math.cos(gamma), -math.sin(gamma), 0],
          [math.sin(gamma), math.cos(gamma), 0],
          [0, 0, 1]]
    
    rotated_point = point.copy()
    
    # Apply rotations sequentially
    rotated_point = [sum([Rx[i][j]*rotated_point[j] for j in range(3)]) for i in range(3)]  # Rotate around x-axis
    rotated_point = [sum([Ry[i][j]*rotated_point[j] for j in range(3)]) for i in range(3)]  # Rotate around y-axis
    rotated_point = [sum([Rz[i][j]*rotated_point[j] for j in range(3)]) for i in range(3)]  # Rotate around z-axis

    return rotated_point


def create_component(parent_comp, name):
    component = parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    component.name = name
    return component

def copy_component(parent_comp, source_comp, x=0, y=0, z=0):
    # if x or y or z is not 0:
    vector = adsk.core.Vector3D.create(x*mm, y*mm, z*mm)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector
        # self.component.component.occurrences.addExistingComponent(argh.component.component, transform)

    return parent_comp.occurrences.addNewComponentCopy(source_comp, transform).component

def new_comp_occ(parent_comp, source_comp, x=0, y=0, z=0):
    # if x or y or z is not 0:
    vector = adsk.core.Vector3D.create(x*mm, y*mm, z*mm)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector
        # self.component.component.occurrences.addExistingComponent(argh.component.component, transform)

    return parent_comp.occurrences.addExistingComponent(source_comp, transform).component

def move_body(component, target, x, y, z):
    features = component.features
    # Create a collection of entities for move
    body = adsk.core.ObjectCollection.create()
    body.add(target)

    # Create a transform to do move
    vector = adsk.core.Vector3D.create(x*mm, y*mm, z*mm)
    transform = adsk.core.Matrix3D.create()
    transform.translation = vector

    # Create a move feature
    moveFeats = features.moveFeatures
    moveFeatureInput = moveFeats.createInput(body, transform)
    moveFeats.add(moveFeatureInput)


def cut_body(component, target, tool, keep_tool=False):
    features = component.features
    target_body = target.body
    tool_bodies = adsk.core.ObjectCollection.create()
    tool_bodies.add(tool.body)

    CombineCutInput = component.features.combineFeatures.createInput(target_body, tool_bodies)
         
    CombineCutFeats = features.combineFeatures
    CombineCutInput = CombineCutFeats.createInput(target_body, tool_bodies)
    CombineCutInput.isKeepToolBodies = keep_tool
    CombineCutInput.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
    CombineCutFeats.add(CombineCutInput)

def angle_between_lines(line1, line2):
    # α = arccos[(xa · xb + ya · yb + za · zb) / (√(xa² + ya² + za²) · √(xb² + yb² + zb²))]
    l1_start, l1_end = get_coords_from_line(line1)
    l2_start, l2_end = get_coords_from_line(line2)
    xa = l1_end["x"]-l1_start["x"]
    ya = l1_end["y"]-l1_start["y"]
    za = l1_end["z"]-l1_start["z"]
    xb = l2_end["x"]-l2_start["x"]
    yb = l2_end["y"]-l2_start["y"]
    zb = l2_end["z"]-l2_start["z"]
    
    # A = (xa · xb + ya · yb + za · zb)
    A = (xa * xb + ya * yb + za * zb)
    
    # B = √(xa² + ya² + za²)
    # C = √(xb² + yb² + zb²)
    B = math.sqrt(xa*xa + ya*ya + za*za)
    C = math.sqrt(xb*xb + yb*yb + zb*zb)
    
    # arccos[A/(B*C)]
    return math.degrees(math.acos(A/(B*C)))

def get_coords_from_line(line):
    return {
        "x":line.startSketchPoint.geometry.x, 
        "y":line.startSketchPoint.geometry.y, 
        "z":line.startSketchPoint.geometry.z
        }, {
        "x":line.endSketchPoint.geometry.x, 
        "y":line.endSketchPoint.geometry.y,
        "z":line.endSketchPoint.geometry.z
        }

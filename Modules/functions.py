import adsk.core, adsk.fusion, adsk.cam, traceback
import math

mm = 0.1

def minidox_thumbs(num_keys, over, up, radius, key_space, key1_angle):
    alpha = math.asin((key_space / 2) / radius)
    key_locs = {}
    for key in range(num_keys):
        key_locs[f"key{key}"] = {
            "x" : (radius * math.sin(2 * alpha * key + key1_angle) + over) * mm, 
            "y" : (radius * math.cos(2 * alpha * key + key1_angle) + up) * mm
            }
    return key_locs


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

import adsk.core, adsk.fusion, adsk.cam, traceback

mm = 0.1

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

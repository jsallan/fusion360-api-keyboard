import adsk.core, adsk.fusion, adsk.cam, traceback
from . import config, functions

mm = 0.1

class Component:
    def __init__(self, parent_comp, name):
        self.parent_comp = parent_comp
        self.name = name

    def create_component(self):
        # if self.parent_comp.isRootComponent:
        self.component = self.parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        self.component.name = self.name


class Box:
    def __init__(self, parent_comp, height, width, depth, name, sketch_plane="xy"):
        self.parent_comp = parent_comp
        self.sketch_plane = self.get_sketch_plane(sketch_plane)
        self.height = height * mm
        self.width = width * mm
        self.depth = depth * mm
        self.name = name

    def get_sketch_plane(self, sketch_plane):
        if sketch_plane == "xy":
            return self.parent_comp.xYConstructionPlane
        if sketch_plane == "yz":
            return self.parent_comp.yZConstructionPlane
        if sketch_plane == "xz":
            return self.parent_comp.xZConstructionPlane
    
    def create(self):
        self.create_sketch()
        self.create_body()

    def create_sketch(self):
        self.sketch = self.parent_comp.sketches.add( self.sketch_plane )
        
        pa = adsk.core.Point3D.create( -(self.width/2), -(self.height/2), 0 )
        pb = adsk.core.Point3D.create( (self.width/2), -(self.height/2), 0 )
        pc = adsk.core.Point3D.create( (self.width/2), (self.height/2), 0 )
        pd = adsk.core.Point3D.create( -(self.width/2), (self.height/2), 0 )

        #-- Create Edges
        la = self.sketch.sketchCurves.sketchLines.addByTwoPoints( pa, pb )
        lb = self.sketch.sketchCurves.sketchLines.addByTwoPoints( pb, pc )
        lc = self.sketch.sketchCurves.sketchLines.addByTwoPoints( pc, pd )
        ld = self.sketch.sketchCurves.sketchLines.addByTwoPoints( pd, pa )

    def create_body(self):
        features = self.parent_comp.features
        extrudes = features.extrudeFeatures
        extrude_input = extrudes.createInput(self.sketch.profiles[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        extrude_input.setDistanceExtent( False, adsk.core.ValueInput.createByReal( self.depth ) )

        self.extruded_feature = extrudes.add(extrude_input)
        self.body = self.extruded_feature.bodies.item(0)
        self.body.name = self.name
    
    def rename_body(self, new_name):
        self.body.name = new_name
        

class Keyhole():
    def __init__(self, parent_comp, name):
        self.name = name
        self.parent_comp = parent_comp

    def create_component(self):
        self.component = Component(self.parent_comp, self.name)
        self.component.create_component()

    def create_keyhole(self):
        self.create_component()
        
        inside_cut = Box(
            self.component.component, 
            config.keyhole_width, 
            config.keyhole_height, 
            config.keyhole_depth, 
            "inside_cut"
            )
        
        self.keyhole = Box(
            self.component.component, 
            config.keyhole_width + config.keyhole_rim_width*2, 
            config.keyhole_height + config.keyhole_rim_width*2, 
            config.keyhole_depth, 
            "keyhole"
            )
        inside_cut.create()
        self.keyhole.create()

        functions.cut_body(self.component.component, self.keyhole, inside_cut, keep_tool=False)

        keyclip_cut = Box(
            self.component.component, 
            config.keyhole_width + 2*config.key_notch_depth, 
            config.key_notch_width, 
            config.key_notch_height, 
            "keyclip_cut"
            )
        
        keyclip_cut.create()

        functions.cut_body(self.component.component, self.keyhole, keyclip_cut, keep_tool=False)

        self.body = self.keyhole.body


class Column():
    def __init__(self, parent_comp, num_keys, name):
        self.parent_comp = parent_comp
        self.num_keys = num_keys
        self.name = name
        self.keys = []
        self.move_vector = {
            'x': 0, 
            'y': config.keyhole_height + config.keyhole_rim_width*2 + config.key_vert_space, 
            'z':0
            }

    def create(self):
        self.component = Component(self.parent_comp, self.name)
        self.component.create_component()



        # len(new_key.keyhole.sketch.sketchCurves.sketchLines)
        # new_key.keyhole.sketch.sketchCurves.sketchLines.item(3).geometry.startPoint.x

        for key in range(self.num_keys):
            new_key = Keyhole(self.component.component, f"row{key}")
            new_key.create_keyhole()
            self.keys.append(new_key)

            # if key == 0:
            #     new_key = Keyhole(self.component.component, f"row{key}")
            #     new_key.create_keyhole()
            #     self.keys.append(new_key)

            # if key > 0:
                # self.keys.append(functions.new_comp_occ(
                #     self.component.component, 
                #     self.keys[0].component.component, 
                #     self.move_vector["x"] * (key), 
                #     self.move_vector["y"] * (key), 
                #     self.move_vector["z"] * (key)
                #     ))

            # functions.move_component(self.keys[key].component.component, self.move_vector["x"] * key, self.move_vector["y"] * key, self.move_vector["z"] * key)
            if key > 0:
                functions.move_body(
                    self.keys[key].component.component, 
                    self.keys[key].body, 
                    self.move_vector["x"] * key, 
                    self.move_vector["y"] * key, 
                    self.move_vector["z"] * key
                    )

class Matrix():
    def __init__(self, parent_comp, name):
        self.parent_comp = parent_comp
        self.num_cols = config.num_cols
        self.cols = []
        self.name = name
        self.move_vector = {
            'x': config.keyhole_width + config.keyhole_rim_width*2 + config.col_space, 
            'y': 0, 
            'z':0
            }

    def create_component(self):
        self.component = Component(self.parent_comp, self.name)
        self.component.create_component()

    def create(self):
        self.create_component()
        for col in range(self.num_cols):
        #     new_col = Column(self.component.component, config.num_rows, f"col{col}")
        #     new_col.create()
        #     self.cols.append(new_col)

            if col == 0:
                new_col = Column(self.component.component, config.num_rows, f"col{col}")
                new_col.create()
                self.cols.append(new_col)

            if col > 0:
                self.cols.append(functions.copy_component(
                    self.component.component, 
                    self.cols[0].component.component, 
                    self.move_vector["x"] * (col), 
                    self.move_vector["y"] * (col), 
                    self.move_vector["z"] * (col)
                    ))
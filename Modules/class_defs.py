import adsk.core, adsk.fusion, adsk.cam, traceback, math
from . import config, functions, object_factories

mm = 0.1

# class Component:
#     def __init__(self, parent_comp, name):
#         self.parent_comp = parent_comp
#         self.name = name

#     def create_component(self):
#         # if self.parent_comp.isRootComponent:
#         self.component = self.parent_comp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
#         self.component.name = self.name


class Box:
    def __init__(self, parent_comp, height, width, depth, name, sketch_plane="xy", x_center=0.0, y_center=0.0, z_center=0.0, rotation=0):
        self.parent_comp = parent_comp
        self.sketch_plane = self.get_sketch_plane(sketch_plane)
        self.height = height * mm
        self.width = width * mm
        self.depth = depth * mm
        self.name = name
        self.x_center = x_center * mm
        self.y_center = y_center * mm
        self.z_center = z_center * mm
        self.rotation = rotation
        self.corners = self.create_corners()
        self.sketch = None
        self.body = None
        self.extruded_feature = None

    def create_corners(self):
        # (x, y, z)
        hypoteneus = math.sqrt(math.pow((self.width/2), 2) + math.pow((self.height/2), 2))
        theta = math.degrees(math.atan((self.height/2)/(self.width/2)))
        # self.tl = {
        #     "x" : (-(self.width/2)) * math.cos(math.radians(45+self.rotation)) + self.x_center, 
        #     "y" : ((self.height/2)) * math.sin(math.radians(45+self.rotation)) + self.y_center, 
        #     "z" : self.z_center
        #     }
        # self.tr = {
        #     "x" : ((self.width/2)) * math.cos(math.radians(45+self.rotation)) + self.x_center, 
        #     "y" : ((self.height/2)) * math.sin(math.radians(45+self.rotation)) + self.y_center, 
        #     "z" : self.z_center
        #     }
        # self.bl = {
        #     "x" : (-(self.width/2)) * math.cos(math.radians(45+self.rotation)) + self.x_center, 
        #     "y" : (-(self.height/2)) * math.sin(math.radians(45+self.rotation)) + self.y_center, 
        #     "z" : self.z_center
        #     }
        # self.br = {
        #     "x" : ((self.width/2)) * math.cos(math.radians(45+self.rotation)) + self.x_center, 
        #     "y" : (-(self.height/2)) * math.sin(math.radians(45+self.rotation)) + self.y_center, 
        #     "z" : self.z_center
        #     }
        self.tl = {
            "x" : (hypoteneus) * math.cos(math.radians(180-theta+self.rotation)) + self.x_center, 
            "y" : (hypoteneus) * math.sin(math.radians(180-theta+self.rotation)) + self.y_center, 
            "z" : self.z_center
            }
        self.tr = {
            "x" : (hypoteneus) * math.cos(math.radians(theta+self.rotation)) + self.x_center, 
            "y" : (hypoteneus) * math.sin(math.radians(theta+self.rotation)) + self.y_center, 
            "z" : self.z_center
            }
        self.bl = {
            "x" : (hypoteneus) * math.cos(math.radians(180+theta+self.rotation)) + self.x_center, 
            "y" : (hypoteneus) * math.sin(math.radians(180+theta+self.rotation)) + self.y_center, 
            "z" : self.z_center
            }
        self.br = {
            "x" : (hypoteneus) * math.cos(math.radians(360-theta+self.rotation)) + self.x_center, 
            "y" : (hypoteneus) * math.sin(math.radians(360-theta+self.rotation)) + self.y_center, 
            "z" : self.z_center
            }
        return {"tl" : self.tl, "tr" : self.tr, "bl" : self.bl, "br" : self.br}

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
        
        bl = adsk.core.Point3D.create( **self.bl )
        br = adsk.core.Point3D.create( **self.br )
        tr = adsk.core.Point3D.create( **self.tr )
        tl = adsk.core.Point3D.create( **self.tl )

        #-- Create Edges
        la = self.sketch.sketchCurves.sketchLines.addByTwoPoints( bl, br )
        lb = self.sketch.sketchCurves.sketchLines.addByTwoPoints( br, tr )
        lc = self.sketch.sketchCurves.sketchLines.addByTwoPoints( tr, tl )
        ld = self.sketch.sketchCurves.sketchLines.addByTwoPoints( tl, bl )

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
    def __init__(self, parent_comp, name, x_center=0, y_center=0, z_center=0, key_rotation=0):
        self.name = name
        self.parent_comp = parent_comp
        self.x_center = x_center
        self.y_center = y_center
        self.z_center = z_center
        self.component = None
        self.keyhole = None
        self.body = None
        self.corners = {}
        self.key_rotation = key_rotation # degrees

    def create_component(self):
        self.component = functions.create_component(self.parent_comp, self.name)
        # self.component = Component(self.parent_comp, self.name)
        # self.component.create_component()

    def create_keyhole(self):
        self.create_component()
        
        inside_cut = Box(
            self.component, 
            config.keyhole_width, 
            config.keyhole_height, 
            config.keyhole_depth, 
            "inside_cut",
            x_center=self.x_center,
            y_center=self.y_center,
            z_center=self.z_center,
            rotation = self.key_rotation
            )
        
        self.keyhole = Box(
            self.component, 
            config.keyhole_width + config.keyhole_rim_width*2, 
            config.keyhole_height + config.keyhole_rim_width*2, 
            config.keyhole_depth, 
            "keyhole",
            x_center=self.x_center,
            y_center=self.y_center,
            z_center=self.z_center, 
            rotation = self.key_rotation
            )
        inside_cut.create()
        self.keyhole.create()

        functions.cut_body(self.component, self.keyhole, inside_cut, keep_tool=False)

        keyclip_cut = Box(
            self.component, 
            config.keyhole_width + 2*config.key_notch_depth, 
            config.key_notch_width, 
            config.key_notch_height, 
            "keyclip_cut",
            x_center=self.x_center,
            y_center=self.y_center,
            z_center=self.z_center, 
            rotation = self.key_rotation
            )
        
        keyclip_cut.create()

        functions.cut_body(self.component, self.keyhole, keyclip_cut, keep_tool=False)

        self.body = self.keyhole.body
        self.corners = self.keyhole.corners

    def get_corner_coords(self, corner):
        return self.corners[corner]


class Column():
    def __init__(self, parent_comp, name, col, placement_function):
        self.parent_comp = parent_comp
        self.num_keys = config.num_rows
        self.name = name
        self.col = col
        self.keys = []
        self.component = None
        self.corners = {}
        self.key_center_locs, self.key_rots = placement_function(self.col)

    def create(self):
        self.component = functions.create_component(self.parent_comp, self.name)

        for key in range(self.num_keys):
            new_key = object_factories.keyhole_factory(
                self.component, 
                f"row{key}", 
                self.key_center_locs[key]["x"], 
                self.key_center_locs[key]["y"], 
                self.key_center_locs[key]["z"],
                self.key_rots[key]
                )
            self.keys.append(new_key)
            if key == 0:
                self.corners["bl"] = new_key.corners["bl"]
                self.corners["br"] = new_key.corners["br"]

            if key == self.num_keys-1:
                self.corners["tl"] = new_key.corners["tl"]
                self.corners["tr"] = new_key.corners["tr"]


class Matrix():
    def __init__(self, parent_comp, name):
        self.parent_comp = parent_comp
        self.num_cols = config.num_cols
        self.cols = []
        self.name = name
        self.corners = {}

    def create_component(self):
        self.component = functions.create_component(self.parent_comp, self.name)

    def create(self):
        self.create_component()
        for col in range(self.num_cols):

            new_col = Column(
                self.component, 
                f"col{col}",
                col,
                functions.place_matrix_keys,
                )
            new_col.create()
            self.cols.append(new_col)
            self.get_corners()
    
    def get_corners(self):
        self.corners = {
            "tl" : self.cols[0].corners["tl"], 
            "tr" : self.cols[-1].corners["tr"],
            "bl" : self.cols[0].corners["bl"],
            "bl" : self.cols[-1].corners["br"]
        }



class Keyboard():
    def __init__(self, parent_comp, name, thumb_placement):
        self.parent_comp = parent_comp
        self.name = name
        self.component = functions.create_component(self.parent_comp, "keyboard")
        self.key_matrix = object_factories.matrix_factory(self.component, "matrix")
        self.thumbs = object_factories.thumbs_factory(self.component, "thumbs", 0, thumb_placement)
        mcu_cutter_dims = dict(
            cut_width = config.MCU_cut_width,
            cut_height = config.MCU_cut_height,
            cut_extrude = config.MCU_cut_extrude,
            PCB_thickness = config.MCU_PCB_thickness,
            lip = config.MCU_lip,
            tl_margin = config.MCU_tl_margin,
            USB_width = config.MCU_USB_width,
            USB_height = config.MCU_USB_height,
            USB_extrude = config.MCU_USB_extrude,
            USB_zoffset = config.MCU_USB_zoffset
        )
        self.mcu_cutter = object_factories.elec_cutter_factory(self.component, "mcu_cutter", mcu_cutter_dims, 0, start_tl=[self.key_matrix.corners["tr"]["x"]/mm, self.key_matrix.corners["tr"]["y"]/mm, 0])
        usb_cutter_dims = dict(
            cut_width = config.USB_cut_width,
            cut_height = config.USB_cut_height,
            cut_extrude = config.USB_cut_extrude,
            PCB_thickness = config.USB_PCB_thickness,
            lip = config.USB_lip,
            tl_margin = config.USB_tl_margin,
            USB_width = config.USB_USB_width,
            USB_height = config.USB_USB_height,
            USB_extrude = config.USB_USB_extrude,
            USB_zoffset = config.USB_USB_zoffset
        )
        self.usb_cutter = object_factories.elec_cutter_factory(self.component, "usb_cutter", usb_cutter_dims, 0) #, start_tl=[self.mcu_cutter.corners["br"]["x"]/mm, self.mcu_cutter.corners["br"]["y"]/mm, 0])
        x=10
        functions.rotate_component(self.usb_cutter.parent_comp, self.usb_cutter.component, -90, [0,0,1])
        functions.move_component(self.usb_cutter.parent_comp, self.usb_cutter.component, [self.mcu_cutter.corners["br"]["x"], self.mcu_cutter.corners["br"]["y"], 0])
        x = 10

class Case():
    def __init__(self, matrix, parent_comp, sketch_plane="xy"):
        self.matrix = matrix
        self.parent_comp = parent_comp
        self.sketch_plane = self.get_sketch_plane(sketch_plane)
        self.case_points = []
        self.get_point_series()
        self.create()

    def get_point_series(self):
        # get series of points starting on col0 tl, col0 tr, col1 tl etc
        for col in self.matrix.cols:
            self.case_points.append(col.corners["tl"])
            self.case_points.append(col.corners["tr"])
        
        for col in reversed(self.matrix.cols):
            self.case_points.append(col.corners["br"])
            self.case_points.append(col.corners["bl"])

    def get_sketch_plane(self, sketch_plane):
        if sketch_plane == "xy":
            return self.parent_comp.xYConstructionPlane
        if sketch_plane == "yz":
            return self.parent_comp.yZConstructionPlane
        if sketch_plane == "xz":
            return self.parent_comp.xZConstructionPlane
    
    def create(self):
        self.create_sketch()

    def create_sketch(self):
        self.sketch = self.parent_comp.sketches.add( self.sketch_plane )
        self.sketch_lines = self.sketch.sketchCurves.sketchLines
        # self.matrix_outline = adsk.core.ObjectCollection.create()
        self.matrix_outline = []
        
        start_pt = adsk.core.Point3D.create(**self.case_points[0])
        for index in range(1, len(self.case_points), 1):
            point = adsk.core.Point3D.create(**self.case_points[index])
            # point2 = adsk.core.Point3D.create(**self.case_points[index+1])

            # self.matrix_outline.add(self.sketch_lines.addByTwoPoints(start_pt, point))
            new_line = self.sketch_lines.addByTwoPoints(start_pt, point)
            self.matrix_outline.append(new_line)
            # if index > 1:
            #     self.sketch.sketchCurves.sketchArcs.addFillet(last_line, last_line.endSketchPoint.geometry, new_line, new_line.endSketchPoint.geometry, 1*mm)
            start_pt = new_line.endSketchPoint
            # last_line = new_line

        point = adsk.core.Point3D.create(**self.case_points[0])
        new_line = self.sketch_lines.addByTwoPoints(start_pt, point)
        # point1 = adsk.core.Point3D.create(**self.case_points[-1])
        # point2 = adsk.core.Point3D.create(**self.case_points[0])

        # self.matrix_outline.add(self.sketch_lines.addByTwoPoints(point1, point2))

        curves = self.sketch.findConnectedCurves(self.sketch_lines.item(0))
        dirPoint = adsk.core.Point3D.create(0,500,0)
        self.offset_curves = self.sketch.offset(curves, dirPoint, 5*mm)

        # for index in range(len(self.offset_curves.item)-1):
        #     functions.

        for index in range(len(self.matrix_outline)):
            line1 = self.offset_curves.item(index)
            line2 = self.offset_curves.item(index+1)
            if functions.angle_between_lines(line1, line2) > 0:
                self.sketch.sketchCurves.sketchArcs.addFillet(line1, line1.endSketchPoint.geometry, line2, line2.startSketchPoint.geometry, config.fillet*mm)
        else:
            line1 = self.offset_curves.item(len(self.matrix_outline))
            line2 = self.offset_curves.item(0)
            if functions.angle_between_lines(line1, line2) > 0:
                self.sketch.sketchCurves.sketchArcs.addFillet(line1, line1.endSketchPoint.geometry, line2, line2.startSketchPoint.geometry, config.fillet*mm)

class Thumbs():
    def __init__(self, parent_comp, name, col, placement_function):
        self.parent_comp = parent_comp
        self.num_keys = config.minidox_num_thumb_keys
        self.name = name
        self.col = col
        self.keys = []
        self.component = None
        self.corners = {}
        self.key_center_locs, self.key_rots = placement_function(self.col)

    def create(self):
        self.component = functions.create_component(self.parent_comp, self.name)

        for key in range(self.num_keys):
            new_key = object_factories.keyhole_factory(
                self.component, 
                f"row{key}", 
                self.key_center_locs[key]["x"], 
                self.key_center_locs[key]["y"], 
                self.key_center_locs[key]["z"],
                self.key_rots[key]
                )
            self.keys.append(new_key)
            if key == 0:
                self.corners["bl"] = new_key.corners["bl"]
                self.corners["br"] = new_key.corners["br"]

            if key == self.num_keys-1:
                self.corners["tl"] = new_key.corners["tl"]
                self.corners["tr"] = new_key.corners["tr"]


class Electronics_cutter():
    '''Creates an object used to cut a hole for electronics.'''
    def __init__(self, parent_comp, name, cutter_dims, rot, start_tl= [0, 0, 0]):
        '''one of tl or tr must remain 0'''
        self.name = name
        self.parent_comp = parent_comp
        self.component = None
        self.corners = {}
        self.cutter_dims = cutter_dims
        self.rot = rot
        self.start_tl = start_tl

    def create(self):
        self.component = functions.create_component(self.parent_comp, self.name)

        x_center = self.start_tl[0] + self.cutter_dims["cut_width"]/2 + self.cutter_dims["tl_margin"]
        y_center = self.start_tl[1] - self.cutter_dims["cut_height"]/2
        z_center = self.start_tl[2]
        self.pcb_cutter = object_factories.box_factory(
            self.component, 
            self.name, 
            self.cutter_dims["cut_height"] + self.cutter_dims["lip"], 
            self.cutter_dims["cut_width"], 
            self.cutter_dims["PCB_thickness"],
            rot=self.rot,
            x_center=x_center,
            y_center=y_center + self.cutter_dims["lip"]/2,
            z_center=z_center
            )
        self.vertical_cutter = object_factories.box_factory(
            self.component, 
            self.name, 
            self.cutter_dims["cut_height"], 
            self.cutter_dims["cut_width"], 
            self.cutter_dims["cut_extrude"],
            rot=self.rot,
            x_center=x_center,
            y_center=y_center,
            z_center=z_center
            )
        self.usb_cutter = object_factories.box_factory(
            self.component,
            "usb_cutter",
            self.cutter_dims["USB_height"],
            self.cutter_dims["USB_width"],
            self.cutter_dims["USB_extrude"],
            rot=self.rot,
            x_center=x_center,
            y_center=y_center + self.cutter_dims["cut_height"]/2,
            z_center=z_center + self.cutter_dims["USB_zoffset"]
        )
        self.get_corners()
        

    def get_corners(self):
        self.corners = self.vertical_cutter.corners

#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, sys
from .Modules import config, class_defs, functions


mm = 0.1

# keyhole_width = 19
# keyhole_height = 19
# keyhole_depth = 4
# keyhole_rim_width = 3
# key_vert_space = 4
# key_notch_width = 5
# key_notch_depth = 0.5
# key_notch_height = 2

class ConfigException(Exception):
    pass




def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if config.num_cols != len(config.col_stagger):
            ui.messageBox("Can not build keyboard. Please make sure each column has a stagger, i.e. num_cols == len(col_stagger)")
            sys.exit('Cancelled')


        design = adsk.fusion.Design.cast( app.activeProduct )
        rootComp = design.rootComponent

        # keyhole1 = class_defs.Keyhole(rootComp, "row1")

        # keyhole1.create_keyhole()

        # keyhole2 = class_defs.Keyhole(rootComp, "row2", 25, 25, 25)

        # keyhole2.create_keyhole()

        # col1 = class_defs.Column(rootComp, 3, 'col1')
        # col1.create()

        # matrix = class_defs.Matrix(rootComp, "key_matrix")
        # matrix.create()

        # case = class_defs.Case(matrix, rootComp)

        # thumbs = class_defs.Thumbs2(rootComp, "thumbs", 0, functions.minidox_thumbs)
        # thumbs.create()

        keyboard = class_defs.Keyboard(rootComp, "keyboard", functions.minidox_thumbs)

        x = 5
        # test1 = Component(rootComp, "test1")
        # test1.create_component()

        # box_test = Box(test1.component, params.keyhole_width, params.keyhole_height, params.keyhole_depth)
        # box_test.create_sketch()
        # box_test.create_body()
    # except ConfigException as e:
    #     if ui:
    #         ui.messageBox(e.args[0] + "\n" + e.args[1])

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

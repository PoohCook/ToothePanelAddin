#Author-Pooh
#Description-Create a toothe Panel on a sketch

import adsk.core, adsk.fusion, adsk.cam, traceback
from . import PNL
from . import CMD

_panel = None
_handlers = []

# command properties
commandId = 'ToothedPanel'
commandName = 'Toothed Panel'
commandDescription = 'Craete a Toothed Panel fo laser cutting\n'
commandResources = './resources/command'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'SketchCreatePanel'


class MySelectHandler(adsk.core.SelectionEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _panel
        try:
            args = adsk.core.SelectionEventArgs.cast(args)
            pnt = adsk.fusion.SketchPoint.cast(args.selection.entity).geometry
            args.isSelectable = True

            cmd = adsk.core.Command.cast(args.firingEvent.sender)
            selectorInput =adsk.core.SelectionCommandInput.cast(cmd.commandInputs.itemById("origin_select"))

            if _panel:
                if selectorInput.selectionCount == 0:
                    _panel.setOrigin(pnt)
                elif selectorInput.selectionCount == 1:
                    _panel.setExtent(pnt) 
                else:
                    origin = selectorInput.selection(0)
                    selectorInput.clearSelection()
                    selectorInput.addSelection(origin.entity)
                    _panel.setExtent(pnt) 

            
        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class MyInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            args = adsk.core.InputChangedEventArgs.cast(args)
            if args.input.id in ["panel_width", "panel_height"]:
                selectorInput =adsk.core.SelectionCommandInput.cast(args.inputs.itemById("origin_select"))
                if selectorInput.selectionCount == 2:
                    origin = selectorInput.selection(0)
                    selectorInput.clearSelection()
                    selectorInput.addSelection(origin.entity)

        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class MyCommandExecutePreviewHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _panel
        try:
            if _panel:
                _panel.draw()
        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))                

# Event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        global _panel
        try:
            cmdArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = cmdArgs.command.commandInputs
            if _panel:
                _panel.draw()
 
        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Event handler that creates my Command.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def createMainTab(self, id, name, inputs):
        tabCmdInput = inputs.addTabCommandInput(id, name)
        mainInputs = tabCmdInput.children

        # Create a selection input.
        selectionInput = mainInputs.addSelectionInput('origin_select', 'Origin', 'where to originate the panel')
        selectionInput.addSelectionFilter(adsk.core.SelectionCommandInput.SketchPoints)
        selectionInput.setSelectionLimits(1,3)

        # Create distance value input X.
        distanceValueInput = mainInputs.addDistanceValueCommandInput('panel_width', 'Panel Width', adsk.core.ValueInput.createByReal(1))
        # distanceValueInput.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(1, 0, 0))
        distanceValueInput.expression = '10 mm'
        distanceValueInput.hasMinimumValue = False
        distanceValueInput.hasMaximumValue = False
        distanceValueInput.isEnabled = False
        
        # Create distance value input Y.
        distanceValueInput2 = mainInputs.addDistanceValueCommandInput('panel_height', 'Panel Height', adsk.core.ValueInput.createByReal(1))
        # distanceValueInput2.setManipulator(adsk.core.Point3D.create(0, 0, 0), adsk.core.Vector3D.create(0, 1, 0))
        distanceValueInput2.expression = '10 mm'
        distanceValueInput2.hasMinimumValue = False
        distanceValueInput2.hasMaximumValue = False
        distanceValueInput2.isEnabled = False

    def createSideTab(self, id, name, inputs):
        # Create a tab input.
        tabCmdInput = inputs.addTabCommandInput(id, name)
        tabInputs = tabCmdInput.children

        tabInputs.addIntegerSpinnerCommandInput('%s_teeth_count' % id, 'Teeth', 0 , 100 , 1, int(0))
        tabInputs.addValueInput('%s_teeth_width' % id, 'Teeth Width', 'mm', adsk.core.ValueInput.createByString("thickness * 2"))
        tabInputs.addValueInput('%s_teeth_depth' % id, 'Teeth depth', 'mm', adsk.core.ValueInput.createByString("thickness"))
        tabInputs.addValueInput('%s_set_back' % id, 'Edge set back', 'mm', adsk.core.ValueInput.createByReal(0))

    def notify(self, args):
        global _panel
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the execute event.           
            onExecute = MyCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 

            onSelect = MySelectHandler()
            cmd.select.add(onSelect)
            _handlers.append(onSelect) 

            onExecutePreview = MyCommandExecutePreviewHandler()
            cmd.executePreview.add(onExecutePreview)
            _handlers.append(onExecutePreview)

            onInputChanged = MyInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            self.createMainTab("main", "Main", inputs)
            self.createSideTab("top", "Top", inputs)
            self.createSideTab("right", "Right", inputs)
            self.createSideTab("bottom", "Bottom", inputs)
            self.createSideTab("left", "Left", inputs)
    
            _panel = PNL.ToothedPanel(inputs)

        except:
            app = adsk.core.Application.get()
            ui  = app.userInterface
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        CMD.addCommandToPanel(workspaceToUse, panelToUse, 
                              commandId, commandName, commandDescription, commandResources, 
                              MyCommandCreatedHandler())

    except:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        CMD.deleteControlAndDefinition(workspaceToUse, panelToUse, commandId)
    except:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

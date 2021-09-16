import adsk.core as ac


# Some utility functions for adding commands to toolbar pannels
def getUi():
    app = ac.Application.get()
    return ac.UserInterface.cast(app.userInterface)


def uiMessageBox(message):
    ui = getUi()
    ui.messageBox(message)


def getWorkspacePanel(workspaceId, panelId):
    ui = getUi()
    workspaces = ui.workspaces
    modelingWorkspace = workspaces.itemById(workspaceId)
    toolbarPanels = modelingWorkspace.toolbarPanels
    return toolbarPanels.itemById(panelId)


def deleteControlAndDefinition(workspaceId, panelId, commandId):
    ui = getUi()
    panel = getWorkspacePanel(workspaceId, panelId)
    commandControl = panel.controls.itemById(commandId)
    if commandControl:
        commandControl.deleteMe()

    commandDefinition = ui.commandDefinitions.itemById(commandId)
    if commandDefinition:
        commandDefinition.deleteMe()


def addCommandToPanel(workspaceId, panelId,
                      commandId, commandName, commandDescription, commandResources, onCommandCreated):
    ui = getUi()
    toolbarPanel = getWorkspacePanel(workspaceId, panelId)
    toolbarControlsPanel = toolbarPanel.controls
    toolbarControlPanel = toolbarControlsPanel.itemById(commandId)
    if not toolbarControlPanel:
        cmdDefs = ac.CommandDefinitions.cast(ui.commandDefinitions)
        cmdDefPanel = ac.CommandDefinition.cast(cmdDefs.itemById(commandId))
        if not cmdDefPanel:
            cmdDefPanel = cmdDefs.addButtonDefinition(commandId, commandName,
                                                      commandDescription, commandResources)
        
        cmdDefPanel.commandCreated.add(onCommandCreated)
        
        toolbarControlPanel = toolbarControlsPanel.addCommand(cmdDefPanel, '')
        toolbarControlPanel.isVisible = True

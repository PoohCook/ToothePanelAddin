import adsk.core, adsk.fusion, adsk.cam
from . import NS

class ToothedPanel():
    def __init__(self, inputs):
        self.lines = None
        self.origin = adsk.core.Point3D.create(0,0,0)
        self.panelWidth = inputs.itemById("panel_width")
        self.panelHeight = inputs.itemById("panel_height")

        self.topInputs = self.loadSideControls("top", inputs)
        self.rightInputs = self.loadSideControls("right", inputs)
        self.bottomInputs = self.loadSideControls("bottom", inputs)
        self.leftInputs = self.loadSideControls("left", inputs)

        self.up = adsk.core.Vector3D.create(0, 1, 0)
        self.down = adsk.core.Vector3D.create(0, -1, 0)
        self.left = adsk.core.Vector3D.create(-1, 0, 0)
        self.right = adsk.core.Vector3D.create(1, 0, 0)

    def loadSideControls(self, id, inputs):
        return NS.Namespace(
            teethWidth=inputs.itemById("%s_teeth_width" % id),
            teethDepth=inputs.itemById("%s_teeth_depth" % id),
            teethCount=inputs.itemById("%s_teeth_count" % id),            
        )

    def setOrigin(self, pnt):
        self.origin = pnt
        self.panelWidth.setManipulator(pnt, adsk.core.Vector3D.create(1, 0, 0))
        self.panelHeight.setManipulator(pnt, adsk.core.Vector3D.create(0, 1, 0))

    def createScaledVector(self, vector, scale):
            retVector = vector.copy()
            retVector.scaleBy(scale)
            return retVector
       
    def generateSide(self, vProgress, vRelief, length, inputs):
        tWidth = inputs.teethWidth.value
        tDepth = inputs.teethDepth.value
        tCount = inputs.teethCount.value
 
        vectors = []
        if tCount < 0:
            raise ValueError("invalid tCount")
        
        elif tCount == 0:
            vectors.append(self.createScaledVector(vProgress, length))
        
        elif tCount == 1:
            prog = (length - tWidth)/2.0
            vectors.append(self.createScaledVector(vProgress, prog))
            vectors.append(self.createScaledVector(vRelief, tDepth))
            vectors.append(self.createScaledVector(vProgress, tWidth))
            vectors.append(self.createScaledVector(vRelief, tDepth * -1))
            vectors.append(self.createScaledVector(vProgress, prog))

        else:
            prog = (length - (tCount * tWidth))/(tCount-1)
            for i in range(tCount-1):
                vectors.append(self.createScaledVector(vProgress, tWidth))
                vectors.append(self.createScaledVector(vRelief, tDepth))
                vectors.append(self.createScaledVector(vProgress, prog))
                vectors.append(self.createScaledVector(vRelief, tDepth * -1))
                
            vectors.append(self.createScaledVector(vProgress, tWidth))

        return vectors           

    def draw(self):
        width = self.panelWidth.value
        height = self.panelHeight.value

        vectors = []
        vectors += self.generateSide(self.up, self.right, height, self.leftInputs)
        vectors += self.generateSide(self.right, self.down, width, self.topInputs)
        vectors += self.generateSide(self.down, self.left, height, self.rightInputs)
        vectors += self.generateSide(self.left, self.up, width, self.bottomInputs)

        app = adsk.core.Application.get()
        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)
        lines = sketch.sketchCurves.sketchLines
        points = sketch.sketchPoints
        firstPnt = points.add(self.origin)
        lastPnt = firstPnt
        nextPnt = self.origin.copy()
        for vector in vectors[:-1]:
            nextPnt.translateBy(vector)
            nextPnt = points.add(nextPnt)
            line = lines.addByTwoPoints(lastPnt, nextPnt)
            lastPnt = line.endSketchPoint
            nextPnt = lastPnt.geometry.copy()

        lines.addByTwoPoints(lastPnt, firstPnt)

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
            setBack=inputs.itemById("%s_set_back" % id),            
        )

    def setOrigin(self, pnt):
        app = adsk.core.Application.get()
        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)

        self.origin = pnt
        manPnt = self.origin.copy()
        
        manPnt.transformBy(sketch.transform)
        xVector = adsk.core.Vector3D.create(1, 0, 0)
        xVector.transformBy(sketch.transform)
        yVector = adsk.core.Vector3D.create(0, 1, 0)
        yVector.transformBy(sketch.transform)
        self.panelWidth.setManipulator(manPnt, xVector)
        self.panelHeight.setManipulator(manPnt, yVector)
        self.panelWidth.isEnabled = True
        self.panelHeight.isEnabled = True

    def createScaledVector(self, vector, scale):
            retVector = vector.copy()
            retVector.scaleBy(scale)
            return retVector

    def getValues(self, inputs, length, relief):
        return NS.Namespace(
            tWidth=inputs.teethWidth.value,
            tDepth=inputs.teethDepth.value,
            tCount=inputs.teethCount.value,
            setBack=inputs.setBack.value,
            length=length,
            relief=relief,
        )        

    def generateSide(self, vProgress, vRelief, values):       
        if values.length < 0:
            values.tWidth *= -1
            values.setBack *= -1

        if values.relief < 0:
            values.tDepth *= -1
 
        vectors = []
        if values.tCount < 0:
            raise ValueError("invalid tCount")
        
        elif values.tCount == 0:
            vectors.append(self.createScaledVector(vProgress, values.length))
        
        elif values.tCount == 1:
            prog = (values.length - values.tWidth)/2.0
            vectors.append(self.createScaledVector(vRelief, values.tDepth))
            vectors.append(self.createScaledVector(vProgress, prog))
            vectors.append(self.createScaledVector(vRelief, values.tDepth * -1))
            vectors.append(self.createScaledVector(vProgress, values.tWidth))
            vectors.append(self.createScaledVector(vRelief, values.tDepth))
            vectors.append(self.createScaledVector(vProgress, prog))
            vectors.append(self.createScaledVector(vRelief, values.tDepth * -1))

        else:
            if values.setBack != 0:
                vectors.append(self.createScaledVector(vRelief, values.tDepth))
                vectors.append(self.createScaledVector(vProgress, values.setBack))
                vectors.append(self.createScaledVector(vRelief, values.tDepth * -1))
                values.length -= (2 * values.setBack)

            prog = (values.length - (values.tCount * values.tWidth))/(values.tCount-1)
            for i in range(values.tCount-1):
                vectors.append(self.createScaledVector(vProgress, values.tWidth))
                vectors.append(self.createScaledVector(vRelief, values.tDepth))
                vectors.append(self.createScaledVector(vProgress, prog))
                vectors.append(self.createScaledVector(vRelief, values.tDepth * -1))
                
            vectors.append(self.createScaledVector(vProgress, values.tWidth))

            if values.setBack != 0:
                vectors.append(self.createScaledVector(vRelief, values.tDepth))
                vectors.append(self.createScaledVector(vProgress, values.setBack))
                vectors.append(self.createScaledVector(vRelief, values.tDepth * -1))

        return vectors  

    def isParallel(self, vec1, vec2):
        return vec2.x * vec1.y == vec1.x * vec2.y

    def joinSegments(self, segment1, seg1Direction, segment2, seg2Direction, concactinate=True):
        seg1Delta = None
        if not self.isParallel(segment1[-1], seg1Direction):
            seg1Delta = segment1[-1]
            del(segment1[-1])
        seg2Delta = None
        if not self.isParallel(segment2[0], seg2Direction):
            seg2Delta = segment2[0]
            del(segment2[0])

        if seg1Delta:
            segment2[0].add(seg1Delta)
        if seg2Delta:
            segment1[-1].add(seg2Delta)

        if concactinate:
            return segment1 + segment2
        
        offset = adsk.core.Vector3D.create(0,0,0)
        if seg1Delta:
            offset.subtract(seg1Delta)
        if seg2Delta:
            offset.add(seg2Delta)
        return offset

    def draw(self):
        width = self.panelWidth.value
        height = self.panelHeight.value

        leftValues = self.getValues(self.leftInputs, height, width)
        topValues = self.getValues(self.topInputs, width, height)
        rightValues = self.getValues(self.rightInputs, height, width)
        bottomValues = self.getValues(self.bottomInputs, width, height)

        segmentLeft = self.generateSide(self.up, self.right, leftValues)
        segmentTop = self.generateSide(self.right, self.down, topValues)
        segmentRight = self.generateSide(self.down, self.left, rightValues)
        segmentBottom = self.generateSide(self.left, self.up, bottomValues)

        vectors = self.joinSegments(segmentLeft, self.up, segmentTop, self.right)
        vectors = self.joinSegments(vectors, self.right, segmentRight, self.down)
        vectors = self.joinSegments(vectors, self.down, segmentBottom, self.left)
        offset = self.joinSegments(vectors, self.left, vectors, self.up, concactinate=False)

        app = adsk.core.Application.get()
        sketch = adsk.fusion.Sketch.cast(app.activeEditObject)
        lines = sketch.sketchCurves.sketchLines
        points = sketch.sketchPoints

        origin = self.origin.copy()
        origin.translateBy(offset)

        firstPnt = points.add(origin)
        lastPnt = firstPnt
        nextPnt = origin.copy()
        for vector in vectors[:-1]:
            nextPnt.translateBy(vector)
            nextPnt = points.add(nextPnt)
            line = lines.addByTwoPoints(lastPnt, nextPnt)
            lastPnt = line.endSketchPoint
            nextPnt = lastPnt.geometry.copy()

        lines.addByTwoPoints(lastPnt, firstPnt)

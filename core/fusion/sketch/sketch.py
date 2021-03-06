from adsk.core import Point3D
from adsk.fusion import DimensionOrientations

from .rectangle import Rectangle

HorizontalDimension = DimensionOrientations.HorizontalDimensionOrientation
VerticalDimension = DimensionOrientations.VerticalDimensionOrientation


class Sketch:

    def __init__(self, name, body, face):
        super().__init__()

        self.face = face
        self.sketch = body.parent.sketches.add(self.face.brepface)
        self.sketch.name = name
        self.lines = self.sketch.sketchCurves.sketchLines

        # Change the lines outlining the face into construction lines
        self.__face_lines = Rectangle(self.sketch, self.lines[0:4], construction=True)

        # Project the hidden edges of the face into the sketch so that
        # the edges can easily be referenced from the Line class; making
        # other operations much easier.
        for line in self.face.brepface.edges[0:4]:
            ref = self.sketch.project(line)

        # Select the new projected lines and create a Rectangle class
        # from them.
        self.border = Rectangle(self.sketch, self.lines[4:8], construction=True)

        # Save some reference points that will be used later
        self.reference_points = self.border.reference_points
        self.reference_plane = self.sketch.referencePlane
        self.reference_line = self.border.reference_line

    def draw_rectangle(self, point, length, constrain=False):
        width = self.border.width

        return Rectangle.draw(self.sketch,
                              point,
                              self.offset_point(point, length, width),
                              self.border.bottom.sketch_line if constrain else None,
                              self.border.top.sketch_line if constrain else None,
                              self.border.bottom.left)

    def draw_margin(self, point):
        end_point = self.offset_point(point, 0, self.border.width)

        marginline = self.lines.addByTwoPoints(point, end_point)
        marginline.isConstruction = True

        self.margin_dimension = self.sketch.sketchDimensions.addDistanceDimension(
            self.border.bottom.left.point,
            marginline.startSketchPoint,
            HorizontalDimension,
            Point3D.create(point.x + .5, point.y - .5, 0)
        )
        self.sketch.geometricConstraints.addPerpendicular(self.border.bottom.sketch_line,
                                                          marginline)
        return marginline

    def offset_point(self, point, length, width=0):
        if self.is_vertical:
            xoffset = width
            yoffset = length
        else:
            yoffset = width
            xoffset = length

        return Point3D.create(point.x + xoffset,
                              point.y + yoffset,
                              point.z)

    @property
    def is_vertical(self):
        return self.border.is_vertical

    @property
    def name(self):
        return self.face.brepface.name

    @name.setter
    def name(self, value):
        self.face.brepface.name = value

    @property
    def profiles(self):
        return self.sketch.profiles

    @property
    def start_point(self):
        return self.border.bottom.left.geometry

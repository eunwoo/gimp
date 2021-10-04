VERTICAL = 0
OTHERS = 1

class Line:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        if x1 == x2:
            self.type = VERTICAL
            if y1 < y2: 
                self.y_min = y1
                self.y_max = y2
            else:
                self.y_min = y2
                self.y_max = y1
        else:
            self.type = OTHERS
            (self.a, self.b) = self.LineCoef([x1, y1], [x2, y2])

    def LineCoef(self, p1, p2):
        x1 = p1[0]
        x2 = p2[0]
        y1 = p1[1]
        y2 = p2[1]
        a = (y1 - y2)/(x1 - x2)
        b = (-x2*y1 + x1*y2)/(x1 - x2)
        return (a, b)

def TestCrossVertical(lineVert, line):
    y_sol = line.a * lineVert.x1 + line.b
    if (y_sol - lineVert.y_min) * (y_sol - lineVert.y_max) < 0:
        return True
    else:
        return False

def TestCross(line1, line2):
    if line1.type == VERTICAL and line2.type == VERTICAL:
        return False
    else:
        if line1.type == VERTICAL:
            return TestCrossVertical(line1, line2)
        elif line2.type == VERTICAL:
            return TestCrossVertical(line2, line1)
        else:
            x_sol = (-line1.b + line2.b)/(line1.a - line2.a)
            y_sol = (-line2.a*line1.b + line1.a*line2.b)/(line1.a - line2.a)
            if (x_sol - line1.x1)*(x_sol - line1.x2) < 0 and (x_sol - line2.x1)*(x_sol - line2.x2) < 0:
                return True
            else:
                return False
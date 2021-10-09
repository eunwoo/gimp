class BezierPoint:
    def __init__(self, x_g1, y_g1, x, y, x_g2, y_g2):
        self.x_g1 = x_g1
        self.y_g1 = y_g1
        self.x = x
        self.y = y
        self.x_g2 = x_g2
        self.y_g2 = y_g2
        self.acute = False
        self.acute2 = False
import line
import sys
import math
from PySide6.QtWidgets import *
from PySide6.QtGui import QPainter, QPen, QWheelEvent, QColor, QBrush
from PySide6.QtCore import Qt, QRect
from PySide6 import QtCore, QtGui
import PySide6
import json
import os.path
from MainWidget import *
from BezierPoint import BezierPoint

class MyCanvas(QWidget):
    def __init__(self, parent=None):
        print('MyCanvas init')
        self.parent = parent
        self.bzPoints = []
        super().__init__()
        self.setupVariable()
        self.setupUI()

    def setupVariable(self):
        self.bCtrl = False
        self.bShift = False
        self.showControlPoint = True
        self.selected_point = -1
        self.zoomFactor = 1.2
        
        self.w = 600
        self.h = 600
        self.angle = 30.0
        self.v_org_x = 0
        self.v_org_y = 0
        self.v_w = 600
        self.v_h = self.v_w
        self.run_mode = 0
        self.show_curve = True

        self.zoomInCenterX = self.w*0.5
        self.zoomInCenterY = self.h*0.5

        self.CalcScale()

    def setupUI(self):
        self.setMouseTracking(True)
        self.setWindowTitle('my canvas widget')
        self.move(300,300)
        self.resize(400,200)
        self.show()

    def CalcScale(self):
        self.scale_w = self.w/self.v_w
        self.scale_h = self.h/self.v_h
        if self.scale_w > self.scale_h:
            self.scale = self.scale_h
        else:
            self.scale = self.scale_w

    def wheelEvent(self, event: QWheelEvent):
        print('wheel event(%d,%d)'%(event.angleDelta().x(), event.angleDelta().y()))
        if self.bCtrl:
            if event.angleDelta().y() > 0:
                self.zoomIn(self.mouse_x, self.mouse_y)
                self.update()
            else:
                self.zoomOut(self.mouse_x, self.mouse_y)
                self.update()
        elif self.bShift == False:
            if event.angleDelta().y() > 0:
                self.MoveDown()
                self.update()
            else:
                self.MoveUp()
                self.update()
        else:
            if event.angleDelta().y() > 0:
                self.MoveRight()
                self.update()
            else:
                self.MoveLeft()
                self.update()

    def mouseMoveEvent(self, event) -> None:
        x = event.position().x()
        y = event.position().y()
        self.mouse_x = x
        self.mouse_y = y
        msg = 'mouseMoveEvent: x=%d, y=%d' % (event.position().x(), event.position().y())
        print (msg)
        sel_i = self.searchPoint(x, y)
        if sel_i != -1:
            i = sel_i
            if i == 0:
                prev = len(self.bzPoints)-1
            else:
                prev = i - 1
            if i == len(self.bzPoints)-1:
                next = 0
            else:
                next = i + 1
            dx1 = self.bzPoints[next].x - self.bzPoints[i].x
            dy1 = self.bzPoints[next].y - self.bzPoints[i].y
            l1 = math.sqrt(dx1*dx1 + dy1*dy1)
            dx2 = self.bzPoints[prev].x - self.bzPoints[i].x
            dy2 = self.bzPoints[prev].y - self.bzPoints[i].y
            l2 = math.sqrt(dx2*dx2 + dy2*dy2)
            if l1 != 0 and l2 != 0:
                th = math.acos((dx1 * dx2 + dy1 * dy2)/l1/l2)
            else:
                th = 0
            msg = 'selected point[%d]=(%.3f, %.3f), angle=%.3f'%(sel_i, self.bzPoints[sel_i].x, self.bzPoints[sel_i].y, th*180/math.pi)
            print(msg)
            self.parent.parent.statusbar.showMessage(msg)
        if self.selected_point != sel_i:
            self.selected_point = sel_i
            self.repaint()            
    def keyPressEvent(self, e):
        print('key press event')
        if e.key() == Qt.Key_Control:
            self.bCtrl = True
        elif e.key() == Qt.Key_Shift:
            self.bShift = True
    def keyReleaseEvent(self, e):
        print('key release event')
        if e.key() == Qt.Key_Control:
            self.bCtrl = False
        elif e.key() == Qt.Key_Shift:
            self.bShift = False

    def paintEvent(self, e):
        print('cavnas paint event')
        qp = QPainter(self)
        self.Draw(qp)

    def resizeEvent(self, event: PySide6.QtGui.QResizeEvent) -> None:
        self.w = self.width()
        self.h = self.height()
        self.v_w = self.w / self.scale
        self.v_h = self.h / self.scale

    def MoveUp(self):
        self.v_org_y = self.v_org_y + self.h / self.scale * 0.1
    def MoveDown(self):
        self.v_org_y = self.v_org_y - self.h / self.scale * 0.1
    def MoveLeft(self):
        self.v_org_x = self.v_org_x + self.w / self.scale * 0.1
    def MoveRight(self):
        self.v_org_x = self.v_org_x - self.w / self.scale * 0.1
    def zoomIn(self, x, y):
        print('zoom in')
        self.scale = self.scale * self.zoomFactor
        self.v_org_x = self.v_org_x + x/self.scale*(self.zoomFactor - 1.0)
        self.v_org_y = self.v_org_y + y/self.scale*(self.zoomFactor - 1.0)
        self.v_w = self.w/self.scale
        self.v_h = self.h/self.scale
    def zoomOut(self, x, y):
        print('zoom out')
        self.scale = self.scale / self.zoomFactor
        self.v_org_x = self.v_org_x + x/self.scale*(1.0-self.zoomFactor)/self.zoomFactor
        self.v_org_y = self.v_org_y + y/self.scale*(1.0-self.zoomFactor)/self.zoomFactor
        self.v_w = self.w/self.scale
        self.v_h = self.h/self.scale

    def SetData(self, data):
        self.bzPoints = data

    def vw_to_scr_x(self, x):
        return (x - self.v_org_x)*self.scale
    def vw_to_scr_y(self, y):
        return (y - self.v_org_y)*self.scale
    def scr_to_vw_x(self, x):
        return x/self.scale + self.v_org_x
    def scr_to_vw_y(self, y):
        return y/self.scale + self.v_org_y

    def Draw(self, qp):
        qp.fillRect(QRect(0,0,self.width(),self.height()), QBrush(QColor(0, 0, 10, 255)))
        self.draw_line(qp)
        self.draw_point(qp)
        if self.show_curve == True:
            self.draw_curve(qp)
        if self.showControlPoint:
            self.draw_control_point(qp)
        if self.selected_point != -1:
            x = self.vw_to_scr_x(self.bzPoints[self.selected_point].x) - 10
            y = self.vw_to_scr_y(self.bzPoints[self.selected_point].y) - 10
            qp.setPen(QPen(Qt.blue, 3, Qt.DotLine))
            qp.drawEllipse(int(x), int(y), 20, 20)
        if hasattr(self, 'lines'):
            qp.setPen(QPen(Qt.red, 3, Qt.DotLine))
            x1 = self.vw_to_scr_x(self.lines[0][0])
            y1 = self.vw_to_scr_y(self.lines[0][1])
            x2 = self.vw_to_scr_x(self.lines[1][0])
            y2 = self.vw_to_scr_y(self.lines[1][1])
            qp.drawLine(int(x1), int(y1), int(x2), int(y2))
        if hasattr(self, 'x_min') and hasattr(self, 'test_line_idx'):
            qp.setPen(QPen(Qt.red, 3, Qt.DotLine))
            x1 = self.vw_to_scr_x(self.x_min)
            y1 = self.vw_to_scr_y(self.y_min)
            x2 = self.vw_to_scr_x(self.x_max)
            y2 = self.vw_to_scr_y(self.y_max)
            qp.drawRect(int(x1), int(y1), int(x2)-int(x1), int(y2)-int(y1))

            x1 = self.vw_to_scr_x(self.bzPoints[self.test_line_idx].x)
            y1 = self.vw_to_scr_y(self.bzPoints[self.test_line_idx].y)
            x2 = self.vw_to_scr_x(self.bzPoints[self.test_line_idx+1].x)
            y2 = self.vw_to_scr_y(self.bzPoints[self.test_line_idx+1].y)
            qp.drawLine(int(x1), int(y1), int(x2), int(y2))
        # p_test to p_edge_bbox
        if hasattr(self, 'x_min') and hasattr(self, 'lines'):
            qp.setPen(QPen(Qt.red, 3, Qt.DotLine))
            x1 = self.vw_to_scr_x(self.x_min)
            y1 = self.vw_to_scr_y(self.y_min)
            x2 = self.vw_to_scr_x((self.lines[0][0]+self.lines[2][0])*0.5)
            y2 = self.vw_to_scr_y((self.lines[0][1]+self.lines[2][1])*0.5)
            qp.drawLine(int(x1), int(y1), int(x2), int(y2))

        if hasattr(self, 'x_sol'):
            # draw cross point
            qp.setPen(QPen(Qt.blue, 15))
            x1 = self.vw_to_scr_x(self.x_sol)
            y1 = self.vw_to_scr_y(self.y_sol)
            qp.drawPoint(int(x1), int(y1))

        qp.fillRect(QRect(15,5,160,80), QBrush(QColor(255, 255, 255, 220)))
        qp.setPen(QPen(Qt.black, 15))
        text = 'v_org=(%.3f, %.3f)'%(self.v_org_x, self.v_org_y)
        qp.drawText(20,20, text)
        text = 'scale=(%.3f)'%(self.scale)
        qp.drawText(20,40, text)
        text = 'v_center=(%.3f, %.3f)'%(self.scr_to_vw_x(self.w/2), self.scr_to_vw_y(self.h/2))
        qp.drawText(20,60, text)
        text = 'v_size=(%.3f, %.3f)'%(self.v_w, self.v_h)
        qp.drawText(20,80, text)

    def draw_line(self, qp):
        if len(self.bzPoints) > 1:
            qp.setPen(QPen(Qt.cyan, 2))
            for i in range(len(self.bzPoints)-1):
                x1 = self.vw_to_scr_x(self.bzPoints[i].x)
                y1 = self.vw_to_scr_y(self.bzPoints[i].y)
                x2 = self.vw_to_scr_x(self.bzPoints[i+1].x)
                y2 = self.vw_to_scr_y(self.bzPoints[i+1].y)
                qp.drawLine(int(x1), int(y1), int(x2), int(y2))
            x1 = self.vw_to_scr_x(self.bzPoints[len(self.bzPoints)-1].x)
            y1 = self.vw_to_scr_y(self.bzPoints[len(self.bzPoints)-1].y)
            x2 = self.vw_to_scr_x(self.bzPoints[0].x)
            y2 = self.vw_to_scr_y(self.bzPoints[0].y)
            qp.drawLine(int(x1), int(y1), int(x2), int(y2))

    def draw_point(self, qp):
        for i in range(len(self.bzPoints)):
            if self.bzPoints[i].acute == True:
                qp.setPen(QPen(Qt.red, 10))
            else:
                qp.setPen(QPen(Qt.darkGreen, 5))
            x1 = self.vw_to_scr_x(self.bzPoints[i].x)
            y1 = self.vw_to_scr_y(self.bzPoints[i].y)
            qp.drawPoint(int(x1), int(y1))

    def draw_control_point(self, qp):
        qp.setPen(QPen(Qt.red, 1))
        for i in range(len(self.bzPoints)):
            x = self.vw_to_scr_x(self.bzPoints[i].x)
            y = self.vw_to_scr_y(self.bzPoints[i].y)
            x1 = self.vw_to_scr_x(self.bzPoints[i].x_g1)
            y1 = self.vw_to_scr_y(self.bzPoints[i].y_g1)
            qp.drawLine(int(x), int(y), int(x1), int(y1))
            qp.drawPoint(int(x), int(y))
            qp.drawPoint(int(x1), int(y1))
            x1 = self.vw_to_scr_x(self.bzPoints[i].x_g2)
            y1 = self.vw_to_scr_y(self.bzPoints[i].y_g2)
            qp.drawPoint(int(x1), int(y1))
            qp.drawLine(int(x), int(y), int(x1), int(y1))

    # def drawBezierCurve(self, qp):
    #     pen = QPen(Qt.black, 7)
    #     qp.setPen(pen)
    #     path = QPainterPath()
    #     path.moveTo(50, 50)
    #     path.cubicTo(200, 50, 50, 350, 350, 350)
        
    #     qp.drawPath(path)

    def draw_curve(self, qp):   # draw cubic Bezier curve
        qp.setPen(QPen(Qt.red, 1))
        for i in range(len(self.bzPoints)):
            for t_step in range(100):
                if i == len(self.bzPoints)-1:
                    next = 0
                else:
                    next = i+1
                t = t_step*0.01
                # P12t = P1 + t*P12 = Pa
                P12tx = self.bzPoints[i].x + t*(self.bzPoints[i].x_g2 - self.bzPoints[i].x)
                P12ty = self.bzPoints[i].y + t*(self.bzPoints[i].y_g2 - self.bzPoints[i].y)
                # P23t = P2 + t*P23 = Pb
                P23tx = self.bzPoints[i].x_g2 + t*(self.bzPoints[next].x_g1 - self.bzPoints[i].x_g2)
                P23ty = self.bzPoints[i].y_g2 + t*(self.bzPoints[next].y_g1 - self.bzPoints[i].y_g2)
                # P34t = P3 + t*P34 = Pc
                P34tx = self.bzPoints[next].x_g1 + t*(self.bzPoints[next].x - self.bzPoints[next].x_g1)
                P34ty = self.bzPoints[next].y_g1 + t*(self.bzPoints[next].y - self.bzPoints[next].y_g1)
                # Pab = Pa + t*(Pb - Pa)
                Pabx = P12tx + t*(P23tx - P12tx)
                Paby = P12ty + t*(P23ty - P12ty)
                # Pbc = Pb + t*(Pc - Pb)
                Pbcx = P23tx + t*(P34tx - P23tx)
                Pbcy = P23ty + t*(P34ty - P23ty)
                # P = Pab + t*(Pbc - Pab)
                Px = Pabx + t*(Pbcx - Pabx)
                Py = Paby + t*(Pbcy - Paby)
                x1 = self.vw_to_scr_x(Px)
                y1 = self.vw_to_scr_y(Py)
                qp.drawPoint(int(x1), int(y1))
                if i > 0:
                    qp.drawLine(int(x1), int(y1), int(xprev), int(yprev))
                xprev = x1
                yprev = y1
    def searchPoint(self, x, y):
        x_max = self.w
        y_max = self.h
        dist_min = math.sqrt(x_max*x_max + y_max*y_max)
        sel_i = -1
        for i in range(len(self.bzPoints)):
            dx = self.bzPoints[i].x - self.scr_to_vw_x(x)
            dy = self.bzPoints[i].y - self.scr_to_vw_y(y)
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < dist_min:
                dist_min = dist
                sel_i = i
        return sel_i

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyCanvas()
    sys.exit(app.exec())

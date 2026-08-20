from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPainter, QPen, QImage, QColor, QTransform
from PyQt6.QtWidgets import QApplication, QWidget
import sys
import numpy as np
import colourToNumberConverter
import math

class NumbersGrid(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colour By Number")
        self.panOffset = QPoint(0,0)
        self.lastMousePos = QPoint(0,0)
        self.numbersMatrix, self.usedColours = colourToNumberConverter.GenerateNumberGrid()
        self.zoom = 1.0
        self.gridCoordinates = []
        self.closestCoord = [-1,-1]
        self.usedCoord = []
        self.cellSize = 50
        self.selectedColour = -1
        self.transform = QTransform

    def paintEvent(self, event):
        print("Rendering")
        qPainter = QPainter(self)
        
        qPainter.setBrush(Qt.BrushStyle.NoBrush)
        qPainter.translate(self.panOffset)
        qPainter.scale(self.zoom, self.zoom)
        self.transform = QPainter.combinedTransform(qPainter)
        #ENSURE 3000, 3000 IS CHANGED TO SCALE WITH SELECTED IMAGE SIZE, can toggle by uncommenting
        # underlayImage = QImage("compressed.png").scaled(2500, 2500)
        # qPainter.drawImage(QPoint(0,0), underlayImage)

        centeringOffset = self.cellSize/2.5
        m, n = self.numbersMatrix.shape
        for i in range(n):
            x = ((i*self.cellSize))
            for j in range(m):
                y = ((j*self.cellSize))
                self.gridCoordinates.append([x,y])
                qPainter.drawText(int((x+centeringOffset)),int((y+(self.cellSize/2)+centeringOffset)), str(self.numbersMatrix[j][i]))
                qPainter.drawRect(x, y, self.cellSize, self.cellSize)

        if self.closestCoord != [-1,-1]:
            tileNumber = self.numbersMatrix[int(((self.closestCoord[1])/self.cellSize))][int(((self.closestCoord[0])/self.cellSize))]
            rgbVal = [(self.usedColours[tileNumber-1][0]*255).astype(np.uint8), (self.usedColours[tileNumber-1][1]*255).astype(np.uint8), (self.usedColours[tileNumber-1][2]*255).astype(np.uint8)]
            print("InternalRGB " + str(rgbVal))
            if self.selectedColour == tileNumber-1:
                self.usedCoord.append([self.closestCoord, rgbVal])

            for coords in range(len(self.usedCoord)):
                qPainter.setBrush(QColor(self.usedCoord[coords][1][0], self.usedCoord[coords][1][1], self.usedCoord[coords][1][2]))
                qPainter.drawRect(self.usedCoord[coords][0][0], self.usedCoord[coords][0][1], self.cellSize, self.cellSize)
                qPainter.setBrush(QColor(255,255,255))

        qPainter.resetTransform()

        for i in range(len(self.usedColours)):
            if i != self.selectedColour:
                qPainter.setBrush(QColor((self.usedColours[i][0]*255).astype(np.uint8), (self.usedColours[i][1]*255).astype(np.uint8), (self.usedColours[i][2]*255).astype(np.uint8)))
                qPainter.drawRect((i*(self.cellSize)), 0, self.cellSize, self.cellSize)
                qPainter.setBrush(Qt.BrushStyle.NoBrush)
                qPainter.drawText(20+(i*(self.cellSize)), 20, str(i+1))
            else:
                qPainter.setBrush(QColor((self.usedColours[i][0]*255).astype(np.uint8), (self.usedColours[i][1]*255).astype(np.uint8), (self.usedColours[i][2]*255).astype(np.uint8)))
                qPainter.setPen(QPen(QColor(255,255,255), 3))
                qPainter.drawRect((i*(self.cellSize)), 0, self.cellSize, self.cellSize)
                qPainter.setBrush(Qt.BrushStyle.NoBrush)
                qPainter.setPen(Qt.PenStyle.SolidLine)
                qPainter.drawText(20+(i*(self.cellSize)), 20, str(i+1))

        print("Drawn objects succesfully")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.lastMousePos = event.pos()
        if event.button() == Qt.MouseButton.RightButton:
            unalteredPos = event.position().toPoint()
            mousePos = (event.pos() - self.panOffset)/self.zoom
            closest_point = min(self.gridCoordinates, key=lambda c: math.hypot((c[0]+(self.cellSize/2)) - mousePos.x(), (c[1]+(self.cellSize/2)) - mousePos.y()))
            print("YmousePos " + str(unalteredPos.y()))
            if unalteredPos.y() > 50:
                self.closestCoord = closest_point   
                print(closest_point)
            elif unalteredPos.y() < 50:
                print(unalteredPos.x())
                self.selectedColour = self.usedColours.index(self.usedColours[(int((unalteredPos.x())/(self.cellSize)))])
                self.closestCoord = closest_point
                print("SelectedColour1 " + str(self.selectedColour))
            self.update()

            #check mouse pos
            #find what cell mouse is in
            #check cell number
            #fill with correct colour

    def mouseMoveEvent(self, event):
            delta = event.pos() - self.lastMousePos
            self.panOffset += delta
            self.lastMousePos = event.pos()
            self.update()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.update() 

        
app = QApplication(sys.argv)
window = NumbersGrid()
window.show()
sys.exit(app.exec())

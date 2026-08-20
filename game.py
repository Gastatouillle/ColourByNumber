from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPainter, QPen, QImage, QColor, QTransform
from PyQt6.QtWidgets import QApplication, QWidget
import sys
import numpy as np
import colourToNumberConverter
import math

class NumbersGrid(QWidget):
    #initialise all values for variables used between scopes
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

    #main event, runs every update
    def paintEvent(self, event):
        print("Rendering")
        #creates painter object, assigns default brush at beginning of each loop
        qPainter = QPainter(self)
        qPainter.setBrush(Qt.BrushStyle.NoBrush)

        #translates and zooms widget by offsets. Used for pan and zoom when program is running
        qPainter.translate(self.panOffset)
        qPainter.scale(self.zoom, self.zoom)

        # debug code, puts image underlay underneath number grid

        # underlayImage = QImage("compressed.png").scaled(50, 50)
        # qPainter.drawImage(QPoint(0,0), underlayImage)

        #centeringOffset holds an offset such that numbers are roughly centered to the grid cells
        centeringOffset = self.cellSize/2.5

        #store size of numbers grid matrix as rows/column
        m, n = self.numbersMatrix.shape

        #iterate over the size of numbersmatrix, n and m are interchangeable as the image is always square
        for i in range(n):
            #find current x coordinate in pixels by multiplying the column by cellsize
            x = ((i*self.cellSize))
            for j in range(m):
                #find current y coordinate in pixels by multiplying the row by cellsize
                y = ((j*self.cellSize))

                #save the currrent coordinates to a list. Saves the top left of each cell
                self.gridCoordinates.append([x,y])

                #draw the text for each cell at x,y adjusted for centre offset. Text value is the number that cell has been assigned
                qPainter.drawText(int((x+centeringOffset)),int((y+(self.cellSize/2)+centeringOffset)), str(self.numbersMatrix[j][i]))

                #draw the grid cell relative to the top left of the cell x,y. cellSize determines the height and width of a cell
                qPainter.drawRect(x, y, self.cellSize, self.cellSize)

        #if the closest cell is not default value
        if self.closestCoord != [-1,-1]:
            #find the number a cell/tile has been assigned by dividing the x and y value of the coordinate by the cellsize. eg: If closestcoord is [100, 100], tile is matrix index -> [2,2]
            tileNumber = self.numbersMatrix[int(((self.closestCoord[1])/self.cellSize))][int(((self.closestCoord[0])/self.cellSize))]

            #find the rgb value of a cell by accessing the list of colours that are in the picture. usedcolours is a list of np.floats. So must be converted to RGB values
            rgbVal = [(self.usedColours[tileNumber-1][0]*255).astype(np.uint8), (self.usedColours[tileNumber-1][1]*255).astype(np.uint8), (self.usedColours[tileNumber-1][2]*255).astype(np.uint8)]
            print("InternalRGB " + str(rgbVal))

            #if the selected colour is the same as the number of the cell. ie: if selected colour = 1, and tile number = 1. Continue
            if self.selectedColour == tileNumber-1:
                self.usedCoord.append([self.closestCoord, rgbVal])

            #iterate over the list of coordinates that have been used. This redraws all completed cells each update
            #usedCoords is of form [[x,y], [r,g,b]]
            for coords in range(len(self.usedCoord)):
                #set the colour of the brush to the colour of the cell
                qPainter.setBrush(QColor(self.usedCoord[coords][1][0], self.usedCoord[coords][1][1], self.usedCoord[coords][1][2]))

                #draw the cell itself at the coordinates accessed from coords and at cellsize by cellsize
                qPainter.drawRect(self.usedCoord[coords][0][0], self.usedCoord[coords][0][1], self.cellSize, self.cellSize)

                #reset the brush colour to white
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
        if event.button() == Qt.MouseButton.RightButton:
            self.lastMousePos = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            unalteredPos = event.position().toPoint()
            mousePos = (event.pos() - self.panOffset)/self.zoom
            closestPoint = min(self.gridCoordinates, key=lambda c: math.hypot((c[0]+(self.cellSize/2)) - mousePos.x(), (c[1]+(self.cellSize/2)) - mousePos.y()))
            print("YmousePos " + str(unalteredPos.y()))
            if unalteredPos.y() > 50:
                self.closestCoord = closestPoint   
                print(closestPoint)
            elif unalteredPos.y() < 50:
                print(unalteredPos.x())
                self.selectedColour = self.usedColours.index(self.usedColours[(int((unalteredPos.x())/(self.cellSize)))])
                self.closestCoord = closestPoint
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

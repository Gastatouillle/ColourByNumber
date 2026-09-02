from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtWidgets import QApplication, QWidget
import sys
import numpy as np
import colourToNumberConverter
import math
import time

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
        self.gridCoordsApplied = False
        self.closestCoord = [-1,-1]
        self.usedCoord = []
        self.cellSize = 50
        self.selectedColour = -1
        self.elapsedTimes = []

    #main event, runs every update
    def paintEvent(self, event):
        print("Rendering")
        #creates painter object, assigns default brush at beginning of each loop
        qPainter = QPainter(self)
        qPainter.setBrush(Qt.BrushStyle.NoBrush)

        #translates and zooms widget by offsets. Used for pan and zoom when program is running
        qPainter.translate(self.panOffset)
        qPainter.scale(self.zoom, self.zoom)

        #centeringOffset holds an offset such that numbers are roughly centered to the grid cells
        centeringOffset = self.cellSize/2.5

        #store size of numbers grid matrix as rows/column
        m, n = self.numbersMatrix.shape

        #draw full grid
        #iterate over the size of numbersmatrix, n and m are interchangeable as the image is always square
        for i in range(n):
            #find current x coordinate in pixels by multiplying the column by cellsize
            x = ((i*self.cellSize))
            for j in range(m):
                #find current y coordinate in pixels by multiplying the row by cellsize
                y = ((j*self.cellSize))

                #save the currrent coordinates to a list. Saves the top left of each cell
                #if statement to avoid appending the same information to the list every update
                if self.gridCoordsApplied == False:
                    self.gridCoordinates.append([x,y])

                #draw the text for each cell at x,y adjusted for centre offset. Text value is the number that cell has been assigned
                qPainter.drawText(int((x+centeringOffset)),int((y+(self.cellSize/2)+centeringOffset)), str(self.numbersMatrix[j][i]))

                #draw the grid cell relative to the top left of the cell x,y. cellSize determines the height and width of a cell
                qPainter.drawRect(x, y, self.cellSize, self.cellSize)
        #Ensures gridcoordinates will not be added too
        self.gridCoordsApplied = True
        #colour cells
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



        #Prevent the next section from transforming when panning or zooming
        qPainter.resetTransform()

        #draw colour selector bar
        #itrate over the used colours
        for i in range(len(self.usedColours)):
            #if the current colour is not the selected colour draw colour selector bar with no selection
            if i != self.selectedColour:
                #set brush colour to the colour of current iteration
                qPainter.setBrush(QColor((self.usedColours[i][0]*255).astype(np.uint8), (self.usedColours[i][1]*255).astype(np.uint8), (self.usedColours[i][2]*255).astype(np.uint8)))

                #Draw cells
                qPainter.drawRect((i*(self.cellSize)), 0, self.cellSize, self.cellSize)

                #reset brush so text is black, then draw text into cell adjusted for centering
                qPainter.setBrush(Qt.BrushStyle.NoBrush)
                qPainter.drawText(20+(i*(self.cellSize)), 20, str(i+1))
            else:
                #if the selected cell is the current i value, draw the cell the same as above, but with a white box surrounding
                qPainter.setBrush(QColor((self.usedColours[i][0]*255).astype(np.uint8), (self.usedColours[i][1]*255).astype(np.uint8), (self.usedColours[i][2]*255).astype(np.uint8)))
                qPainter.setPen(QPen(QColor(255,255,255), 3))
                qPainter.drawRect((i*(self.cellSize)), 0, self.cellSize, self.cellSize)
                qPainter.setBrush(Qt.BrushStyle.NoBrush)
                qPainter.setPen(Qt.PenStyle.SolidLine)
                qPainter.drawText(20+(i*(self.cellSize)), 20, str(i+1))



    def mousePressEvent(self, event):
        start = time.time()
        #on right click, set the last mouse position to the current mouse position. Used for zoom and pan later
        if event.button() == Qt.MouseButton.RightButton:
            self.lastMousePos = event.pos()
        if event.button() == Qt.MouseButton.LeftButton:
            #on left click, set two positions for mouse. One adjusted for zoom and pan offsets. relative to the window rather than the canvas
            windowPos = event.position().toPoint()
            mousePos = (event.pos() - self.panOffset)/self.zoom

            #find the closest grid cell centre, this line iterates over the grid cells and compares them to the adjusted mouse position. Finding the closest centre of a cell
            minDistance = float('inf')  # Start with infinity so any distance is smaller
            closestPoint = [-1,-1]
            for coords in self.gridCoordinates:
                # find the center point of the current cell
                cellCenterX = (coords[0] + (self.cellSize / 2)) - mousePos.x()
                cellCenterY = (coords[1] + (self.cellSize / 2)) - mousePos.y()
                
                # Calculate actual straight-line distance
                distance = math.hypot(cellCenterX, cellCenterY)
                
                # Update if this cell is closer than the previous closest cell
                if distance < minDistance:
                    minDistance = distance
                    closestPoint = coords


            #if the mouse position relative to the window is greater than 50. Set the closest grid coordinate to the closest centre
            if windowPos.y() > 50:
                self.closestCoord = closestPoint   
                print(closestPoint)
            elif windowPos.y() < 50:
                #if the mouse position is less than 50, meaning the user is selecting a new colour as the colour selector cells are in the top 50 px
                #change selected colour to the colour of clicked cell
                print(windowPos.x())
                self.selectedColour = self.usedColours.index(self.usedColours[(int((windowPos.x())/(self.cellSize)))])
                self.closestCoord = closestPoint
                print("SelectedColour " + str(self.selectedColour))
                print("Drawn objects succesfully")

            #runs the paint event
            self.update()
        end = time.time()
        elapsed = end-start
        self.elapsedTimes.append([len(self.elapsedTimes),elapsed])

    #On mouse move
    def mouseMoveEvent(self, event):
            #pan the screen when the mouse is dragged
            delta = event.pos() - self.lastMousePos
            self.panOffset += delta
            self.lastMousePos = event.pos()

            #run paint event
            self.update()

    def wheelEvent(self, event):
        #on scroll wheel, zoom in and out by 1.1x
        if event.angleDelta().y() > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1
        self.update() 


#create app object and window object
app = QApplication(sys.argv)
window = NumbersGrid()
#show the windows
window.show()

#on exit of app, kill all traces
if not app.exec():
    with open("elapsedTimes.txt", "w", encoding="utf-8") as file:
        file.write(str(window.elapsedTimes))
    print(window.elapsedTimes)
    sys.exit()

#8x26 grid for timing tests

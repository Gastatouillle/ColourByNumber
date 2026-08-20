import kmeans
import matplotlib.pyplot as plt
import numpy as np
import sys

colourCount = 25

def GenerateNumberGrid():

    img_compressed = kmeans.readImage('compressed.png')
    pointsMatrix = img_compressed.reshape((-1, img_compressed.shape[2]))
    print(pointsMatrix)

    usedColours = []
    numbersMatrix = []
    usedCounter = 1

    #iterate over every pixel
    for i in range(len(pointsMatrix)):
            #if the colour of the pixel is not used
            if ([pointsMatrix[i][0], pointsMatrix[i][1], pointsMatrix[i][2]]) not in usedColours:
                #add that colour to usedcolours
                usedColours.append([pointsMatrix[i][0], pointsMatrix[i][1], pointsMatrix[i][2]])
                #assign that pixel the next number beginning at 1
                numbersMatrix.append(usedCounter)
                #increment used numbers by 1 so next unique colour is assigned next sequential number
                usedCounter += 1
                print("Found new match at px: " + str(i) + "  Colour: " + str([pointsMatrix[i][0], pointsMatrix[i][1], pointsMatrix[i][2]]))
            else:
                #If the number is not unique, find the number it was assigned and assign that number to the pixel
                numbersMatrix.append(usedColours.index(([pointsMatrix[i][0], pointsMatrix[i][1], pointsMatrix[i][2]])) + 1)

    print("Length of numbermatrix: " + str(len(numbersMatrix)))
    print("used colours:" + str(usedColours))
    print("UsedCounter: " + str(usedCounter))

    numbersMatrix = np.array(numbersMatrix).reshape(50, 50)
    return numbersMatrix, usedColours

def plotImages(numbersmatrix, img):
    fig, ax1 = plt.subplots()

    # Display the first image
    ax1.imshow(img)
    ax1.set_title('original')

    height, width = numbersmatrix.shape

    fontsize = max(1, min(12, 500 / max(width, height)))

    for y in range(height):
         for x in range(width):
            ax1.text(x, y, str(numbersmatrix[y, x]), ha="center", va="center", color="black", fontsize=fontsize)
            

    ax1.set_xticks([x - 0.5 for x in range(width + 1)], minor=True)
    ax1.set_yticks([y - 0.5 for y in range(height + 1)], minor=True)
    ax1.grid(which="minor")

    ax1.set_xticks([])
    ax1.set_yticks([])

    # Adjust layout spacing and show
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    plotImages(GenerateNumberGrid(), kmeans.readImage("compressed.png"))
import cv2 
import numpy as np
import matplotlib.pyplot as plt
import math

def readImage(image_path):
    #open image, resize contents, change colours to RGB

    img = cv2.imread(image_path)
    img = cv2.resize(img, (50, 50))

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    img = img/255.0

    return img


def initMeans(img, colour_count):
    #img.reshape moves all the data into specified shape from 3d RGB data, in this case a 2d matrix
    #Original (3D):  [100 rows] x [100 columns] x [3 channels]
    #Reshaped (2D):  [10,000 pixels] x [3 channels]
    pointsMatrix = img.reshape((-1, img.shape[2]))
    m, n = pointsMatrix.shape[:2]

    #np.zeroes creates colour_count row by n column array of zeroes
    means = np.zeros((colour_count, n))

    for i in range(colour_count):
        print("Initialising point:" + str(i))
        #create colour_count points in the array as centroids
        #m, size=10, replace=False. m chooses rows, size=10 selects 10 random rows, replace=false prevents the same index being selected twice
        randIndices = np.random.choice(m, size=10, replace=False)
        #Calculates the mean point of the generated 10 points, saves mean point at index i
        means[i] = np.mean(pointsMatrix[randIndices], axis=0)

    return pointsMatrix, means

def euclidDistance(x1, y1, x2, y2):
    #find distance between x1y1 and x2y2
    return math.dist((x1, y1), (x2, y2))

def kMeans(points, means, colour_count):
    #10 is placeholder, tune for ideal across data suite
    iterations = 10

    #creates an array of size = (n. of rows in points)
    index = np.zeros(points.shape[0])

    while iterations > 0:
        print(iterations)
        for j in range(points.shape[0]):
            minDist = math.inf

            for k in range(colour_count):
                x1, y1 = points[j, 0], points[j, 1]
                x2, y2, = means[k, 0], means[k, 1]

                dist = euclidDistance(x1, y1, x2, y2)

                if dist <= minDist:
                    minDist = dist
                    index[j] = k

        for k in range(colour_count):
            clusterPoints = points[index == k]
            if len(clusterPoints) > 0:
                means[k] = np.mean(clusterPoints, axis=0)

        iterations -= 1

    return means, index

def compressImage(means, index, img):
    centroid = np.array(means)

    #multiply by 255 and then convert to uint8 otherwise opencv saved a black image because all values are floats < 1
    recovered = (centroid[index.astype(int), :] * 255).astype('uint8')

    recovered = recovered.reshape(img.shape)

    #flip from rgb to brg because opencv is bgr
    recovered_for_saving = cv2.cvtColor(recovered, cv2.COLOR_RGB2BGR)
    cv2.imwrite('compressed.png', recovered_for_saving)

    return recovered

def plotImages(recovered, img):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Display the first image
    ax1.imshow(img)
    ax1.set_title('original')
    ax1.axis('off')  # Hide grid ticks and pixel borders

    # Display the second image
    ax2.imshow(recovered)
    ax2.set_title('compressed')
    ax2.axis('off')  # Hide grid ticks and pixel borders

    # Adjust layout spacing and show
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    img = readImage('images.png')

    colourCount= 25
    
    points, means = initMeans(img, colourCount)
    means, index = kMeans(points, means, colourCount)
    recovered = compressImage(means, index, img)

    plotImages(recovered, img)
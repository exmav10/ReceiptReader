import cv2
import numpy as np
import operator
import sys
import math

MIN_COUNTOUR_AREA = 5
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

class ContourWithData():
    npaContour = None
    boundingRect = None
    x = 0 # left X
    y = 0 # top y
    width = 0
    height = 0
    area = 0.0
    isNewLine = False
    isSpace = False

    def fillContourData(self):
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.x = intX
        self.y = intY
        self.width = intWidth
        self.height = intHeight

    # Looks contour area.
    def isContourValid(self): 
        if self.area < MIN_COUNTOUR_AREA: return False
        return True        

def main():
    try:
        classifications = np.loadtxt("classifications.txt", np.float32)
    except:
        print("Cannot Read Classifications") 
        sys.exit()
    
    try:
        flattenedImages = np.loadtxt("flattened.txt", np.float32)                 # read in training images
    except:
        print("Cannot Read Flattened Images") 
        sys.exit()
    
    classifications = classifications.reshape((classifications.size, 1)) # Classifications
    kNearest = cv2.ml.KNearest_create() # Create knearest element
    # traindata, responses, sampleidx
    kNearest.train(flattenedImages, cv2.ml.ROW_SAMPLE, classifications) # Train knearest element with classification and flattened images
    

    # TESTING PART
    validContoursWithData = []

    testingImage = cv2.imread('test_images/two_lines.png')
    if testingImage is None:
        print("Please Enter Valid Test Image")
        sys.exit()
        return
    # end if
    
    # Make image readeble
    imgGray = cv2.cvtColor(testingImage, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 0) # TODO: Learn (5,5) and 0
    imgThresh = cv2.adaptiveThreshold(imgBlur,                           # input image
                                      255,                                  # make pixels that pass the threshold full white
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
                                      cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
                                      2)                                    # constant subtracted from the mean or weighted mean
    imgThresh1 = imgThresh.copy() # Copy image, findcontours modifies it and we need the main image while finding imageROI
    # Segmentation is added for two part letters: i, ü, ö etc.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 15)) # Capital
    imgThresh1 = cv2.morphologyEx(imgThresh1, cv2.MORPH_CLOSE, rect_kernel)
    
    contours, hierarchy = cv2.findContours(imgThresh1, cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_SIMPLE) # compress horizontal, vertical, and diagonal segments and leave only their end points
    
    for npaContour in contours:
        contourWithData = ContourWithData()
        contourWithData.npaContour = npaContour
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)
        contourWithData.fillContourData()
        contourWithData.area = cv2.contourArea(contourWithData.npaContour)
        if contourWithData.isContourValid():
            validContoursWithData.append(contourWithData)
        # end if 
    # end for

    validContoursWithData.sort(key = operator.attrgetter("y"), reverse = False) 
    # End of main
    def sortingAlgorithm(): 
        didChanged = False
        for i in range(len(validContoursWithData) - 1 ):
            firstValue = validContoursWithData[i]
            secondValue = validContoursWithData[i+1]
            if (secondValue.y - firstValue.y <= 20):
                # they are in the same line, compare x values
                if firstValue.x > secondValue.x: # first value should be move right 
                    validContoursWithData[i] = secondValue
                    validContoursWithData[i+1] = firstValue
                    didChanged = True
        if didChanged:
            sortingAlgorithm()
            
    sortingAlgorithm()
    
    for i in range(len(validContoursWithData) - 1):
        firstValue = validContoursWithData[i]
        secondValue = validContoursWithData[i + 1]
        if firstValue.y + firstValue.height < secondValue.y: # Control for new line
            firstValue.isNewLine = True
        
        if firstValue.x + firstValue.width + 4 < secondValue.x:
            firstValue.isSpace = True

    finalText = ""
    for contourWithData in validContoursWithData:
        # Draw Rectangle
        cv2.rectangle(testingImage, 
                    (contourWithData.x, contourWithData.y), 
                    (contourWithData.x + contourWithData.width, contourWithData.y + contourWithData.height),
                    (0, 255, 0), # Color 
                    2) # Thickness 
        # crop char out of threshold image
        imgROI = imgThresh[contourWithData.y : contourWithData.y + contourWithData.height, 
                            contourWithData.x : contourWithData.x + contourWithData.width]
        # resize image, this will be more consistent for recognition and storage
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
        # flatten image into 1d numpy array
        npaRIOResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
        # convert from 1d numpy array of ints to 1d numpy array of floats
        npaRIOResized = np.float32(npaRIOResized)
        # call KNN function find_nearest
        # TODO: (AYDIN)
        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaRIOResized, k = 1)
        # get character from results
        strCurrentChar = str(chr(int(npaResults[0][0])))
        finalText = finalText + strCurrentChar
        if contourWithData.isSpace:
            finalText = finalText + " "
        if contourWithData.isNewLine:
            finalText = finalText + "\n"
    # end for
    print("\n" + finalText + "\n")
    cv2.imshow("Receipt Reader", testingImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return
    
    
if __name__ == "__main__":
    main()
# end if

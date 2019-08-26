import cv2
import numpy as np
import operator
import os

MIN_COUNTOUR_AREA = 15
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

class ContourWithData():
    npaContour = None
    boundingRect = None
    intRectX = 0
    intRectY = 0
    intRectWidth = 0
    intRectHeight = 0
    fltArea = 0.0

    def calculateRectTopLeftPoint(self):
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def isContourValid(self):
        if self.fltArea < MIN_COUNTOUR_AREA: return False
        return True

def main():
    
    allContoursWithData = []
    validContoursWithData = []

    try:
        classifications = np.loadtxt("classifications.txt", np.float32)
    except:
        print("Cannot Read Classifications \n") 
        os.system("pause")
        return
    
    try:
        flattenedImages = np.loadtxt("flattened.txt", np.float32)                 # read in training images
    except:
        print("Cannot Read Flattened Images \n") 
        os.system("pause")
        return
    
    classifications = classifications.reshape((classifications.size, 1))
    kNearest = cv2.ml.KNearest_create()
    kNearest.train(flattenedImages, cv2.ml.ROW_SAMPLE, classifications)
    testingImage = cv2.imread('letters.png')
    if testingImage is None:
        print("Cannot Open Testing Image")
        os.system("pause")
        return
    # end if
    
    imgGray = cv2.cvtColor(testingImage, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 0)
    imgThresh = cv2.adaptiveThreshold(imgBlur,                           # input image
                                      255,                                  # make pixels that pass the threshold full white
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
                                      cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
                                      2)                                    # constant subtracted from the mean or weighted mean
    imgThresh1 = imgThresh.copy()
    contours, hierarchy = cv2.findContours(imgThresh1,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE) # compress horizontal, vertical, and diagonal segments and leave only their end points
    
    for npaContour in contours:
        contourWithData = ContourWithData()
        contourWithData.npaContour = npaContour
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)
        contourWithData.calculateRectTopLeftPoint()
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)
        allContoursWithData.append(contourWithData)
    # end for

    for contourWithData in allContoursWithData:                 
        if contourWithData.isContourValid():
            validContoursWithData.append(contourWithData)
        # end if
    # end for

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))

    finalText = ""
    for contourWithData in validContoursWithData:
        cv2.rectangle(testingImage, 
                        (contourWithData.intRectX, contourWithData.intRectY), 
                        (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),
                        (0, 255, 0),
                        2)
        # crop char out of threshold image
        imgROI = imgThresh[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight, 
                            contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]
        # resize image, this will be more consistent for recognition and storage
        imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
        # flatten image into 1d numpy array
        npaRIOResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
        # convert from 1d numpy array of ints to 1d numpy array of floats
        npaRIOResized = np.float32(npaRIOResized)
        # call KNN function find_nearest
        retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaRIOResized, k = 1)
        # get character from results
        strCurrentChar = str(chr(int(npaResults[0][0])))
        finalText = finalText + strCurrentChar
    # end for
    print("\n" + finalText + "\n")
    cv2.imshow("testingImage", testingImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return
    # End of main

if __name__ == "__main__":
    main()
# end if

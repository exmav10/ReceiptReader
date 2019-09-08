# Inspired from https://github.com/MicrocontrollersAndMore/OpenCV_3_KNN_Character_Recognition_Python
# ş (351) => - (45)
# ı (305) => * (42)
# ğ (287) => < (60)
# : (58)  => q (113)

import cv2
import numpy as numpy
from matplotlib import pyplot as plt
import pytesseract as pyt
import numpy as np
from PIL import Image
import sys

MIN_COUNTOUR_AREA = 15
RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

def main():
    print(np.float32(105))
    originalImage = cv2.imread("training_chars.png")
    grayScaleImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY) # Grayscale
    # 5x5 Kernel (smoothing window, width - height), 0 sigma => sigma value, determines how much the image will be blurred, zero makes function chooses the sigma value
    blurImage = cv2.GaussianBlur(grayScaleImage, (5,5), 0) 
    # input image, 255 => make pixels that pass the threshold full white, THRESH_BINARY_INV => white foreground - black background
    thresholdImage = cv2.adaptiveThreshold(blurImage, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    thresholdImageCopy = thresholdImage
    # Segmentation is added for two part letters: i, ü, ö etc.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 12)) # points
    threshed = cv2.morphologyEx(thresholdImageCopy, cv2.MORPH_CLOSE, rect_kernel)
    # retr_external = gives outermost contours only, 
    contours, hierarchy = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # these are our training images, due to the data types that the KNN object KNearest requires, we have to declare a single Mat,
    # then append to it as though it's a vector, also we will have to perform some conversions before writing to file later
    npaFlattenedImages = np.empty((0, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
    intClassifications = [] # these are our training classifications, note we will have to perform some conversions before writing to file later
    intValidChars = [ord('0'), ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8'), ord('9'),
                     ord('A'), ord('B'), ord('C'), ord('Ç'), ord('D'), ord('E'), ord('F'), ord('G'), ord('Ğ'), ord('H'), ord('I'), ord('İ'),
                     ord('J'), ord('K'), ord('L'), ord('M'), ord('N'), ord('O'), ord('Ö'), ord('P'), ord('R'), ord('S'), ord('Ş'),
                     ord('T'),ord('U'), ord('Ü'), ord('V'), ord('Y'), ord('Z'),ord('a'), ord('b'), ord('c'), ord('ç'), ord('d'),
                     ord('e'), ord('f'), ord('g'), ord('ğ'), ord('h'), ord('ı'), ord('i'),
                     ord('j'), ord('k'), ord('l'), ord('m'), ord('n'), ord('o'), ord('ö'), ord('p'), ord('r'), ord('s'), ord('ş'),
                     ord('t'),ord('u'), ord('ü'), ord('v'), ord('y'), ord('z'), 
                     ord('.'), ord(','), ord('!'), ord('?'), ord(':'), ord(';'), ord('-'), ord('*'), ord('/'), ord('<'), ord('q')]
    for contour in contours:
        if cv2.contourArea(contour) > MIN_COUNTOUR_AREA:
            [intX, intY, intW, intH] = cv2.boundingRect(contour)
            cv2.rectangle(originalImage, (intX, intY), (intX + intW, intY + intH), (0,0,255), 2) # 2 thickness
            imgROI = thresholdImage[intY:intY+intH, intX:intX+intW]
            imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))
            cv2.imshow("Original Training Image", originalImage)
            intChar = cv2.waitKey(0)
            if intChar == 27: # esc
                sys.exit()
            elif intChar in intValidChars:
                intCharToSave = intChar
                if intChar == 45: # - => ş
                    intCharToSave = 351
                elif intChar == 42: # * => ı
                    intCharToSave = 305
                elif intChar == 60: # < => ğ
                    intCharToSave = 287
                elif intChar == 113: # q => :
                    intCharToSave = 58
                print("Char to save : " + str(intCharToSave) + " " + str(chr(intCharToSave)))
                intClassifications.append(intCharToSave)
                npaFlattenedImage = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))
                npaFlattenedImages = np.append(npaFlattenedImages, npaFlattenedImage, 0) # 0 puts new element in another row in matrix
                cv2.rectangle(originalImage, (intX, intY), (intX + intW, intY + intH), (0,255,0), 2)
            # end if
        # end if
    # end for
    fltClassifications = np.array(intClassifications, np.float32) # Convert int to float
    npaClassifications = fltClassifications.reshape((fltClassifications.size, 1))
    np.savetxt("classifications/altarikh_points.txt", npaClassifications)
    np.savetxt("flattened/altarikh_points.txt", npaFlattenedImages) 
    cv2.destroyAllWindows()
    return

if __name__ == "__main__":
    main()
# end if
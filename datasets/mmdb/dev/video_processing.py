import numpy as np
import copy
import cv2

cap = cv2.VideoCapture('teste1.avi')


ret, min_pixels = cap.read()
# Step1: find maximum of each pixel
while(cap.isOpened()):
    ret, new = cap.read()
    try:
        cv2.min(new, min_pixels, min_pixels)
    except:
        break



# Agora, preciso pre-processar esta imagem para usa-la depois como referencia
min_pixels = cv2.cvtColor(min_pixels, cv2.COLOR_BGR2GRAY)
min_pixels0 = copy.deepcopy(min_pixels)
minval, maxval, minloc, maxloc = cv2.minMaxLoc(min_pixels)
ret, min_pixels = cv2.threshold(min_pixels, minval+130, 255,\
        cv2.THRESH_BINARY_INV)

min_pixels = cv2.medianBlur(min_pixels,71)

contours, hierarchy = cv2.findContours(min_pixels, cv2.RETR_LIST,\
                     cv2.CHAIN_APPROX_NONE)
rectangle = cv2.minAreaRect(contours[0])
box = cv2.cv.BoxPoints(rectangle)
box = np.int0(box)
cv2.drawContours(min_pixels,[box],0,(255,255,255),2)

#keyboard = cv2.min_pixels0i(cv2.Rect(roiLeft,roiTop,roiWidth,roiHeight)).clone()


cap.release()
cv2.imshow('frame2',cv2.add(min_pixels,min_pixels0))

cv2.waitKey(10000)
exit()

# Step2: do actual processing
cap = cv2.VideoCapture('teste1.avi')
ret, gray = cap.read()
gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

while(cap.isOpened()):
    ret, new = cap.read()
    new = cv2.cvtColor(new, cv2.COLOR_BGR2GRAY)

    alpha = 1.0
    beta = 1 - alpha
    cv2.addWeighted( new, alpha, gray, beta, 0.0, gray)

    thresh = cv2.GaussianBlur(gray,(5,5),255)
    thresh = cv2.max(thresh, min_pixels)
    #thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)

    #:wthresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    #thresh = cv2.adaptiveThreshold(thresh,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
    #                 cv2.THRESH_BINARY,15,3)

    #ret, thresh = cv2.threshold(thresh,110,255,cv2.THRESH_BINARY_INV)

    cv2.imshow('frame',thresh)
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


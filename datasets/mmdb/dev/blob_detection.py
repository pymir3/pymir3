# This code snippet was taken from the video processing algorithm because it was
# not needed anymore. Nevertheless, it is a relevant piece of code for study
# purposes;
#Setup SimpleBlobDetector parameters.
params = cv2.SimpleBlobDetector_Params()
# Change thresholds
params.minThreshold = 100;
params.maxThreshold = 200;

# Filter by Area.
params.filterByArea = True
params.minArea = 15000
params.maxArea = 128000

# Filter by Circularity
params.filterByCircularity = False
#params.minCircularity = 0.1

# Filter by Convexity
params.filterByConvexity = False
#params.minConvexity = 0.0

# Filter by Inertia
params.filterByInertia = False
#params.maxInertiaRatio = 1.0

# Create a detector with the parameters
ver = (cv2.__version__).split('.')
if int(ver[0]) < 3 :
    detector = cv2.SimpleBlobDetector(params)
else :
    detector = cv2.SimpleBlobDetector_create(params)

keypoints = detector.detect(min_pixels)
im_with_keypoints = cv2.drawKeypoints(min_pixels, keypoints, np.array([]),\
        (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
cv2.imshow("Keypoints", im_with_keypoints)


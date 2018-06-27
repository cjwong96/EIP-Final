# import the necessary packages
import numpy as np

import cv2

class Stitcher:

	
	def is_cv3(self):
		# if we are using OpenCV 3.X, then our cv2.__version__ will start
		# with '3.'

			
		# return whether or not the current OpenCV version matches the
		# major version number
		return cv2.__version__.startswith("3.")
	



	def __init__(self):
		# determine if we are using OpenCV v3.X and initialize the
		# cached homography matrix
		self.isv3 = self.is_cv3()
		self.cachedH = None

	def stitch(self, images, ratio=0.75, reprojThresh=4.0,
		showMatches=False):
		# unpack the images, then detect keypoints and extract
		# local invariant descriptors from them
		try:
			(imageB, imageA) = images
			imageC = np.zeros((300, 800, 3), dtype=np.uint8)
			imageC[0:imageB.shape[0], 400:400+imageB.shape[1]] = imageA
			(kpsA, featuresA) = self.detectAndDescribe(imageC)
			(kpsB, featuresB) = self.detectAndDescribe(imageB)
			# match features between the two images
			print("get Feature")
			try:
				M = self.matchKeypoints(kpsB, kpsA,
					featuresB, featuresA, ratio, reprojThresh)
			except:
				return None
			(matches, H, status) = M
			result = cv2.warpPerspective(imageB, H,
				(imageA.shape[1] + imageB.shape[1], imageA.shape[0]))
			result[0:imageB.shape[0], 400:400+imageB.shape[1]] = imageA
			# check to see if the keypoint matches should be visualized
			if showMatches:
				vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches,
					status)

				# return a tuple of the stitched image and the
				# visualization
				return (result, vis)

			# return the stitched image
		except:
			result = None
		return result

	def detectAndDescribe(self, image):
		# convert the image to grayscale
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		# check to see if we are using OpenCV 3.X
		if self.isv3:
			# detect and extract features from the image
			descriptor = cv2.xfeatures2d.SIFT_create()
			(kps, features) = descriptor.detectAndCompute(image, None)

		# otherwise, we are using OpenCV 2.4.X
		else:
			# detect keypoints in the image
			detector = cv2.FeatureDetector_create("SIFT")
			kps = detector.detect(gray)

			# extract features from the image
			extractor = cv2.DescriptorExtractor_create("SIFT")
			(kps, features) = extractor.compute(gray, kps)

		# convert the keypoints from KeyPoint objects to NumPy
		# arrays
		kps = np.float32([kp.pt for kp in kps])

		# return a tuple of keypoints and features
		return (kps, features)

	def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB,
		ratio, reprojThresh):
		# compute the raw matches and initialize the list of actual
		# matches
		matcher = cv2.DescriptorMatcher_create("BruteForce")
		rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
		matches = []

		# loop over the raw matches
		for m in rawMatches:
			# ensure the distance is within a certain ratio of each
			# other (i.e. Lowe's ratio test)
			if len(m) == 2 and m[0].distance < m[1].distance * ratio:
				matches.append((m[0].trainIdx, m[0].queryIdx))

		# computing a homography requires at least 4 matches
		if len(matches) > 4:
			# construct the two sets of points
			ptsA = np.float32([kpsA[i] for (_, i) in matches])
			ptsB = np.float32([kpsB[i] for (i, _) in matches])

			# compute the homography between the two sets of points
			(H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
				reprojThresh)

			# return the matches along with the homograpy matrix
			# and status of each matched point
			return (matches, H, status)

		# otherwise, no homograpy could be computed
		return None
"""
This file detects the forgery using Noise and SIFT (#1 of the workflow).
To run the test, set absolute path of the image in the image_path variable
at line 110 and run the file.
We need OpenCV and scikit-learn for the process.

Run the file using the command:
> python test_forgery.py
"""
import sys
import math
import numpy as np

from PIL import Image
from scipy import signal
from sklearn.cluster import KMeans

from sklearn.cluster import DBSCAN
import numpy as np
import cv2
import re
from datetime import datetime


class DetectForgery(object):
    def __init__(self, input):
        self.image = cv2.imread(input)

    def siftDetector(self):
        sift = cv2.SIFT_create()
        # sift = cv2.xfeatures2d.SIFT_create()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.key_points, self.descriptors = sift.detectAndCompute(gray, None)
        return self.key_points, self.descriptors

    def showSiftFeatures(self):
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        sift_image = cv2.drawKeypoints(
            self.image, self.key_points, self.image.copy())
        return sift_image

    def locateForgery(self, eps=40, min_sample=2):
        # clusters = DBSCAN(eps=eps, min_samples=min_sample).fit(
        #     self.descriptors)
        print('descriptor shape:', self.descriptors.shape)
        print('key points shape:', len(self.key_points))
        clusters = DBSCAN(eps=120, min_samples=2).fit(
            self.descriptors)
        print('clusters:', clusters)
        print('cluster labels:', set(clusters.labels_))
        print('total clusters:', len(set(clusters.labels_)))

        number_of_clusters = len(set(clusters.labels_))
        number_of_keypoints = len(self.key_points)


        forgery = self.image.copy()
        anomaly_count = 0
        for idx in range(len(self.key_points)):
            if clusters.labels_[idx] == -1:
                anomaly_count += 1
                cv2.circle(forgery, (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1])),
                           3, (0, 0, 255), -1)
        # cv2.imshow('SIFT Keypoints', self.image)
        print('Anomaly count:', anomaly_count, 'out of', len(self.key_points))

        anomalous_ratio = anomaly_count / (number_of_keypoints * (number_of_clusters - 1 + 1e-8))
        non_anomalous_cluster_ratio = (number_of_clusters - 1) / (number_of_keypoints - anomaly_count + 1e-8)

        possible_forgery = anomalous_ratio / non_anomalous_cluster_ratio

        print('Anomalous ratio:', anomalous_ratio)
        print('Non-anomalous ratio:', non_anomalous_cluster_ratio)

        if possible_forgery > 0.25:
            print('Forgery score:', possible_forgery)
            print('Forgery Found!!')
        else:
            print('Forgery score:', possible_forgery)
            print('No Forgery Found!!')

        return forgery

        exit()
        size = np.unique(clusters.labels_).shape[0] - 1
        forgery = self.image.copy()
        if (size == 0) and (np.unique(clusters.labels_)[0] == -1):
            print('No Forgery Found!!')
            return None
        if size == 0:
            size = 1
        cluster_list = [[] for i in range(size)]
        for idx in range(len(self.key_points)):
            if clusters.labels_[idx] != -1:
                cluster_list[clusters.labels_[idx]].append(
                    (int(self.key_points[idx].pt[0]), int(self.key_points[idx].pt[1])))
        for points in cluster_list:
            if len(points) > 1:
                for idx1 in range(1, len(points)):
                    # Green color in BGR
                    cv2.line(forgery, points[0], points[idx1], (0, 255, 0), 5)
                    # cv2.line(forgery, points[0], points[idx1], (255, 0, 0), 5)
        return forgery


class DetectNoise(object):
    def __init__(self, input):
        self.input = input

    def estimate_noise(self, I):
        H, W = I.shape

        M = [[1, -2, 1], [-2, 4, -2], [1, -2, 1]]

        sigma = np.sum(np.sum(np.absolute(signal.convolve2d(I, M))))
        sigma = sigma * math.sqrt(0.5 * math.pi) / (6 * (W - 2) * (H - 2))

        return sigma

    def detect(self, blockSize=32):
        im = Image.open(self.input)
        im = im.convert('1')

        blocks = []

        imgwidth, imgheight = im.size

        # break up image into NxN blocks, N = blockSize
        for i in range(0, imgheight, blockSize):
            for j in range(0, imgwidth, blockSize):
                box = (j, i, j + blockSize, i + blockSize)
                b = im.crop(box)
                a = np.asarray(b).astype(int)
                blocks.append(a)

        variances = []
        for block in blocks:
            variances.append([self.estimate_noise(block)])

        kmeans = KMeans(n_clusters=2, random_state=0).fit(variances)
        center1, center2 = kmeans.cluster_centers_

        if abs(center1 - center2) > .4:
            return True
        else:
            return False


if __name__ == "__main__":
    # Load the image
    # image_path = r'C:/Work/id-match/source_files/passport/images/2.png'
    # image_path = r'C:/Work/id-match/source_files/id_cards/5.jpg'
    image_path = r'C:/Work/id-match/source_files/id_cards/7.png'
    # image_path = r'C:/Work/id-match/source_files/id_cards/8.jpg'
    noise_detector = DetectNoise(image_path)
    noise_forgery = noise_detector.detect()
    if(noise_forgery):
        print('\nNoise variance inconsistency detected')
    else:
        print('\nNo noise variance inconsistency detected')

    forgery_detector = DetectForgery(image_path)

    key_points, descriptors = forgery_detector.siftDetector()

    forgery = forgery_detector.locateForgery(60, 2)
    if forgery is None:
        sys.exit(0)
    cv2.imshow('Original image', forgery_detector.image)
    cv2.resizeWindow('Original image', 800, 600)
    cv2.imshow('Forgery', forgery)
    cv2.resizeWindow('Forgery', 800, 600)
    wait_time = 1000
    while(cv2.getWindowProperty('Forgery', 0) >= 0) or (cv2.getWindowProperty('Original image', 0) >= 0):
        keyCode = cv2.waitKey(wait_time)
        if (keyCode) == ord('q') or keyCode == ord('Q'):
            cv2.destroyAllWindows()
            break
        elif keyCode == ord('s') or keyCode == ord('S'):
            name = re.findall(r'(.+?)(\.[^.]*$|$)', image_path)
            date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
            new_file_name = name[0][0]+'_'+str(60)+'_'+str(2)
            new_file_name = new_file_name+'_'+date+name[0][1]

            vaue = cv2.imwrite(new_file_name, forgery)
            print('Image Saved as....', new_file_name)

    cv2.destroyAllWindows()
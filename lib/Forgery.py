import os
import torch
import numpy as np
from PIL import Image
from PIL import ImageChops
from PIL import ImageEnhance
from PIL.ExifTags import TAGS
from lib.ImageModels import IMDModel
import sys
import math

from PIL import Image
from scipy import signal
from sklearn.cluster import KMeans

from sklearn.cluster import DBSCAN
import cv2
import re
from datetime import datetime
from lib.Logging import Logging, log


class Forgery:
    def __init__(self, image):
        self.image = image
        self.key_points = None
        logging = Logging()

    def detect(self):
        """
        Detect forgery in the image using level 1 and level 2 tests.
        Level 1 test performs ELA and metadata analysis. Then runs the ELA through a pretrained model to detect forgery.
        Level 2 test performs noise detection and SIFT analysis.
        Finally, we combine the results of both tests giving 25% weight to level 1 and 75% to level 2.
        :return: boolean indicating if forgery is detected
        """
        level_1_score = 1 if self.level_1_test() else 0
        level_2_score = self.level_2_test()
        forgery_score = level_1_score * .25 + level_2_score * .75
        log(f'Forgery score: {forgery_score}', print_console=True)
        return forgery_score > 0.5


    def level_1_test(self):
        ela_test = ELATest(self.image)
        level_1_analysis = ela_test.infer()
        if level_1_analysis:
            log(f'Level 1 analysis detected forgery', print_console=True)
        else:
            log(f'Level 1 analysis did not detect forgery', print_console=True)
        return level_1_analysis

    def level_2_test(self):
        noise_detector = DetectNoise(self.image)
        noise_forgery = noise_detector.detect()
        if(noise_forgery):
            log(f'Level 2 analysis detected noise variance inconsistency', print_console=True)
        else:
            log(f'Level 2 analysis did not detect noise variance inconsistency', print_console=True)

        forgery_detector = SIFTTest(self.image)

        key_points, descriptors = forgery_detector.sift_detector()
        forgery = forgery_detector.forgery_score(120, 2)
        if forgery > 0.25:
            log(f'Level 2 analysis detected forgery with score of {forgery}', print_console=True)
        else:
            log(f'Level 2 analysis did not detect forgery with score of {forgery}', print_console=True)

        return (0.25 if noise_forgery else 0) + (0.75 if forgery > 0.25 else 0)



class ELATest:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(self.image_path)
        self.model_path = 'lib/model/model_im1.pth'
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = torch.load(self.model_path).to(self.device)
        # self.model = IMDModel()
        # self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        # self.model.to(self.device)

    def find_metadata(self):
        flag = 0
        try:
            info = self.image._getexif()
            for (tag, value) in info.items():
                if "Software" == TAGS.get(tag, tag):  # checking for software traces
                    log(f'Software Signature: {value}', print_console=True)
                    flag = 1
            if flag == 0:
                log(f'No Software Signature Found. Seems like real image...', print_console=True)

        except Exception as e:
            log(f'Failed to load metadata: {e}', print_console=True)

    def perform_ela(self):
        DIR = "temp/"
        TEMP = DIR + "temp.jpg"
        original = self.image.copy()

        if original.mode != 'RGB':
            original = original.convert('RGB')

        if (os.path.isdir(DIR) == False):
            os.mkdir(DIR)
        original.save(TEMP, quality=90)
        temporary = Image.open(TEMP)
        diff = ImageChops.difference(original, temporary)

        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        SCALE = 255.0 / max_diff

        diff = ImageEnhance.Brightness(diff).enhance(SCALE)

        # d = diff.load()
        # WIDTH, HEIGHT = diff.size
        # for x in range(WIDTH):
        #     for y in range(HEIGHT):
        #         d[x, y] = tuple(k * SCALE for k in d[x, y])

        diff.save(DIR + "ela_img.jpg")

    def infer(self):
        log('Performing metadata analysis...', print_console=True)
        self.find_metadata()

        log('Performing ELA analysis...', print_console=True)
        self.perform_ela()

        img = Image.open("temp/ela_img.jpg")
        img = img.resize((128, 128))
        img = np.array(img, dtype=np.float32).transpose(2, 0, 1) / 255.0
        img = np.expand_dims(img, axis=0)

        out = self.model(torch.from_numpy(img).to(device=self.device))
        y_pred = torch.max(out, dim=1)[1]
        log(f'Level 1 analysis result: {y_pred}', print_console=True)
        return True if y_pred else False


class SIFTTest():
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(self.image_path)

    def sift_detector(self):
        sift = cv2.SIFT_create()
        # sift = cv2.xfeatures2d.SIFT_create()
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        self.key_points, self.descriptors = sift.detectAndCompute(gray, None)
        return self.key_points, self.descriptors

    def show_sift_features(self):
        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        sift_image = cv2.drawKeypoints(
            self.image, self.key_points, self.image.copy())
        return sift_image

    def forgery_score(self, eps=120, min_sample=2):
        clusters = DBSCAN(eps=eps, min_samples=min_sample).fit(
            self.descriptors)

        number_of_clusters = len(set(clusters.labels_))
        number_of_keypoints = len(self.key_points)

        # forgery = self.image.copy()
        anomaly_count = 0
        for idx in range(len(self.key_points)):
            if clusters.labels_[idx] == -1:
                anomaly_count += 1

        anomalous_ratio = anomaly_count / (number_of_keypoints * (number_of_clusters - 1 + 1e-8))
        non_anomalous_cluster_ratio = (number_of_clusters - 1) / (number_of_keypoints - anomaly_count + 1e-8)

        possible_forgery = anomalous_ratio / non_anomalous_cluster_ratio

        if possible_forgery > 0.25:
            log(f'Possible forgery from level 2 analysis with a score of {possible_forgery}', print_console=True)
        else:
            log(f'No forgery detected from level 2 analysis with a score of {possible_forgery}', print_console=True)

        return possible_forgery


class DetectNoise():
    def __init__(self, image_path):
        self.image_path = image_path

    def estimate_noise(self, I):
        H, W = I.shape

        M = [[1, -2, 1], [-2, 4, -2], [1, -2, 1]]

        sigma = np.sum(np.sum(np.absolute(signal.convolve2d(I, M))))
        sigma = sigma * math.sqrt(0.5 * math.pi) / (6 * (W - 2) * (H - 2))

        return sigma

    def detect(self, blockSize=32):
        im = Image.open(self.image_path)
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

import cv2
from PIL import Image
import pytesseract
from pytesseract import Output
import re
import os
import math
import numpy as np

class PanCard():
    def __init__(self, config={'orient': True, 'skew': True, 'crop': True, 'contrast': True, 'psm': [3, 4, 6], 'mask_color': (0, 165, 255), 'brut_psm': [6]}):
        self.config = config

    def validate(self, panNum):
        if re.match("[A-Z]{5}[0-9]{4}[A-Z]", panNum):
            return True
        else:
            return False

    def extract(self, path):
        self.image_path = path
        self.read_image_cv()
        if self.config['orient']:
            self.cv_img = self.rotate(self.cv_img)

        if self.config['skew']:
            print("skewness correction not available")

        if self.config['crop']:
            print("Smart Crop not available")

        if self.config['contrast']:
            self.cv_img = self.contrast_image(self.cv_img)
            print("correcting contrast")

        pan_numbers = set()
        for i in range(len(self.config['psm'])):
            t = self.text_extractor(self.cv_img, self.config['psm'][i])
            pan = self.is_pan_card(t)
            if pan != "Not Found":
                pan_numbers.add(pan)

        return list(pan_numbers)

    def mask_image(self, path, write, pan_list):
        self.mask_count = 0
        self.mask = cv2.imread(str(path), cv2.IMREAD_COLOR)
        for j in range(len(self.config['psm'])):
            for i in range(len(pan_list)):
                if self.mask_pan(pan_list[i], write, self.config['psm'][j]) > 0:
                    self.mask_count += 1

        cv2.imwrite(write, self.mask)
        return self.mask_count

    def mask_pan(self, pan, out_path, psm):
        d = self.box_extractor(self.mask, psm)
        n_boxes = len(d['level'])
        color = self.config['mask_color']
        count_of_match = 0
        for i in range(n_boxes):
            string = d['text'][i].strip()
            if pan in string:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                cv2.rectangle(self.mask, (x, y), (x + w, y + h), color, cv2.FILLED)
                count_of_match += 1

        return count_of_match

    def read_image_cv(self):
        self.cv_img = cv2.imread(str(self.image_path), cv2.IMREAD_COLOR)

    def mask_nums(self, input_file, output_file):
        img = cv2.imread(str(input_file), cv2.IMREAD_COLOR)
        for i in range(len(self.config['brut_psm'])):
            d = self.box_extractor(img, self.config['brut_psm'][i])
            n_boxes = len(d['level'])
            color = self.config['mask_color']
            for i in range(n_boxes):
                string = d['text'][i].strip()
                if string.isdigit() and len(string) >= 1:
                    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, cv2.FILLED)

        cv2.imwrite(output_file, img)
        return "Done"

    def rotate_only(self, img, angle_in_degrees):
        rotated = ndimage.rotate(img, angle_in_degrees)
        return rotated

    def is_image_upside_down(self, img):
        face_locations = face_recognition.face_locations(img)
        encodings = face_recognition.face_encodings(img, face_locations)
        image_is_upside_down = (len(encodings) == 0)
        return image_is_upside_down

    def rotate(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_edges = cv2.Canny(img_gray, 100, 100, apertureSize=3)
        lines = cv2.HoughLinesP(img_edges, 1, math.pi / 180.0, 100, minLineLength=100, maxLineGap=5)
        angles = []
        for x1, y1, x2, y2 in lines[0]:
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            angles.append(angle)

        median_angle = np.median(angles)
        img_rotated = self.rotate_only(img, median_angle)
        if self.is_image_upside_down(img_rotated):
            img_rotated_final = self.rotate_only(img_rotated, -180)
            if self.is_image_upside_down(img_rotated_final):
                print("Kindly check the uploaded image, face encodings still not found!")
                return img_rotated
            else:
                print("image is now straight")
                return img_rotated_final
        else:
            print("image is straight")
            return img_rotated

    def contrast_image(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return thresh

    def text_extractor(self, img, psm):
        config = ('-l eng --oem 3 --psm ' + str(psm))
        t = pytesseract.image_to_string(img, lang='eng', config=config)
        return t

    def box_extractor(self, img, psm):
        config = ('-l eng --oem 3 --psm ' + str(psm))
        t = pytesseract.image_to_data(img, lang='eng', output_type=Output.DICT, config=config)
        return t

    def is_pan_card(self, text):
        match = re.search("[A-Z]{5}[0-9]{4}[A-Z]", text)
        if match:
            return match.group()
        else:
            return "Not Found"

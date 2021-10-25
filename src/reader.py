import os
from typing import Union

import cv2
import numpy as np

from utils import reader_utils
from utils.console import logger


class Reader:
    def __init__(self, n_rows: int, n_cols: int, debug: bool = False):
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.debug = debug

        self.new_size = (210 * 5, 297 * 5)
        warpH, warpW = 297 * 3, 210 * 3
        warpH = warpH - (warpH % n_rows)
        warpW = warpW - (warpW % n_cols)
        self.warp_size = (warpW, warpH)

    def read(self, filename: Union[str, bytes, os.PathLike]) -> Union[np.ndarray, str]:
        if not self.file_exists(filename):
            logger.critical(f'File "{filename}" does not exists.')
            return f'File "{filename}" does not exists.'

        # Read image then preprocess
        imgOrig = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
        imgOrig = cv2.resize(imgOrig, self.new_size)
        imgGray = cv2.cvtColor(imgOrig, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
        imgCanny = cv2.Canny(imgBlur, 10, 50)

        # Find contours, the biggest one is the question's box
        contours, _ = cv2.findContours(
            imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
        )
        rectCon = reader_utils.rectContour(contours, min_area=500)
        questionBox = reader_utils.getCornerPoints(rectCon[0])

        if questionBox.size == 0:
            logger.error(f'Error finding question box for image "{filename}".')
            return f"Error finding question box."

        # Warp the box in case it is not straight
        box = reader_utils.reorder(questionBox)
        pts1 = np.float32(box)
        pts2 = np.float32(
            [[0, 0], [self.warp_size[0], 0], [0, self.warp_size[1]], [*self.warp_size]]
        )
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarped = cv2.warpPerspective(imgGray, matrix, self.warp_size)

        # Apply thresholding to the image
        mean = np.mean(imgWarped) - 10
        imgThresh = cv2.threshold(imgWarped, mean, 255, cv2.THRESH_BINARY_INV)[1]

        boxes = reader_utils.splitBoxes(imgThresh, self.n_rows, self.n_cols)
        scores = np.zeros((self.n_rows, self.n_cols), dtype=int)
        pixVal = np.zeros((self.n_rows, self.n_cols), dtype=int)

        for i, row in enumerate(boxes):
            for j, col in enumerate(row):
                blackened = cv2.countNonZero(col)
                scores[i, j] = 1 if blackened >= 300 else 0
                pixVal[i, j] = blackened

        if self.debug:
            imgCont = imgOrig.copy()
            cv2.drawContours(imgCont, rectCon, -1, (0, 255, 0), 3)
            reader_utils.showImages(
                [imgOrig, imgBlur, imgCanny, imgCont],
                titles=["Original", "Blur", "Canny", "Contour"],
                nrow=1,
            )
            reader_utils.showImages([imgWarped, imgThresh])
            logger.debug(scores)
            logger.debug(pixVal)

        return scores

    @staticmethod
    def file_exists(filename: Union[str, bytes, os.PathLike]) -> bool:
        return os.path.exists(filename)

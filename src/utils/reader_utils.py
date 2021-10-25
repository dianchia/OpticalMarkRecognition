import math
from typing import List, Union

import cv2
import matplotlib.pyplot as plt
import numpy as np

from console import logger


def reorder(points: np.ndarray) -> np.ndarray:
    points = np.reshape(points, (4, 2))
    newpoints = np.zeros((4, 1, 2), np.int32)

    add = np.sum(points, axis=1)
    newpoints[0] = points[np.argmin(add)]
    newpoints[3] = points[np.argmax(add)]

    diff = np.diff(points, axis=1)
    newpoints[1] = points[np.argmin(diff)]
    newpoints[2] = points[np.argmax(diff)]
    return newpoints


def rectContour(contours: List[np.ndarray], min_area: int = 500) -> List[np.ndarray]:
    rectCon = []

    for contour in contours:
        approx = getCornerPoints(contour)
        if len(approx) == 4 and cv2.contourArea(contour) >= min_area:
            rectCon.append(contour)

    rectCon = sorted(rectCon, key=cv2.contourArea, reverse=True)
    return rectCon


def getCornerPoints(contour: np.ndarray) -> np.ndarray:
    peri = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
    return approx


def splitBoxes(img: np.ndarray, n_row: int, n_col: int) -> np.ndarray:
    try:
        rows = np.vsplit(img, n_row)
        boxes = []
        for row in rows:
            cols = np.hsplit(row, n_col)
            boxes.append(cols)
    except ValueError as e:
        logger.exception(e)
        boxes = np.zeros((n_row, n_col))

    return np.array(boxes)


def drawGrid(img: np.ndarray, questions: int = 5, choices: int = 5) -> np.ndarray:
    secW = int(img.shape[1] / questions)
    secH = int(img.shape[0] / choices)
    for i in range(0, 9):
        pt1 = (0, secH * i)
        pt2 = (img.shape[1], secH * i)
        pt3 = (secW * i, 0)
        pt4 = (secW * i, 0)
        cv2.line(img, pt1, pt2, (255, 255, 0), 2)
        cv2.line(img, pt3, pt4, (255, 255, 0), 2)

    return img


def stackImg(imgs: List[np.ndarray]) -> Union[None, np.ndarray]:
    stacked = []

    for img in imgs:
        if len(img.shape) not in [2, 3]:
            logger.exception(
                f"Does not support image with {len(img.shape)} channels."
                f"Only image with 2 or 3 channels is supported"
            )
            return None
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        stacked.append(img)
    stacked = np.hstack(stacked)

    return stacked


def showImages(
    imgs: List[np.ndarray],
    titles: Union[List[str], None] = None,
    ncol: Union[int, None] = None,
    nrow: Union[int, None] = None,
) -> None:
    imgCount = len(imgs)
    if titles:
        assert imgCount == len(titles), logger.error(
            "Number of images and number of titles is not the same."
        )

    if ncol is None and nrow is None:
        ncol = math.ceil(math.sqrt(imgCount))
        nrow = math.ceil(imgCount / ncol)
    elif ncol is None and nrow is not None:
        ncol = math.ceil(imgCount / nrow)
    elif nrow is None and ncol is not None:
        nrow = math.ceil(imgCount / ncol)

    for idx, img in enumerate(imgs, start=1):
        plt.subplot(nrow, ncol, idx)
        cmap = "gray" if len(img.shape) == 2 else "viridis"
        plt.imshow(img, cmap=cmap)
        plt.axis("off")
        if titles:
            plt.title(titles[idx - 1])

    mng = plt.get_current_fig_manager()
    mng.window.state("zoomed")
    plt.tight_layout(w_pad=0)
    plt.show()

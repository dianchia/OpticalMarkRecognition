import argparse
import os
from typing import Union

import numpy as np

from utils.console import logger
from reader import Reader


class IMKReader:
    def __init__(self):
        self.reader = Reader(n_rows=32, n_cols=23, debug=False)
        self.drop_col = [0, 3, 4, 7, 8, 11, 12, 15, 16, 19, 20]
        self.drop_row = [10, 21]
        self.template_dict = {
            "REALISTIK": 0,
            "INVESTIGTIF": 0,
            "ARTISTIK": 0,
            "SOSIAL": 0,
            "ENTERPRISING": 0,
            "KONVENSIONAL": 0,
            "REKOD": 0,
            "CATATAN": "",
        }

    def read_single_file(self, filename: Union[str, bytes, os.PathLike]) -> dict:
        template_dict = self.template_dict.copy()
        answer = self.reader.read(filename)

        if isinstance(answer, str):
            template_dict.update(CATATAN=answer)
            return template_dict

        answer = np.delete(answer, self.drop_col, axis=1)
        answer = np.delete(answer, self.drop_row, axis=0)
        scores = np.zeros((30, 6), dtype=int)
        no_answer = []
        two_answer = []

        for idx_row, row in enumerate(answer, start=1):
            pairs = np.hsplit(row, 6)
            for idx_col, pair in enumerate(pairs):
                question_num = (50 * ((idx_row - 1) // 10)) + (idx_col * 10) + idx_row
                if sum(pair) == 0:
                    logger.info(
                        f"Question {question_num} has no answer or answer is unreadable."
                    )
                    no_answer.append(question_num)
                elif sum(pair) == 2:
                    logger.info(
                        f"Question {question_num} has two answer or answer is unreadable."
                    )
                    two_answer.append(question_num)
                else:
                    scores[idx_row - 1, idx_col] = np.argmax(pair) ^ 1

        scores = np.sum(scores, axis=0)

        for key, score in zip(template_dict.keys(), scores):
            template_dict[key] = score

        if len(no_answer) > 0:
            no_answer = map(lambda x: str(x), no_answer)
            template_dict[
                "CATATAN"
            ] += f'Question {", ".join(no_answer)} has no answer.\n'

        if len(two_answer) > 0:
            two_answer = map(lambda x: str(x), two_answer)
            template_dict[
                "CATATAN"
            ] += f'Question {", ".join(two_answer)} has no answer.\n'

        template_dict.update(REKOD=1)

        return template_dict


class IKKReader:
    def __init__(self):
        raise NotImplemented
        # self.reader = Reader(n_rows=32, n_cols=23, debug=False)

    # def read_single_file(
    #     self, filename: Union[str, bytes, os.PathLike]
    # ) -> Union[np.ndarray, None]:
    #     answer = self.reader.read(filename)
    #     logger.debug(answer)
    #
    #     return None


class IKPReader:
    def __init__(self):
        raise NotImplemented
        # self.reader = Reader(n_rows=32, n_cols=23, debug=False)

    # def read_single_file(
    #     self, filename: Union[str, bytes, os.PathLike]
    # ) -> Union[np.ndarray, None]:
    #     answer = self.reader.read(filename)
    #     logger.debug(answer)
    #
    #     return None


def type_path(path: str):
    if os.path.exists(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f'"{path}" does not exists.')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--paper",
        type=str.upper,
        choices=["IKK", "IKP", "IMK"],
        required=True,
        help="Types of paper",
    )
    parser.add_argument(
        "--path", type=str, required=True, help="Path to image or directory of images"
    )
    args = parser.parse_args()
    return args


def get_path_type(path: str) -> str:
    if os.path.isfile(path):
        return "file"
    else:
        return "dir"


def main() -> None:
    args = parse_args()

    path_type = get_path_type(args.path)

    if args.paper == "IMK":
        reader = IMKReader()
    elif args.paper == "IKK":
        reader = IKKReader()
    else:
        reader = IKPReader()

    if path_type == "file":
        scores = reader.read_single_file(args.path)
        logger.info(scores)


if __name__ == "__main__":
    main()

import pandas as pd
from typing import Union
from pathlib import Path
import os

from utils.console import logger


def validate_path(
    path: Union[str, bytes, os.PathLike, Path], create_on_missing: bool = False
) -> bool:
    if not isinstance(path, Path):
        path = Path(path)
    if not path.exists():
        if not create_on_missing:
            logger.error(f"{path} not found.")
            return False
        logger.info(f"Creating {path}.")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as _:
            pass
        return True
    return True


def read_imk(
    input_path: Union[str, bytes, os.PathLike],
    output_path: Union[str, bytes, os.PathLike],
):
    if not validate_path(input_path):
        return
    validate_path(output_path, create_on_missing=True)

    RIASEK = [
        "REALISTIK",
        "INVESTIGATIF",
        "ARTISTIK",
        "SOSIAL",
        "ENTERPRISING",
        "KONVENSIONAL",
    ]
    COLUMNS = ["NAMA", "TINGKATAN", "KELAS", "NO. KAD PENGENALAN"] + RIASEK
    RANKING = ["1st", "2nd", "3rd"]
    KOD_HOLLANDS = ["KOD HOLLAND 1", "KOD HOLLAND 2", "KOD HOLLAND 3"]

    df = pd.read_excel(input_path, dtype={"NO. KAD PENGENALAN": str, "TINGKATAN": str})
    df = df[COLUMNS]
    df = df.dropna()
    f = df["NO. KAD PENGENALAN"].str.contains("[0-9]{12}")
    df = df[f]

    df[RANKING] = [row.nlargest(3).values for _, row in df[RIASEK].iterrows()]
    df[KOD_HOLLANDS] = [
        row.nlargest(3).index.values for _, row in df[RIASEK].iterrows()
    ]
    for KH in KOD_HOLLANDS:
        df[KH] = df[KH].str[0]
    df["INDEX PERBEZAAN"] = df[RIASEK].max(axis=1) - df[RIASEK].min(axis=1)
    df = df[COLUMNS + ["INDEX PERBEZAAN"] + RANKING + KOD_HOLLANDS]

    with pd.ExcelWriter(output_path) as writer:
        df.to_excel(writer, sheet_name="IMK", index=False)


def read_ikp(
    input_path: Union[str, bytes, os.PathLike],
    output_path: Union[str, bytes, os.PathLike],
):
    if not validate_path(input_path):
        return
    validate_path(output_path, create_on_missing=True)

    COLUMNS = ["NAMA", "TINGKATAN", "NO. KAD PENGENALAN"]
    PAPER1_FIELD = [
        "VERBAL LINGUISTIK (BM)",
        "VERBAL LINGUISTIK (BI)",
        "LOGIK MATEMATIK",
        "VISUAL RUANG 1",
    ]
    PAPER2_FIELD = [
        "(+) VISUAL RUANG2",
        "MUZIK",
        "NATURALIS",
        "INTRAPESONAL",
        "INTERPESONAL",
        "KINESTATIK",
        "EKSISTENTIAL",
    ]
    COMBINED_FIELD = PAPER1_FIELD[:-1] + ["VISUAL RUANG"] + PAPER2_FIELD[1:]

    def fn(s):
        s = str(s)
        if not s.startswith("0"):
            return "0" + s

    paper1: pd.DataFrame = pd.read_excel(
        input_path, sheet_name="IKP(1)", converters={"NO. KAD PENGENALAN": fn}
    )
    paper2: pd.DataFrame = pd.read_excel(
        input_path, sheet_name="IKP(2)", converters={"NO. KAD PENGENALAN": fn}
    )
    paper1 = paper1[COLUMNS + PAPER1_FIELD]
    paper2 = paper2[COLUMNS + PAPER2_FIELD]

    paper1.dropna(inplace=True)
    paper2.dropna(inplace=True)
    logger.info(f"Number of student answered paper 1: {len(paper1)}")
    logger.info(f"Number of student answered paper 2: {len(paper2)}")

    dup1 = paper1[paper1.duplicated(subset=["NO. KAD PENGENALAN"], keep=False)]
    dup2 = paper2[paper2.duplicated(subset=["NO. KAD PENGENALAN"], keep=False)]
    if not dup1.empty:
        logger.warning(f"{len(dup1)} duplicates found in paper 1")
        logger.info(dup1[COLUMNS].sort_values("NO. KAD PENGENALAN"))
        paper1.drop_duplicates(subset=["NO. KAD PENGENALAN"], inplace=True)
        logger.info(
            f"Number of student answered paper 1 after removing duplicates: {len(paper1)}"
        )
    if not dup2.empty:
        logger.warning(f"{len(dup2)} duplicates found in paper 2")
        logger.info(dup2[COLUMNS].sort_values("NO. KAD PENGENALAN"))
        paper2.drop_duplicates(subset=["NO. KAD PENGENALAN"], inplace=True)
        logger.info(
            f"Number of student answered paper 2 after removing duplicates: {len(paper2)}"
        )

    df = paper1.merge(paper2, on=["NO. KAD PENGENALAN"], validate="1:1")
    df.drop(["NAMA_y", "TINGKATAN_y"], axis=1, inplace=True)
    df.rename(columns={"NAMA_x": "NAMA", "TINGKATAN_x": "TINGKATAN"}, inplace=True)
    logger.info(f"Number of student answered paper 1 and 2: {len(df)}")

    df["VISUAL RUANG"] = df["VISUAL RUANG 1"] + df["(+) VISUAL RUANG2"]
    df.drop(["VISUAL RUANG 1", "(+) VISUAL RUANG2"], axis=1, inplace=True)
    df[COMBINED_FIELD] = df[COMBINED_FIELD].apply(lambda x: x * 100).astype("uint8")

    df.to_excel(output_path, index=False)


def main():
    # read_imk('../input/excel/IMK 2021 RESPON.xlsx', '../output/excel/IMK_2021.xlsx')
    read_ikp("../input/excel/IKP 2021 RESPON.xlsx", "../output/excel/IKP_2021.xlsx")


if __name__ == "__main__":
    main()

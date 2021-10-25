import pandas as pd

from utils import create_session, fix_ic


def upload(df: pd.DataFrame):
    pass


def main():
    session = create_session()
    lnk_df = pd.read_csv("../data/database/student_links.csv", index_col="ID")
    inp_df: pd.DataFrame = pd.read_excel(
        "../input/excel/IMK 2021 RESPON.xlsx", converters={"NO. KAD PENGENALAN": fix_ic}
    )
    inp_df.dropna(
        axis=0,
        how="any",
        subset=["NAMA", "TINGKATAN", "NO. KAD PENGENALAN"],
        inplace=True,
    )
    ESSENTIAL_COL = ["NAMA", "NO. KAD PENGENALAN"]
    IMK_COL = [
        "REALISTIK",
        "INVESTIGATIF",
        "ARTISTIK",
        "SOSIAL",
        "ENTERPRISING",
        "KONVENSIONAL",
    ]
    inp_df = inp_df[ESSENTIAL_COL + IMK_COL]
    student: pd.Series = inp_df.iloc[0]
    data = {
        "txtIDMurid": 7614477,
        "txtIDimk": 3424739,
        "txtTimk": "01-03-2019",
        "txtHol1": "R",
        "txtMark1": 18,
        "txtHol2": "I",
        "txtMark2": 27,
        "txtHol3": "A",
        "txtMark3": 23,
        "txtHol4": "S",
        "txtMark4": 21,
        "txtHol5": "E",
        "txtMark5": 20,
        "txtHol6": "K",
        "txtMark6": 26,
        "btnKemasIMK": "Kemaskini+Rekod",
    }
    session.post(
        "https://epkm.moe.gov.my//murid/k_imk_murid.php?idmurid=7614477&idimk=3424739",
        data=data,
    )


if __name__ == "__main__":
    main()

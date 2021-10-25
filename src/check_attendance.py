import itertools
import os
import sys
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from streamlit import cli as stcli

from utils import fix_ic, forms2int, validate_name


INV_MAPPINGS = {
    "IMK": ["1", "3"],
    "IKP": ["3"],
    "ITP 1": ["1"],
    "ITP 4": ["4"],
}


def pie_label(pct, allvals):
    absolute = int(round(pct / 100.0 * np.sum(allvals)))
    return absolute


@st.cache(allow_output_mutation=True)
def load_main_df(df_main, inv_type: str) -> pd.DataFrame:
    filters = "|".join(INV_MAPPINGS[inv_type])
    df_main = pd.read_excel(
        df_main,
        converters={
            "Keterangan Tingkatan Tahun": forms2int,
            "No. KP": fix_ic,
            "No. Tel Bimbit Penjaga 1": str,
            "No. Tel Bimbit Penjaga 2": str,
        },
    )
    df_main = df_main[df_main["Keterangan Tingkatan Tahun"].str.contains(filters)]
    return df_main


@st.cache
def load_attendance_df(df_attendance, inv_type: str) -> pd.DataFrame:
    df_attendance: pd.DataFrame = pd.read_excel(
        df_attendance,
        converters={"NO. KAD PENGENALAN": fix_ic},
    )
    df_attendance.dropna(
        axis=0,
        how="any",
        subset=["NAMA", "TINGKATAN", "NO. KAD PENGENALAN"],
        inplace=True,
    )
    df_attendance = validate_name(df_attendance)
    return df_attendance


@st.cache
def filter_df(df: pd.DataFrame, s: str):
    filters = "|".join(INV_MAPPINGS[s])
    df = df[df["Keterangan Tingkatan Tahun"].str.contains(filters)]
    return df


def main():
    st.set_page_config(layout="wide")
    st.markdown("<h3>Sila pilih jenis inventori </h3>", unsafe_allow_html=True)
    inv_type = st.selectbox("", INV_MAPPINGS.keys(), key="inv_type")

    col1, col2 = st.columns(2)
    col1.markdown(
        "<h3>Sila pilih Excel yang anda muat turun dari APDM</h3>",
        unsafe_allow_html=True,
    )
    col2.markdown(
        f"<h3>Sila pilih Excel yang mengandungi senarai nama murid yang sudah jawap {inv_type}</h3>",
        unsafe_allow_html=True,
    )
    df_main = col1.file_uploader("", type=["xls", "xlsx"], key="df_main")
    df_attendance = col2.file_uploader("", type=["xls", "xlsx"], key="df_attendance")

    if df_main is None or df_attendance is None:
        st.stop()

    df_main = load_main_df(df_main, inv_type)
    df_attendance = load_attendance_df(df_attendance, inv_type)

    df_main["ADA NAMA"] = df_main["Nama"].isin(df_attendance["NAMA"])
    df_main["ADA KP"] = df_main["No. KP"].isin(df_attendance["NO. KAD PENGENALAN"])
    df_main["JAWAP"] = df_main["ADA NAMA"] | df_main["ADA KP"]
    df_main.drop(["ADA NAMA", "ADA KP"], axis=1, inplace=True)

    forms = df_main["Keterangan Tingkatan Tahun"].unique()
    forms.sort()
    classes = df_main["Nama Kelas"].unique()
    classes.sort()

    selected_forms = st.selectbox("Tingkatan", forms)
    selected_classes = st.multiselect("Kelas", classes, default=classes)
    selected_classes.sort()
    selected_classes = "|".join(selected_classes)

    df_filtered = df_main[df_main["Nama Kelas"].str.contains(selected_classes)]
    df_filtered = df_filtered[
        df_filtered["Keterangan Tingkatan Tahun"].str.contains(selected_forms)
    ]

    df_show = df_filtered[~df_filtered.JAWAP].sort_values("Nama Kelas")
    df_show = df_show.reset_index(drop=True)
    st.dataframe(df_show, height=540)
    st.markdown(
        f"<h5>Jumlah murid yang belum jawap: {len(df_show)}</h5>",
        unsafe_allow_html=True,
    )

    if st.button("Muat Turun Untuk Sendiri"):
        outputfile = f"./{inv_type}_{datetime.now().year}.xlsx"
        with pd.ExcelWriter(outputfile) as writer:
            df_show.to_excel(writer, index=False)
        st.success(f"Telah muat turun di {os.path.abspath(outputfile)}")

    cols = itertools.cycle(st.columns(4))
    for cls in selected_classes.split("|"):
        df_tmp = df_filtered[df_filtered["Nama Kelas"].str.contains(cls)]
        present = df_tmp.JAWAP.eq(True).astype(int).sum()
        absent = df_tmp.JAWAP.eq(False).astype(int).sum()
        fig, ax = plt.subplots()
        plt.title(f"{selected_forms} {cls}")
        ax.axis("equal")
        ax.pie(
            [present, absent],
            labels=["Dah Jawap", "Belum Jawap"],
            autopct=lambda pct: pie_label(pct, [present, absent]),
            startangle=90,
            colors=["#4daf4a", "#e41a1c"],
        )
        next(cols).pyplot(fig)


if __name__ == "__main__":
    if st._is_running_with_streamlit:
        main()
    else:
        sys.argv = ["streamlit", "run", sys.argv[0]]
        sys.exit(stcli.main())

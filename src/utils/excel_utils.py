import pandas as pd


S2I_MAPPINGS = {
    "KELAS KHAS MENENGAH": "0",
    "TINGKATAN SATU": "1",
    "TINGKATAN DUA": "2",
    "TINGKATAN TIGA": "3",
    "TINGKATAN EMPAT": "4",
    "TINGKATAN LIMA": "5",
}


def fix_ic(ic: int):
    try:
        ic = str(ic)
        if ic[0] != "0":
            ic = "0" + ic
        return ic
    except IndexError:
        return pd.NA


def forms2int(s: str):
    return S2I_MAPPINGS[s]


def validate_name(inp_df: pd.DataFrame) -> pd.DataFrame:
    ref_df = pd.read_excel(
        "../../data/database/v2018_muatturun_BEA7619-6.xls",
        converters={
            "Keterangan Tingkatan Tahun": forms2int,
            "No. KP": fix_ic,
            "No. Tel Bimbit Penjaga 1": str,
            "No. Tel Bimbit Penjaga 2": str,
        },
    )

    ref_df_renamed = ref_df[["Nama", "No. KP"]].rename(columns={"Nama": "NAMA"})
    inp_df_renamed = inp_df[["NAMA", "NO. KAD PENGENALAN"]].rename(
        columns={"NO. KAD PENGENALAN": "No. KP"}
    )

    # Fix name base on No. KP
    inp_df_reindexed = inp_df_renamed.set_index("No. KP")
    ref_df_reindexed = ref_df_renamed.set_index("No. KP")
    inp_df_reindexed.update(ref_df_reindexed)
    inp_df_reindexed.reset_index(inplace=True)
    inp_df["NAMA"] = inp_df_reindexed["NAMA"]

    return inp_df

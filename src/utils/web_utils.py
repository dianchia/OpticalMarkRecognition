import os
from typing import Optional

import requests
from dotenv import load_dotenv

from .console import logger


def init_user():
    unm = input("Sila masukkan nama pengguna SEPKM: ")
    pwd = input("Sila masukkan kata laluan: ")
    with open("../.env", "w") as f:
        f.write(f"namapengguna={unm}\nkatalaluan={pwd}")


def create_session() -> Optional[requests.Session]:
    if not os.path.exists(".env"):
        init_user()
    load_dotenv(".env")
    session = requests.Session()
    login_data = {
        "txtuser": os.environ["namapengguna"],
        "txtpass": os.environ["katalaluan"],
        "sbtMasuk": "MASUK",
    }

    resp = session.post(
        "https://epkm.moe.gov.my/guru/proses.php", data=login_data, verify=False
    )
    if resp.status_code == 200:
        logger.info("Telah berjaya log masuk ke SEPKM.")
        return session

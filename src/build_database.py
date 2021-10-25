import re

import pandas as pd
from bs4 import BeautifulSoup
from rich.progress import track

from utils import create_session


def main():
    url_index = "https://epkm.moe.gov.my/guru/index.php"
    session = create_session()
    html = session.get(f"{url_index}?page=3")
    soup = BeautifulSoup(html.text, "html.parser")
    pages = soup.find_all("a", href=re.compile(r"start=\d*"))
    pages = [page["href"] for page in pages]

    link_pattrn = re.compile("idmurid")
    full_links = []
    for page in track(pages):
        resp = session.get(f"{url_index}{page}")
        soup = BeautifulSoup(resp.text, "html.parser")
        links = soup.find_all("a", href=link_pattrn)
        full_links.extend([link["href"] for link in links])
    full_links = list(set(full_links))

    df = []
    sid_pattrn = re.compile(r"idmurid=(\d*)")

    for link in full_links:
        sid = sid_pattrn.search(link).group(1)
        df.append({"ID": int(sid), "link": link})
    df = pd.DataFrame(df, columns=["ID", "link"])
    df.sort_values(by="ID", inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.to_csv("../data/database/student_links.csv", index=False)


if __name__ == "__main__":
    main()

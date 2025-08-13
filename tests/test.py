import os
import sys

from app.clients.moviepilot import CMoviePilotClient
from app.clients.qbittorrent import CQbittorrentClient
from app.common.config import MP_PASS, MP_URL, MP_USER, QB_PASS, QB_URL, QB_USER

# sys.path.insert(
#     0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# )


def main():
    client = CMoviePilotClient(base_url=MP_URL, user=MP_USER, password=MP_PASS)
    # response = client.query_transfer_history("仙逆 - S01E19 - 第 19 集.mkv")
    # client.extract_srcname_from_response_by_name(
    #     response=response, target_name="仙逆 - S01E19 - 第 19 集.mkv"
    # )
    # print(src_name)
    destName: list[str] = [
        "利剑·玫瑰 - S01E01 - 第 1 集.mp4",
        "仙逆 - S01E30 - 第 30 集.mp4",
        "仙逆 - S01E28 - 第 28 集.mp4",
    ]
    srcName: list[str] = []
    client.delete_transfer_history_by_name(destName, srcName)

    print(srcName)
    qbittorrent = CQbittorrentClient(
        base_url=QB_URL, user=QB_USER, password=QB_PASS
    )

    for filename in srcName:
        print(filename)
        qbittorrent.delete_torrents(filename)


if __name__ == "__main__":
    main()

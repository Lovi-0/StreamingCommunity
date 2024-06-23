# 23.06.24

from Src.Lib.Downloader import TOR_downloader

manager = TOR_downloader()

magnet_link = "magnet:?x"
manager.add_magnet_link(magnet_link)
manager.start_download()
manager.move_downloaded_files()

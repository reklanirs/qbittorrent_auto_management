# qbittorrent_auto_management
Automatically manage qbittorrent rss, download, and delete torrents.

Need to work with rclone.





### Issues:

有一些种子会有很奇怪的命名无法被识别, 更致命的是有的命名里面会有 " 号, 导致qbit_auto输出的json无法被解析: json.decoder.JSONDecodeError: Expecting ',' delimiter: line 15375 column 102 (char 559815).
E.g.:
(C96) [PLUM (Kanna, Ayakase Chiyoko)] Anta ni Naisho no Memory Piece   †ø?„«ÿ„¨?†_?‡??Š"?‘?\x14‡›?‡?? [Chinese] 1280x.zip
去掉这个种子里面的特殊符号后, clean过的命名为:
C96[PLUMKanna,AyakaseChiyoko]AntaniNaishonoMemoryPiece_"[Chinese]1280x.zip
可以发现仍然有一个 " 号, 会导致出错. 这个不是json的问题, 而是种子的问题, 需要手动clean种子命名.


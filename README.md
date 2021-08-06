# qbittorrent_auto_management
Automatically manage qbittorrent rss, download, and delete torrents. (Under windows)

Need to work with rclone and [qbittorrent-cli](https://github.com/fedarovich/qbittorrent-cli).



### Usage

**Install rclone,  Cmder, qbittorrent-cli and python3**

- Install and add rclone into your path
- Install python3 and make sure it's in your path
- Install [qbittorrent-cli](https://github.com/fedarovich/qbittorrent-cli/releases) and add it into your path
- Install Cmder
- Config your Google Drive account in rclone and make sure it's called `gd`
- Put `rss.sh` and `qbit_auto.py` into the same folder



**Config parameters**

In `qbit_auto.py`, 

	- line 15, config your qBittorrent webui password
	- line 16, config your server url (127.0.0.1 if local)

In `rss.sh`

- line 1, config the folder you want to upload
- (line 11, by default, the folder will be uploaded into gd:RSS)



**Run:**

In cmder, run

```shell
./rss.sh
```

That's all.





### Issues:

有一些种子会有很奇怪的命名无法被识别, 更致命的是有的命名里面会有 " 号, 导致qbit_auto输出的json无法被解析: json.decoder.JSONDecodeError: Expecting ',' delimiter: line 15375 column 102 (char 559815).

E.g.:
(C96) [PLUM (Kanna, Ayakase Chiyoko)] Anta ni Naisho no Memory Piece   †ø?„«ÿ„¨?†_?‡??Š"?‘?\x14‡›?‡?? [Chinese] 1280x.zip

去掉这个种子里面的特殊符号后, clean过的命名为:

C96[PLUMKanna,AyakaseChiyoko]AntaniNaishonoMemoryPiece_"[Chinese]1280x.zip

可以发现仍然有一个 " 号, 会导致出错. 这个不是json的问题, 而是种子的问题, 需要手动clean种子命名.



intra-scanner - Simple tcp port scanner for going through proxies
=========

![Build](https://img.shields.io/badge/Built%20with-Python-Blue)
![License](https://img.shields.io/badge/license-GNU_General_Public_License-_red.svg)

**Current Release: v0.3 (2021.1.19)**


Overview
--------
- 使用场景：
```
    attacker-machine(run intra-scanner)  <--->  vps proxy server  <--->  intranet-machine(proxy client)  <---> other-intranet-machines(scan targets)
```
**Notes**: 在某些特殊的情况下，不方便直接在目标内网机器上安装或运行端口扫描工具，但目标内网机器能反弹代理的情况下，本工具可隔着代理扫描内网机器


Installation
------------

```
apt install expect
python3 -m pip install IPy
python3 -m pip install threadpool
```

*Intra-scanner requires python 3 or greater*


Usage
------------
文件中读取ip列表，默认扫描top100 tcp端口
```
proxychains python3 intra-scan.py -i file_contents_ips.txt
```
支持的ip格式如下：
```
192.168.0.2-200
192.168.0.2/24
192.168.0.2
```
指定特定的目标和端口
```
proxychains python3 intra-scan.py -p 80,443,8080 -t 192.168.0.2/24
proxychains python3 intra-scan.py --top-ports 300 -t 192.168.0.4
```


存在的问题：
-----------
当前脚本匹配了英文，非英文系统可能存在误报
特定的网络抖动下，内网ip不存在


License
---------------
License: GNU General Public License, version 2

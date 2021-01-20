
intra-scanner - Simple tcp port scanner via proxies
=========

![Build](https://img.shields.io/badge/Built%20with-Python-Blue)
![License](https://img.shields.io/badge/license-GNU_General_Public_License-_red.svg)

**Current Release: v0.4 (2021.1.20)**


Overview
--------
- 使用场景：
```
本机(run intra-scan) <---> proxy服务器(vps) <---> 内网机器(proxy客户端) <---> 内网其它机器（工具扫描目标）
```
在特定的情况下，不方便直接在目标内网机器上安装或运行端口扫描工具，但目标内网机器仍可反弹代理的情况下，本工具可隔着代理扫描内网机器。常规的nmap/fscan等扫描工具在挂代理的情况下，会错误的判断所有端口都开启。


Installation
------------

```
apt install expect
chmod +x port_check.sh
python3 -m pip install IPy
```


Usage
------------
指定扫描目标, -i 包含ip列表的文件 / -t ip或ip段
```
proxychains python3 scan-via-proxy.py -i file_contents_ips.txt
proxychains python3 scan-via-proxy.py -t 192.168.0.2/24
```
-t/-i参数支持的ip格式如下：
```
192.168.0.2
192.168.0.2-200
192.168.0.2/24
```

指定特定的目标和端口
```
proxychains python3 scan-via-proxy.py -p 80,443,8080 -t 192.168.0.2/24
proxychains python3 scan-via-proxy.py --top-ports 300 -t 192.168.0.10-255
```
在不指定端口的情况，默认扫描24个端口
```
80,443,22,3306,8443,6379,8161,8080,27017,5984,11211,2049,9200,5601,9990,5900,5901,837,50070,2181,2375,8888,389,888
```


其它说明
-----------
默认最大的扫描线程数是40，见python中g_max_threads，可根据自己网络和代理的性能增加或减少
stat 扫描进度日志，当扫描的资产量较大时，可以通过该日志查看大致的进度。该日志大概2分多种刷新一次 
port_chk.log 端口扫描产生的debug日志，多个线程同时写入，打印比较乱


存在的问题：
-----------
当前脚本仅匹配了英文，非英文系统会存在误报。有中文系统的可提供中文打印给我，我加入expect脚本。

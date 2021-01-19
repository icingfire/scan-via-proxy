#!/usr/bin/python3
import sys, getopt, re, os, threading, time, queue
from IPy import IP
from datetime import datetime

# how many ports for one thread
g_thread_factor = 25
# network can be poor behind proxies
g_max_threads = 40
g_port_scan_script = "./port_check.sh"
g_nmap_top_ports = "./nmap_tcp_ports"
g_target_generator = None


class GeneTargets:
    def __init__(self, ip_l, port_l):
        self.ip_list = ip_l
        self.port_list = port_l
        self.threads = []
        self.fecth_factor = 5

    def register(self, in_thread):
        self.threads.append(in_thread)

    def next(self):
        for one_port in self.port_list:
            for one_ip in self.ip_list:
                yield one_ip + " " + str(one_port)

    def stopall(self):
        for one_t in self.threads:
            one_t.stopping()

    def svc(self):
        local_iter = self.next()
        try:
            while True:
                for one_t in self.threads:
                    if one_t.que.qsize() > self.fecth_factor:
                        continue
                    for i in range(self.fecth_factor):
                        t_next = next(local_iter)
                        #print("put in que: " + t_next)
                        one_t.que.put(t_next)
                time.sleep(1)
        except Exception as e:
            #print("stopping all threads")
            self.stopall()


class CheckSvc:
    def __init__(self):
        self.que = queue.Queue()
        self.stop = False

    def stopping(self):
        self.stop = True

    # in param format: "8.8.8.8 80"
    def check_port(self):
        while True:
            try:
                one_ip_port = self.que.get(timeout=5)
                ret = os.popen(g_port_scan_script + " " + one_ip_port).read().strip("\n")
                if ret != "":
                    print(ret)
            except Exception as e:
                #print("not feed in current thread")
                if self.stop:
                    #print("current thread stopped")
                    return
                else:
                    # queue will raise exception, if queue is empty and timeout
                    pass


def create_wait_workers(thread_num):
    thread_l = []
    for i in range(thread_num):
        t_cs = CheckSvc()
        t_tid = threading.Thread(target=t_cs.check_port)
        t_tid.start()
        g_target_generator.register(t_cs)
        thread_l.append(t_tid)
    t_tid = threading.Thread(target=g_target_generator.svc)
    t_tid.start()
    thread_l.append(t_tid)
    for one_tid in thread_l:
        one_tid.join()


def get_top_ports(str_port_num):
    port_cnt = int(str_port_num)
    if port_cnt <= 0:
        # defualt top 50 ports
        port_cnt = 50
    elif port_cnt > 8400:
        return [ one for one in range(1,65536) ]

    # read from nmap config
    ports_ret = os.popen("head -" + str(port_cnt) + " " + g_nmap_top_ports).read()
    return [ int(one.strip()) for one in ports_ret.split("\n")[:-1] ]


def analyse_ip(str_ip):
    r1 = re.compile(r'\d+(\.\d+){3}$')
    r2 = re.compile(r'\d+\.\d+\.\d+\.(\d+)-(\d+)')
    r3 = re.compile(r'\d+\.\d+\.\d+\.\d+/(\d+)')
    ret_l = []

    try:
        m1 = r1.match(str_ip)
        if m1:
            ret_l.append(str_ip)
            return ret_l
        m2 = r2.match(str_ip)
        if m2:
            start = int(m2.group(1))
            end = int(m2.group(2))
            pre = '.'.join(str_ip.split('.')[:3])
            for i in range(start,end+1):
                ret_l.append(pre + "." + str(i))
            return ret_l
        m3 = r3.match(str_ip)
        if m3:
            for one_ip in IP(str_ip, make_net=1):
                ret_l.append(str(one_ip))
            return ret_l
    except Exception as e:
        print("parse ip error " + str_ip + " , " + str(e))

    return ret_l


def get_iplist_from_file(in_file):
    ret_list = []
    try:
        with open(in_file) as f_h:
            for line in f_h:
                line = line.strip(' \r\n')
                if line != "":
                    ret_list.extend(analyse_ip(line))
    except Exception as e:
        print("Open file " + in_file + " failed, " + str(e))
    return ret_list


def clt_help():
    print("A port scan tool which can go through proxy")
    print(sys.argv[0] + '  [-p <port1>,<port2>,.../--top-ports <number>] -t <ip>/-i <ip_list_file>')
    print(sys.argv[0] + '  -h   to show this help')
    print('e.g: ')
    print('    ' + sys.argv[0] + ' -t 192.168.0.2')
    print('    ' + sys.argv[0] + ' -p 80,443,8080 -i ip_list.txt')


if __name__ == '__main__':
    target_ip = ""
    in_file = ""
    ports = ""
    top_ports = ""

    if len(sys.argv) < 3:
        print("Missing target")
        clt_help()
        exit(1)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:i:p:", ["help", "top-ports="])
    except getopt.GetoptError:
        clt_help()
        exit(2)

    for opt, arg in opts:
        if opt == '-h':
            clt_help()
            exit()
        elif opt == '-t':
            target_ip = arg
        elif opt == '-i':
            in_file = arg
        elif opt == '-p':
            ports = arg
        elif opt == '--top-ports':
            top_ports = arg

    ip_list = []
    port_list = []
    if target_ip != "":
        ip_list.extend(analyse_ip(target_ip))
    if in_file != "":
        ip_list.extend(get_iplist_from_file(in_file))
    if ports != "":
        port_list.extend(ports.split(','))
    if top_ports != "":
        port_list.extend(get_top_ports(top_ports))
    # default scan top 100 ports
    if len(port_list) == 0:
        port_list.extend(get_top_ports(100))

    thread_count = int(len(ip_list) * len(port_list) / g_thread_factor)
    if thread_count <= 0:
        thread_count = 1
    elif thread_count > g_max_threads:
        thread_count = g_max_threads

    print("Scan start at " + datetime.now().strftime('%m/%d-%H:%M:%S') + ", thread count: " + str(thread_count))
    g_target_generator = GeneTargets(ip_list, port_list)
    create_wait_workers(thread_count)
    print("Scan end at " + datetime.now().strftime('%m/%d-%H:%M:%S'))


##############################################################################
#                         Network Connections                                #
# This script shows TCP, UDP connections in realtime from /proc/net/.        #
#                                                                            #
##############################################################################

# !/usr/bin/python

import os
import re
import glob
import socket
import argparse
import time

template = "%-6s %-14s %-7s %-7s %-12s %-5s %-8s %s"
header = template % ("Proto", "Local address", "L_Port", "R_Port", "STATE",
                     "PID", "Program", "Remote address")

STATE = {'01': 'ESTABLISHED',
         '02': 'SYN_SENT',
         '03': 'SYN_RECV',
         '04': 'FIN_WAIT1',
         '05': 'FIN_WAIT2',
         '06': 'TIME_WAIT',
         '07': 'CLOSE',
         '08': 'CLOSE_WAIT',
         '09': 'LAST_ACK',
         '0A': 'LISTEN',
         '0B': 'CLOSING'}

parser = argparse.ArgumentParser(description='Show TCP and UDP connectios.')
parser.add_argument("-t", "--tcp", help="Show TCP connections",
                    action="store_const", const="tcp")
parser.add_argument("-u", "--udp", help="Show UDP connections",
                    action="store_const", const="udp")
parser.add_argument("-n", "--noDNS", help="Don't convert IP addreses to \
                    hosts names", action="store_false")
parser.add_argument("-s", "--sec", type=int, help="Nuber of seconds to refresh", default=1)
args = parser.parse_args()


def load_table(proto_v):
    """
    Read the table of tcp connections & remove header
    """
    with open("/proc/net/" + proto_v, 'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def hex2dec(s):
    """ Convert hex to dec and return string """
    return str(int(s, 16))


def ip_convert(s):
    """ Convert ip from hex to decimal """
    ip = [(hex2dec(s[6:8])), (hex2dec(s[4:6])), (hex2dec(s[2:4])),
          (hex2dec(s[0:2]))]
    return '.'.join(ip)


def remove_empty(array):
    return [x for x in array if x != '']


def convert_ip_and_port(array):
    """ Convert ip port from hex to decimal """
    host, port = array.split(':')
    return ip_convert(host), hex2dec(port)


def get_host_name(ip):
    """
    This method returns the first IP address string
    that responds as the given domain name, if not
    responds the return ip.
    """
    if args.noDNS:
        try:
            data = socket.getfqdn(ip)
            return data
        except (socket.timeout, socket.error):
            return ip
    else:
        return ip


def netstat(proto):

    """
    Function to return a list with status of tcp connections at linux systems
    To get pid of all network process running on system, you must run this
    script as superuser
    """
    result = []

    if proto in ("tcp", "udp"):

        content = load_table(proto)

        for line in content:

            line_array = remove_empty(line.split(' '))
            l_host, l_port = convert_ip_and_port(line_array[1])
            r_host, r_port = convert_ip_and_port(line_array[2])
            state = STATE[line_array[3]]
            inode = line_array[9]  # Need the inode to get process pid.
            pid = get_pid_of_inode(inode)
            prog_mane = get_prog_name(pid)

            if r_host[0] != "0":

                nline = template % (proto, l_host, l_port, r_port, state, pid, prog_mane,
                                    get_host_name(r_host))

                result.append(nline)

    return result


def get_prog_name(pid_num):

    try:
        exe = os.readlink('/proc/' + str(pid_num) + '/exe')
        l_exe = exe.split("/")  # Split line by /
        ln_exe = l_exe[len(l_exe) - 1]  # Get last program name
    except OSError:
        ln_exe = None

    return ln_exe


def get_pid_of_inode(inode):
    """
    To retrieve the process pid, check every running process and look
    for one using the given inode.
    """
    for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode, os.readlink(item)):
                return item.split('/')[2]
        except OSError:
            pass
    return None


def prnt_scr(buff):
    """
    This Function clear console, print header and print lines
    from buffer.
    """
    os.system('clear')

    print(header)
    print("-" * 80)

    for put_scr in buff:  # Print information on console
        print(put_scr)

    return None


if __name__ == '__main__':

    buff1 = netstat(args.tcp) + netstat(args.udp)
    prnt_scr(buff1)

# -----------------Creating First buffer-------------
    try:
        while True:

            buff1 = netstat(args.tcp)+netstat(args.udp)
# ---------------------------------------------------
            time.sleep(args.sec)  # Wait some seconds
# -----------------Creating Second buffer------------
            buff2 = netstat(args.tcp) + netstat(args.udp)
# ---------------------------------------------------
            if buff2 != buff1:  # Compare 2 buffers
                prnt_scr(buff2)

    except KeyboardInterrupt:
        print("Program stopped!")

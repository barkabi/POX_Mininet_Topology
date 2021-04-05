#!/usr/bin/python

from scapy.all import *
import sys

My_Data="A"*1462

packet = IP(dst="192.168.100.123")/TCP()/My_Data
send(packet,count=)

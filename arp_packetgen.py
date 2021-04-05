#!/usr/bin/python

from scapy.all import *
import sys

#print "Src Dst ",sys.argv," ",type(sys.argv)
#print sys.argv[0]
pkt=send(ARP(op=ARP.who_has,psrc=sys.argv[1],pdst=sys.argv[2]))



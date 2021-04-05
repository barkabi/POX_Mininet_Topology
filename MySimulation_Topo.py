
from mininet.topo import Topo
from mininet.net  import Mininet
from mininet.link import TCLink
from mininet.node import Controller
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.node import OVSKernelSwitch
from scapy.all import *
import os
import random
import time
import subprocess
import threading
from multiprocessing import Process
REMOTE_CONTROLLER_IP = "127.0.0.1"



class SimTopo(Topo):	
	"Simulation Topology"	
	def __init__(self):
		super(SimTopo,self).__init__()

		self.NumOfSwitches=10
		#My Switches
		switch1=self.addSwitch('s1',dpid='0000000000000001')
		switch2=self.addSwitch('s2',dpid='0000000000000002')
		switch3=self.addSwitch('s3',dpid='0000000000000003')
		switch4=self.addSwitch('s4',dpid='0000000000000004')
		switch5=self.addSwitch('s5',dpid='0000000000000005')
		switch6=self.addSwitch('s6',dpid='0000000000000006')
		switch7=self.addSwitch('s7',dpid='0000000000000007')
		switch8=self.addSwitch('s8',dpid='0000000000000008')
		switch9=self.addSwitch('s9',dpid='0000000000000009')
		switch10=self.addSwitch('s10',dpid='000000000000000a')
		#switch11=self.addSwitch('s11',dpid='000000000000000b')
		#switch12=self.addSwitch('s12',dpid='000000000000000c')

	
		#My Hosts
		h11=self.addHost('h11')
		h12=self.addHost('h12')
		h13=self.addHost('h13')
		h14=self.addHost('h14')
		#h15=self.addHost('h15')
	

		h21=self.addHost('h21')
		h22=self.addHost('h22')
		h23=self.addHost('h23')
		h24=self.addHost('h24')
		h25=self.addHost('h25')
		#h26=self.addHost('h26')
		
	


		h31=self.addHost('h31')
		h32=self.addHost('h32')
		h33=self.addHost('h33')
		h34=self.addHost('h34')
		h35=self.addHost('h35')
		#h36=self.addHost('h36')
	


		h41=self.addHost('h41')
		h42=self.addHost('h42')
		h43=self.addHost('h43')
		h44=self.addHost('h44')
		#h45=self.addHost('h45')
	

		h51=self.addHost('h51')
		h52=self.addHost('h52')
		h53=self.addHost('h53')
		#h54=self.addHost('h54')


		h61=self.addHost('h61')
		h62=self.addHost('h62')
		h63=self.addHost('h63')
		h64=self.addHost('h64')
		#h65=self.addHost('h65')

		h71=self.addHost('h71')
		h72=self.addHost('h72')
		h73=self.addHost('h73')
		#h74=self.addHost('h74')

		h81=self.addHost('h81')
		h82=self.addHost('h82')
		h83=self.addHost('h83')
		h84=self.addHost('h84')

		h91=self.addHost('h91')
		h92=self.addHost('h92')
		h93=self.addHost('h93')

		h101=self.addHost('h101')
		h102=self.addHost('h102')
		h103=self.addHost('h103')
		h104=self.addHost('h104')

		#h111=self.addHost('h111')
		#h112=self.addHost('h112')
		#h113=self.addHost('h113')

		#h121=self.addHost('h121')
		#h122=self.addHost('h122')
		#h123=self.addHost('h123')
		#h124=self.addHost('h124')

		#Grouping The Hosts -- Because the indices for each switch is different we have to mention exlicitly 
		self.Groups=[['h11','h12','h13','h14'],['h21','h22','h23','h24','h25'],['h31','h32','h33','h34','h35'],['h41','h42','h43','h44'],['h51','h52','h53'],['h61','h62','h63','h64'],['h71','h72','h73'],['h81','h82','h83','h84'],['h91','h92','h93'],['h101','h102','h103','h104']]
		#Assign IP to Hosts
		self.IP_To_Hosts={}
		self.IP_To_Hosts["h11"]="140.0.1.1"
		self.IP_To_Hosts["h12"]="140.0.1.2"
		self.IP_To_Hosts["h13"]="140.0.1.3"
		self.IP_To_Hosts["h14"]="140.0.1.4"
		#self.IP_To_Hosts["h15"]="140.0.1.5"


		self.IP_To_Hosts["h21"]="141.0.1.1"
		self.IP_To_Hosts["h22"]="141.0.1.2"
		self.IP_To_Hosts["h23"]="141.0.1.3"
		self.IP_To_Hosts["h24"]="141.0.1.4"
		self.IP_To_Hosts["h25"]="141.0.1.5"
		#self.IP_To_Hosts["h26"]="141.0.1.6"


		self.IP_To_Hosts["h31"]="142.0.1.1"
		self.IP_To_Hosts["h32"]="142.0.1.2"
		self.IP_To_Hosts["h33"]="142.0.1.3"
		self.IP_To_Hosts["h34"]="142.0.1.4"
		self.IP_To_Hosts["h35"]="142.0.1.5"
		#self.IP_To_Hosts["h36"]="142.0.1.6"


		self.IP_To_Hosts["h41"]="143.0.1.1"
		self.IP_To_Hosts["h42"]="143.0.1.2"
		self.IP_To_Hosts["h43"]="143.0.1.3"
		self.IP_To_Hosts["h44"]="143.0.1.4"
		#self.IP_To_Hosts["h45"]="143.0.1.5"


		self.IP_To_Hosts["h51"]="144.0.1.1"
		self.IP_To_Hosts["h52"]="144.0.1.2"
		self.IP_To_Hosts["h53"]="144.0.1.3"
		#self.IP_To_Hosts["h54"]="144.0.1.4"

		self.IP_To_Hosts["h61"]="145.0.1.1"
		self.IP_To_Hosts["h62"]="145.0.1.2"
		self.IP_To_Hosts["h63"]="145.0.1.3"
		self.IP_To_Hosts["h64"]="145.0.1.4"
		#self.IP_To_Hosts["h65"]="145.0.1.5"

		self.IP_To_Hosts["h71"]="146.0.1.1"
		self.IP_To_Hosts["h72"]="146.0.1.2"
		self.IP_To_Hosts["h73"]="146.0.1.3"
		#self.IP_To_Hosts["h74"]="146.0.1.4"


		self.IP_To_Hosts["h81"]="147.0.1.1"
		self.IP_To_Hosts["h82"]="147.0.1.2"
		self.IP_To_Hosts["h83"]="147.0.1.3"
		self.IP_To_Hosts["h84"]="147.0.1.4"

		self.IP_To_Hosts["h91"]="148.0.1.1"
		self.IP_To_Hosts["h92"]="148.0.1.2"
		self.IP_To_Hosts["h93"]="148.0.1.3"

		self.IP_To_Hosts["h101"]="149.0.1.1"
		self.IP_To_Hosts["h102"]="149.0.1.2"
		self.IP_To_Hosts["h103"]="149.0.1.3"
		self.IP_To_Hosts["h104"]="149.0.1.4"

		#self.IP_To_Hosts["h111"]="150.0.1.1"
		#self.IP_To_Hosts["h112"]="150.0.1.2"
		#self.IP_To_Hosts["h113"]="150.0.1.3"

		#self.IP_To_Hosts["h121"]="151.0.1.1"
		#self.IP_To_Hosts["h122"]="151.0.1.2"
		#self.IP_To_Hosts["h123"]="151.0.1.3"
		#self.IP_To_Hosts["h124"]="151.0.1.4"
		



		#Addling Links from Hosts to Switches
		self.addLink(h11,switch1,bw=1000)
		self.addLink(h12,switch1,bw=1000)
		self.addLink(h13,switch1,bw=1000)
		self.addLink(h14,switch1,bw=1000)
		#self.addLink(h15,switch1,bw=1000)


		self.addLink(h21,switch2,bw=1000)
		self.addLink(h22,switch2,bw=1000)
		self.addLink(h23,switch2,bw=1000)
		self.addLink(h24,switch2,bw=1000)
		self.addLink(h25,switch2,bw=1000)
		#self.addLink(h26,switch2,bw=1000)


		self.addLink(h31,switch3,bw=1000)
		self.addLink(h32,switch3,bw=1000)
		self.addLink(h33,switch3,bw=1000)
		self.addLink(h34,switch3,bw=1000)
		self.addLink(h35,switch3,bw=1000)
		#self.addLink(h36,switch3,bw=1000)


		self.addLink(h41,switch4,bw=1000)
		self.addLink(h42,switch4,bw=1000)
		self.addLink(h43,switch4,bw=1000)
		self.addLink(h44,switch4,bw=1000)
		#self.addLink(h45,switch4,bw=1000)

		self.addLink(h51,switch5,bw=1000)
		self.addLink(h52,switch5,bw=1000)
		self.addLink(h53,switch5,bw=1000)
		#self.addLink(h54,switch5,bw=1000)

		self.addLink(h61,switch6,bw=1000)
		self.addLink(h62,switch6,bw=1000)
		self.addLink(h63,switch6,bw=1000)
		self.addLink(h64,switch6,bw=1000)
		#self.addLink(h65,switch6,bw=1000)

		self.addLink(h71,switch7,bw=1000)
		self.addLink(h72,switch7,bw=1000)
		self.addLink(h73,switch7,bw=1000)
		#self.addLink(h74,switch7,bw=1000)

		self.addLink(h81,switch8,bw=1000)
		self.addLink(h82,switch8,bw=1000)
		self.addLink(h83,switch8,bw=1000)
		self.addLink(h84,switch8,bw=1000)

		self.addLink(h91,switch9,bw=1000)
		self.addLink(h92,switch9,bw=1000)
		self.addLink(h93,switch9,bw=1000)

		self.addLink(h101,switch10,bw=1000)
		self.addLink(h102,switch10,bw=1000)
		self.addLink(h103,switch10,bw=1000)
		self.addLink(h104,switch10,bw=1000)

		#self.addLink(h111,switch11,bw=1000)
		#self.addLink(h112,switch11,bw=1000)
		#self.addLink(h113,switch11,bw=1000)

		#self.addLink(h121,switch12,bw=1000)
		#self.addLink(h122,switch12,bw=1000)
		#self.addLink(h123,switch12,bw=1000)
		#self.addLink(h124,switch12,bw=1000)

		#Links between Switches
		self.addLink(switch1,switch2,bw=100)
		self.addLink(switch1,switch3,bw=100)
		self.addLink(switch1,switch4,bw=100)
		self.addLink(switch1,switch5,bw=100)
		self.addLink(switch1,switch6,bw=100)
		self.addLink(switch2,switch3,bw=100)
		self.addLink(switch2,switch4,bw=100)
		self.addLink(switch2,switch6,bw=100)
		self.addLink(switch2,switch8,bw=100)
		self.addLink(switch3,switch6,bw=100)
		self.addLink(switch4,switch5,bw=100)
		self.addLink(switch4,switch6,bw=100)
		self.addLink(switch4,switch7,bw=100)
		self.addLink(switch4,switch8,bw=100)
		self.addLink(switch4,switch9,bw=100)
		self.addLink(switch4,switch10,bw=100)
		self.addLink(switch5,switch6,bw=100)
		self.addLink(switch5,switch7,bw=100)
		self.addLink(switch5,switch9,bw=100)
		self.addLink(switch7,switch8,bw=100)
		self.addLink(switch7,switch9,bw=100)
		self.addLink(switch7,switch10,bw=100)
		#self.addLink(switch7,switch11,bw=100)
		self.addLink(switch8,switch10,bw=100)
		#self.addLink(switch8,switch12,bw=100)
		#self.addLink(switch9,switch11,bw=100)
		#self.addLink(switch10,switch11,bw=100)
		#self.addLink(switch10,switch12,bw=100)
		#self.addLink(switch11,switch12,bw=100)



def TrafficGeneration():
	Simulation=SimTopo()


	#Start the Mininet
	net=Mininet(topo=Simulation,link=TCLink,controller=None)
	net.addController("c0", controller=RemoteController,ip=REMOTE_CONTROLLER_IP, port=6633)
	net.start()
	
	for h in net.hosts:
		print "disable ipv6"
		h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
		h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
		h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

	for sw in net.switches:
		print "disable ipv6"
		sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
		sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
		sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
		#Setting the IP Address for each Host and also Default Route to the interface
	for host,hostIP in Simulation.IP_To_Hosts.items():
		tmpHost=net.get(host)
		tmpHost.setIP(hostIP)
		mycomm="ip route add default dev "+host+"-eth0"
		#print mycomm
		tmpHost.cmd(mycomm)
	time.sleep(20)

	for group in Simulation.Groups:
		for host1 in group:
			for othergroup in Simulation.Groups:
				if group!=othergroup:
					for host2 in othergroup:
						if host1!=host2:
							FirstHost=net.get(host1)
							SecondHost=net.get(host2)
							FirstHost.cmd('python packetgen.py ',Simulation.IP_To_Hosts[host1],' ',Simulation.IP_To_Hosts[host2])
							print '\nsudo python packetgen.py ',Simulation.IP_To_Hosts[host1],' ',Simulation.IP_To_Hosts[host2],'\n'

							#FirstHost.cmd('ping '+ str(SecondHost.IP())+" &")
							#print '\nARP Packet  ',Simulation.IP_To_Hosts[host1],' ',Simulation.IP_To_Hosts[host2],'\n'
							#time.sleep(1)
	
	#Traffic Generation
	Traffic_Volume="1G"
	TotalRunningTime=90*60
	Current_Time=0
	port=6000
	print "\nDone "
	#Remove the files in /home/saeed/Data/ -- Because the file system is common ...

	#h11=net.get('h11')
	#h11.cmd('sudo rm -r /home/saeed/Data/*')
	#h11.cmd('sudo killall iperf')
	
	#Genarting Offline Traffic
	TrafficList=[]
	random.seed(10)
	TimeBetweenFlows=25.0

	while Current_Time<TotalRunningTime:
		
		print Current_Time ,' ',TimeBetweenFlows
		#Choosing two groups or switches
		RandomPeer = random.sample(xrange(len(Simulation.Groups)), 2)
		FirstClient=Simulation.Groups[RandomPeer[0]][random.randint(0,len(Simulation.Groups[RandomPeer[0]])-1)]
		SecondClient=Simulation.Groups[RandomPeer[1]][random.randint(0,len(Simulation.Groups[RandomPeer[1]])-1)]
		InterArrivalTime=random.expovariate(1/TimeBetweenFlows)
		Current_Time=Current_Time+InterArrivalTime
		TrafficList.append([FirstClient,SecondClient,port,Traffic_Volume,InterArrivalTime,Current_Time])
		port=port+1
		
	#Start The Servers
	print "Starting the Servers ..."
	for index in range(len(TrafficList)):
		p1 = Process(target=Start_Server, args=(net,TrafficList[index][0], TrafficList[index][1],TrafficList[index][2],))
		print "Source ",TrafficList[index][0]," to ",TrafficList[index][1]," port ",str(TrafficList[index][2])," CurrentTime "+str(TrafficList[index][5])+" \n"
		p1.start()
	#Start The Clients
	print "Starting the Clients ..."
	for index in range(len(TrafficList)):
		p1 = Process(target=Start_Client, args=(net,TrafficList[index][0],TrafficList[index][1],TrafficList[index][2],TrafficList[index][3]))
		print "Source ",TrafficList[index][0]," to ",TrafficList[index][1]," port ",str(TrafficList[index][2])," CurrentTime "+str(TrafficList[index][5])+" \n"
		p1.start()
		print "Current Time ",TrafficList[index][5]
		print "\nInterArrTime",TrafficList[index][4]
		time.sleep(TrafficList[index][4])
		#time.sleep(20)
	"""
	p1 = Process(target=Start_Server, args=(net,Simulation.Groups[4][0], Simulation.Groups[5][0],6001,))
	p1.start()
	time.sleep(5)
	p2 = Process(target=Start_Client, args=(net,Simulation.Groups[4][0],Simulation.Groups[5][0],6001,Traffic_Volume))
	p2.start()
	
	p3 = Process(target=Start_Server, args=(net,Simulation.Groups[4][1], Simulation.Groups[5][1],6002,))
	p3.start()
	time.sleep(5)
	p4 = Process(target=Start_Client, args=(net,Simulation.Groups[4][1],Simulation.Groups[5][1],6002,Traffic_Volume))
	p4.start()

	p5 = Process(target=Start_Server, args=(net,Simulation.Groups[4][2], Simulation.Groups[4][2],6003,))
	p5.start()
	time.sleep(5)
	p6 = Process(target=Start_Client, args=(net,Simulation.Groups[4][2],Simulation.Groups[4][2],6003,Traffic_Volume))
	p6.start()
	time.sleep(5)
	"""
	print "Traffic Done"
	
	CLI(net)
	net.stop()

def Start_Server(net,Client_Src,Server_Dst,port):
	SRC,DST=net.get(Client_Src,Server_Dst)
	DST.cmd('iperf -s -p '+str(port)+' > /home/saeed/Data/'+SRC.IP()+'_'+DST.IP()+'_'+str(port)+'.txt &')
def Start_Client(net,Client_Src,Server_Dst,port,Traffic_Volume):
	SRC,DST=net.get(Client_Src,Server_Dst)
	SRC.cmd('iperf -c '+DST.IP()+' -p '+str(port)+' -n '+Traffic_Volume+' &')

	
if __name__=='__main__':
	TrafficGeneration()
	


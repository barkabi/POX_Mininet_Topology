from pox.core import core
from pox.openflow.discovery import Discovery
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr
# import pox.openflow.discovery
from pox.lib.util import dpidToStr, str_to_dpid
from pox.lib.packet.arp import arp
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
# from pox.openflow.discovery import Discovery
from pox.openflow.flow_tracker import *
from pox.lib.recoco import Timer
import time
from pox.lib.revent import *
from collections import defaultdict
#from LB_ILP_Opt import LB_ILP_Opt
#from PyMathProg_ILP_LP_1 import My_Formulation
#from pymprog import *
import networkx as nx
from pox.openflow.of_json import *
import numpy as np
from pox.openflow.discovery import Discovery
import ipaddress
from multiprocessing import Process
from LB_ILP_Opt_Last_Version1 import LB_ILP_Opt_Last_Version1
from LB_ILP_Opt_Last_Version2 import LB_ILP_Opt_Last_Version2
from math import ceil, floor
from LR1 import Main_Loop
log = core.getLogger()


class MySimulation(EventMixin):
    def __init__(self):
        def startup():
            core.openflow.addListeners(self, priority=0)
            core.openflow_discovery.addListeners(self)
        core.openflow.addListenerByName("FlowStatsReceived", self._handle_flowstats_received)
        core.call_when_ready(startup, ('openflow', 'openflow_discovery'))
	#core.openflow.addListenerByName("PortStatsReceived", self._handle_portstats_received)

	self.Link_Base_Capacity=10000
	self.Adj = np.array([[0,1,1,1,1,1,0,0,0,0],[1,0,1,1,0,1,0,1,0,0],[1,1,0,0,0,1,0,0,0,0],[1,1,0,0,1,1,1,1,1,1],[1,0,0,1,0,1,1,0,1,0],[1,1,1,1,1,0,0,0,0,0],[0,0,0,1,1,0,0,1,1,1],[0,1,0,1,0,0,1,0,0,1],[0,0,0,1,1,0,1,0,0,0],[0,0,0,1,0,0,1,1,0,0]])
        self.Capacity=np.array([[0,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,0,0,0,0],[self.Link_Base_Capacity,0,self.Link_Base_Capacity,self.Link_Base_Capacity,0,self.Link_Base_Capacity,0,self.Link_Base_Capacity,0,0],[self.Link_Base_Capacity,self.Link_Base_Capacity,0,0,0,self.Link_Base_Capacity,0,0,0,0],[self.Link_Base_Capacity,self.Link_Base_Capacity,0,0,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity],[self.Link_Base_Capacity,0,0,self.Link_Base_Capacity,0,self.Link_Base_Capacity,self.Link_Base_Capacity,0,self.Link_Base_Capacity,0],[self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity,0,0,0,0,0],[0,0,0,self.Link_Base_Capacity,self.Link_Base_Capacity,0,0,self.Link_Base_Capacity,self.Link_Base_Capacity,self.Link_Base_Capacity],[0,self.Link_Base_Capacity,0,self.Link_Base_Capacity,0,0,self.Link_Base_Capacity,0,0,self.Link_Base_Capacity],[0,0,0,self.Link_Base_Capacity,self.Link_Base_Capacity,0,self.Link_Base_Capacity,0,0,0],[0,0,0,self.Link_Base_Capacity,0,0,self.Link_Base_Capacity,self.Link_Base_Capacity,0,0]])
	print self.Capacity
	#[self.Capacity]=self.Capacity
	#print self.Capacity
        # core.openflow.addListenerByName("PortStatsReceived", self._handle_portstats_received)
	self.Number_Of_Subnets=10
	self.TotalNumOfLinks = 23
        self.TotalNumOfHosts = 39
	self.Traffic_Matrix=np.zeros((self.TotalNumOfHosts,self.TotalNumOfHosts),dtype=np.double)
	Subnet_To_Subnet=np.zeros((self.Number_Of_Subnets,self.Number_Of_Subnets),dtype=np.double)
	self.Traffic_Image={}
	self.Traffic_Image[0]=Subnet_To_Subnet
	tmpArray=np.zeros((self.TotalNumOfHosts,self.TotalNumOfHosts),dtype=np.double)
	self.HtH_Traffic_Image={}
	self.HtH_Traffic_Image[0]=tmpArray
	self.Traffic_Image_Counter=0
        self.MydpIds = []
        self.All_Shortest_Paths = []
        self.All_End_To_End_Paths = []
        self.Traffic_Matrix_File = open("/home/saeed/Traffic_Matrix.txt", "w+")
        self.BW_Matrix_File = open("/home/saeed/BW_Matrix.txt", "w+")
	self.My_Log=open("/home/saeed/MyLog.txt", "a")
	self.Traffic_Usage=open("/home/saeed/Traffic_Usage.txt", "w")
	self.Total_Byte_Count=open("/home/saeed/Total_Byte_Count.txt", "w")
	self.My_Final_Result=open("/home/saeed/My_Final_Result.txt", "a")
	self.My_Test=open("/home/saeed/My_Test.txt", "w+")
	self.H2H_File=open("/home/saeed/H2H.txt", "w+")
	self.Flow_Stat_Get_Switches=[]
	self.Port_Stat_Get_Switches=[]
        self.dpid_to_SwitchName = {}
        self.Router_To_Router_Ports = {}
        self.Host_To_Router = {}
        self.Host_To_Router_Ports = {}
        self.Host_To_Mac = {}
        self.LinkCounter = 0
        self.HostCounter = 0
        self.InitializationFinished = False
        self.HostCollectingFinished = False
	self.Sampling_Duration=15*60
	self.Epsilon=0.0001
	self.Scale_DownGrade=0.0001
	self.Data_Precision=2 
	self.switches_bw =defaultdict(lambda: defaultdict(int)) # holds switches ports last seen bytes
	self.estim_bw={}
	Timer(self.Sampling_Duration, self._timer_func1, recurring=True)
	#Timer(self.Sampling_Duration, self._timer_func2, recurring=True)
	
	self.Port_Stat_Counter=1
	self.Router_Port_Router={}
	self.Traffic_Usage_On_Links={}
	self.Traffic_Usage_Image={}
	self.My_Routers ={}
	self.My_Routers["R_0" ] ="1.1.1.1"
	self.My_Routers["R_1" ] ="2.2.2.2"
	self.My_Routers["R_2" ] ="3.3.3.3"
	self.My_Routers["R_3" ] ="4.4.4.4"
	self.My_Routers["R_4" ] ="5.5.5.5"
	self.My_Routers["R_5" ] ="6.6.6.6"
	self.My_Routers["R_6" ] ="7.7.7.7"
	self.My_Routers["R_7" ] ="8.8.8.8"
	self.My_Routers["R_8" ] ="9.9.9.9"
	self.My_Routers["R_9" ] ="10.10.10.10"
	#self.My_Routers["R_10" ] ="11.11.11.11"
	#self.My_Routers["R_11" ] ="12.12.12.12"
	self.Number_Of_Routers=len(self.My_Routers)
	self.My_Routers_Rev={}
	self.My_Routers_Rev["1.1.1.1"]="R_0"
	self.My_Routers_Rev["2.2.2.2"]="R_1"
	self.My_Routers_Rev["3.3.3.3"]="R_2"
	self.My_Routers_Rev["4.4.4.4"]="R_3"
	self.My_Routers_Rev["5.5.5.5"]="R_4"
	self.My_Routers_Rev["6.6.6.6"]="R_5"
	self.My_Routers_Rev["7.7.7.7"]="R_6"
	self.My_Routers_Rev["8.8.8.8"]="R_7"
	self.My_Routers_Rev["9.9.9.9"]="R_8"
	self.My_Routers_Rev["10.10.10.10"]="R_9"
	#self.My_Routers_Rev["11.11.11.11"]="R_10"
	#self.My_Routers_Rev["12.12.12.12"]="R_11"

	self.dpid_to_SwitchName={}
	self.dpid_to_SwitchName['00-00-00-00-00-01']='R_0'
	self.dpid_to_SwitchName['00-00-00-00-00-02']='R_1'
	self.dpid_to_SwitchName['00-00-00-00-00-03']='R_2'
	self.dpid_to_SwitchName['00-00-00-00-00-04']='R_3'
	self.dpid_to_SwitchName['00-00-00-00-00-05']='R_4'
	self.dpid_to_SwitchName['00-00-00-00-00-06']='R_5'
	self.dpid_to_SwitchName['00-00-00-00-00-07']='R_6'
	self.dpid_to_SwitchName['00-00-00-00-00-08']='R_7'
	self.dpid_to_SwitchName['00-00-00-00-00-09']='R_8'
	self.dpid_to_SwitchName['00-00-00-00-00-0a']='R_9'
	#self.dpid_to_SwitchName['00-00-00-00-00-0b']='R_10'
	#self.dpid_to_SwitchName['00-00-00-00-00-0c']='R_11'
	#For mapping from Route File 
	self.SwitchName_to_dpid={}
	self.SwitchName_to_dpid['R_0']='00-00-00-00-00-01'
	self.SwitchName_to_dpid['R_1']='00-00-00-00-00-02'
	self.SwitchName_to_dpid['R_2']='00-00-00-00-00-03'
	self.SwitchName_to_dpid['R_3']='00-00-00-00-00-04'
	self.SwitchName_to_dpid['R_4']='00-00-00-00-00-05'
	self.SwitchName_to_dpid['R_5']='00-00-00-00-00-06'
	self.SwitchName_to_dpid['R_6']='00-00-00-00-00-07'
	self.SwitchName_to_dpid['R_7']='00-00-00-00-00-08'
	self.SwitchName_to_dpid['R_8']='00-00-00-00-00-09'
	self.SwitchName_to_dpid['R_9']='00-00-00-00-00-0a'
	#self.SwitchName_to_dpid['R_10']='00-00-00-00-00-0b'
	#self.SwitchName_to_dpid['R_11']='00-00-00-00-00-0c'

	self.My_Host_To_IP_Mapping={}
	self.My_Host_To_IP_Mapping["H_0"]="140.0.1.1"
	self.My_Host_To_IP_Mapping["140.0.1.1"]="H_0"
	self.My_Host_To_IP_Mapping["H_1"]="140.0.1.2"
	self.My_Host_To_IP_Mapping["140.0.1.2"]="H_1"
	self.My_Host_To_IP_Mapping["H_2"]="140.0.1.3"
	self.My_Host_To_IP_Mapping["140.0.1.3"]="H_2"
	self.My_Host_To_IP_Mapping["H_3"]="140.0.1.4"
	self.My_Host_To_IP_Mapping["140.0.1.4"]="H_3"
	#self.My_Host_To_IP_Mapping["H_4"]="140.0.1.5"
	#self.My_Host_To_IP_Mapping["141.0.1.5"]="H_4"

	self.My_Host_To_IP_Mapping["H_4"]="141.0.1.1"
	self.My_Host_To_IP_Mapping["141.0.1.1"]="H_4"
	self.My_Host_To_IP_Mapping["H_5"]="141.0.1.2"
	self.My_Host_To_IP_Mapping["141.0.1.2"]="H_5"
	self.My_Host_To_IP_Mapping["H_6"]="141.0.1.3"
	self.My_Host_To_IP_Mapping["141.0.1.3"]="H_6"
	self.My_Host_To_IP_Mapping["H_7"]="141.0.1.4"
	self.My_Host_To_IP_Mapping["141.0.1.4"]="H_7"
	self.My_Host_To_IP_Mapping["H_8"]="141.0.1.5"
	self.My_Host_To_IP_Mapping["141.0.1.5"]="H_8"
	#self.My_Host_To_IP_Mapping["H_10"]="141.0.1.6"
	#self.My_Host_To_IP_Mapping["141.0.1.6"]="H_10"

	self.My_Host_To_IP_Mapping["H_9"]="142.0.1.1"
	self.My_Host_To_IP_Mapping["142.0.1.1"]="H_9"
	self.My_Host_To_IP_Mapping["H_10"]="142.0.1.2"
	self.My_Host_To_IP_Mapping["142.0.1.2"]="H_10"
	self.My_Host_To_IP_Mapping["H_11"]="142.0.1.3"
	self.My_Host_To_IP_Mapping["142.0.1.3"]="H_11"
	self.My_Host_To_IP_Mapping["H_12"]="142.0.1.4"
	self.My_Host_To_IP_Mapping["142.0.1.4"]="H_12"
	self.My_Host_To_IP_Mapping["H_13"]="142.0.1.5"
	self.My_Host_To_IP_Mapping["142.0.1.5"]="H_13"
	#self.My_Host_To_IP_Mapping["H_16"]="142.0.1.6"
	#self.My_Host_To_IP_Mapping["142.0.1.6"]="H_16"

	self.My_Host_To_IP_Mapping["H_14"]="143.0.1.1"
	self.My_Host_To_IP_Mapping["143.0.1.1"]="H_14"
	self.My_Host_To_IP_Mapping["H_15"]="143.0.1.2"
	self.My_Host_To_IP_Mapping["143.0.1.2"]="H_15"
	self.My_Host_To_IP_Mapping["H_16"]="143.0.1.3"
	self.My_Host_To_IP_Mapping["143.0.1.3"]="H_16"
	self.My_Host_To_IP_Mapping["H_17"]="143.0.1.4"
	self.My_Host_To_IP_Mapping["143.0.1.4"]="H_17"
	#self.My_Host_To_IP_Mapping["H_21"]="143.0.1.5"
	#self.My_Host_To_IP_Mapping["143.0.1.5"]="H_21"

	self.My_Host_To_IP_Mapping["H_18"]="144.0.1.1"
	self.My_Host_To_IP_Mapping["144.0.1.1"]="H_18"
	self.My_Host_To_IP_Mapping["H_19"]="144.0.1.2"
	self.My_Host_To_IP_Mapping["144.0.1.2"]="H_19"
	self.My_Host_To_IP_Mapping["H_20"]="144.0.1.3"
	self.My_Host_To_IP_Mapping["144.0.1.3"]="H_20"
	#self.My_Host_To_IP_Mapping["H_25"]="144.0.1.4"
	#self.My_Host_To_IP_Mapping["144.0.1.4"]="H_25"

	self.My_Host_To_IP_Mapping["H_21"]="145.0.1.1"
	self.My_Host_To_IP_Mapping["145.0.1.1"]="H_21"
	self.My_Host_To_IP_Mapping["H_22"]="145.0.1.2"
	self.My_Host_To_IP_Mapping["145.0.1.2"]="H_22"
	self.My_Host_To_IP_Mapping["H_23"]="145.0.1.3"
	self.My_Host_To_IP_Mapping["145.0.1.3"]="H_23"
	self.My_Host_To_IP_Mapping["H_24"]="145.0.1.4"
	self.My_Host_To_IP_Mapping["145.0.1.4"]="H_24"

	self.My_Host_To_IP_Mapping["H_25"]="146.0.1.1"
	self.My_Host_To_IP_Mapping["146.0.1.1"]="H_25"
	self.My_Host_To_IP_Mapping["H_26"]="146.0.1.2"
	self.My_Host_To_IP_Mapping["146.0.1.2"]="H_26"
	self.My_Host_To_IP_Mapping["H_27"]="146.0.1.3"
	self.My_Host_To_IP_Mapping["146.0.1.3"]="H_27"


	self.My_Host_To_IP_Mapping["H_28"]="147.0.1.1"
	self.My_Host_To_IP_Mapping["147.0.1.1"]="H_28"
	self.My_Host_To_IP_Mapping["H_29"]="147.0.1.2"
	self.My_Host_To_IP_Mapping["147.0.1.2"]="H_29"
	self.My_Host_To_IP_Mapping["H_30"]="147.0.1.3"
	self.My_Host_To_IP_Mapping["147.0.1.3"]="H_30"
	self.My_Host_To_IP_Mapping["H_31"]="147.0.1.4"
	self.My_Host_To_IP_Mapping["147.0.1.4"]="H_31"

	self.My_Host_To_IP_Mapping["H_32"]="148.0.1.1"
	self.My_Host_To_IP_Mapping["148.0.1.1"]="H_32"
	self.My_Host_To_IP_Mapping["H_33"]="148.0.1.2"
	self.My_Host_To_IP_Mapping["148.0.1.2"]="H_33"
	self.My_Host_To_IP_Mapping["H_34"]="148.0.1.3"
	self.My_Host_To_IP_Mapping["148.0.1.3"]="H_34"



	self.My_Host_To_IP_Mapping["H_35"]="149.0.1.1"
	self.My_Host_To_IP_Mapping["149.0.1.1"]="H_35"
	self.My_Host_To_IP_Mapping["H_36"]="149.0.1.2"
	self.My_Host_To_IP_Mapping["149.0.1.2"]="H_36"
	self.My_Host_To_IP_Mapping["H_37"]="149.0.1.3"
	self.My_Host_To_IP_Mapping["149.0.1.3"]="H_37"
	self.My_Host_To_IP_Mapping["H_38"]="149.0.1.4"
	self.My_Host_To_IP_Mapping["149.0.1.4"]="H_38"

	#self.My_Host_To_IP_Mapping["H_39"]="150.0.1.1"
	#self.My_Host_To_IP_Mapping["150.0.1.1"]="H_39"
	#self.My_Host_To_IP_Mapping["H_40"]="150.0.1.2"
	#self.My_Host_To_IP_Mapping["150.0.1.2"]="H_40"
	#self.My_Host_To_IP_Mapping["H_41"]="150.0.1.3"
	#self.My_Host_To_IP_Mapping["150.0.1.3"]="H_41"

	#self.My_Host_To_IP_Mapping["H_42"]="151.0.1.1"
	#self.My_Host_To_IP_Mapping["151.0.1.1"]="H_42"
	#self.My_Host_To_IP_Mapping["H_43"]="151.0.1.2"
	#self.My_Host_To_IP_Mapping["151.0.1.2"]="H_43"
	#self.My_Host_To_IP_Mapping["H_44"]="151.0.1.3"
	#self.My_Host_To_IP_Mapping["151.0.1.3"]="H_44"
	#self.My_Host_To_IP_Mapping["H_45"]="151.0.1.4"
	#self.My_Host_To_IP_Mapping["151.0.1.4"]="H_45"

	self.My_Subnet_To_IP_Mapping={}
	self.My_Subnet_To_IP_Mapping["Sub_0"] = "140.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["140.0.1.0/24"] = "Sub_0"
	

	self.My_Subnet_To_IP_Mapping["Sub_1"] = "141.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["141.0.1.0/24"] = "Sub_1"
	
	self.My_Subnet_To_IP_Mapping["Sub_2"] = "142.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["142.0.1.0/24"] = "Sub_2"
	

	self.My_Subnet_To_IP_Mapping["Sub_3"] = "143.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["143.0.1.0/24"] = "Sub_3"
	
	self.My_Subnet_To_IP_Mapping["Sub_4"] = "144.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["144.0.1.0/24"] = "Sub_4"
	

	self.My_Subnet_To_IP_Mapping["Sub_5"] = "145.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["145.0.1.0/24"] = "Sub_5"

	self.My_Subnet_To_IP_Mapping["Sub_6"] = "146.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["146.0.1.0/24"] = "Sub_6"

	
	self.My_Subnet_To_IP_Mapping["Sub_7"] = "147.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["147.0.1.0/24"] = "Sub_7"

	self.My_Subnet_To_IP_Mapping["Sub_8"] = "148.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["148.0.1.0/24"] = "Sub_8"

	self.My_Subnet_To_IP_Mapping["Sub_9"] = "149.0.1.0/24"
	self.My_Subnet_To_IP_Mapping["149.0.1.0/24"] = "Sub_9"

	#self.My_Subnet_To_IP_Mapping["Sub_10"] = "150.0.1.0/24"
	#self.My_Subnet_To_IP_Mapping["150.0.1.0/24"] = "Sub_10"

	#self.My_Subnet_To_IP_Mapping["Sub_11"] = "151.0.1.0/24"
	#self.My_Subnet_To_IP_Mapping["151.0.1.0/24"] = "Sub_11"

	
	self.Subnet_To_Router_Mapping={}

	self.Subnet_To_Router_Mapping["Sub_0"]="R_0"
	self.Subnet_To_Router_Mapping["Sub_1"]="R_1"
	self.Subnet_To_Router_Mapping["Sub_2"]="R_2"
	self.Subnet_To_Router_Mapping["Sub_3"]="R_3"
	self.Subnet_To_Router_Mapping["Sub_4"]="R_4"
	self.Subnet_To_Router_Mapping["Sub_5"]="R_5"
	self.Subnet_To_Router_Mapping["Sub_6"]="R_6"
	self.Subnet_To_Router_Mapping["Sub_7"]="R_7"
	self.Subnet_To_Router_Mapping["Sub_8"]="R_8"
	self.Subnet_To_Router_Mapping["Sub_9"]="R_9"
	#self.Subnet_To_Router_Mapping["Sub_10"]="R_10"
	#self.Subnet_To_Router_Mapping["Sub_11"]="R_11"


	self.Router_To_Subnet_Mapping={}
	
	self.Router_To_Subnet_Mapping["R_0"]=["140.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_1"]=["141.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_2"]=["142.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_3"]=["143.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_4"]=["144.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_5"]=["145.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_6"]=["146.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_7"]=["147.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_8"]=["148.0.1.0/24"]
	self.Router_To_Subnet_Mapping["R_9"]=["149.0.1.0/24"]
	#self.Router_To_Subnet_Mapping["R_10"]=["150.0.1.0/24"]
	#self.Router_To_Subnet_Mapping["R_11"]=["151.0.1.0/24"]

	self.Subnet_IP_To_Router_Mapping={}
	self.Subnet_IP_To_Router_Mapping["140.0.1.0/24"]="R_0"
	self.Subnet_IP_To_Router_Mapping["141.0.1.0/24"]="R_1"
	self.Subnet_IP_To_Router_Mapping["142.0.1.0/24"]="R_2"
	self.Subnet_IP_To_Router_Mapping["143.0.1.0/24"]="R_3"
	self.Subnet_IP_To_Router_Mapping["144.0.1.0/24"]="R_4"
	self.Subnet_IP_To_Router_Mapping["145.0.1.0/24"]="R_5"
	self.Subnet_IP_To_Router_Mapping["146.0.1.0/24"]="R_6"
	self.Subnet_IP_To_Router_Mapping["147.0.1.0/24"]="R_7"
	self.Subnet_IP_To_Router_Mapping["148.0.1.0/24"]="R_8"
	self.Subnet_IP_To_Router_Mapping["149.0.1.0/24"]="R_9"
	#self.Subnet_IP_To_Router_Mapping["150.0.1.0/24"]="R_10"
	#self.Subnet_IP_To_Router_Mapping["151.0.1.0/24"]="R_11"
	
	self.Paths_Report={}
	self.TmpPathReport=[]
	

	self.Subnets=[[0,1,2,3],[4,5,6,7,8],[9,10,11,12,13],[14,15,16,17],[18,19,20],[21,22,23,24],[25,26,27],[28,29,30,31],[32,33,34],[35,36,37,38]]
    def float_round(self,num, places = 0, direction = floor):
    	return direction(num * (10**places)) / float(10**places)
    # handler for timer function that sends the requests to all the
    # switches connected to the controller.
    def _timer_func1 (self):
		for connection in core.openflow._connections.values():
			#print connection
			connection.send(of.ofp_stats_request(body=of.ofp_flow_stats_request()))
			#connection.send(of.ofp_stats_request(body=of.ofp_port_stats_request()))
			#print("Sent  flow/port stats request(s)"+str(connection.dpid))
    
    def Final_Paths_Suggestion(self,Subnet_To_Subnet,OurBestChoices,Subnet_To_Router_Mapping,Subnet_To_IP_Mapping):
    	ODPairs = []
    	#print type(Subnet_To_Subnet)
    	#print len(Subnet_To_Subnet)
    	#print Subnet_To_Subnet
    	for i in range(self.Number_Of_Routers):
        	for j in range(self.Number_Of_Routers):
			if i!=j:
				for key,val in Subnet_To_Router_Mapping.items():
					if "R_"+str(j)==val:
              					tmp1 = key.split("_")
						ODPairs.append((i, j, int(tmp1[1])))
	print "Inja"
    	print ODPairs
	print OurBestChoices
    	FinalResult = []
       	# Constrcut Topology for that OD-Pair and Find the Path
	MyTopo = nx.Graph()
        NodeList = [h for h in range(self.Number_Of_Routers)]
	#print NodeList
        MyTopo.add_nodes_from(NodeList)
    	# print "Ghabl ",ODPairs
    	for k in ODPairs:

        	
        	# print MyTopo.nodes()
        	for m in OurBestChoices:
            		if m[2] == k[2]:
				#print i
				#print i[0]
				#print i[1]
				#print type(i[0])
				node1=int(m[0])
				node2=int(m[1])
				#print node1,node2
				
                    		MyTopo.add_edge(node1, node2)
		#print k[0],k[1],k[2] 
		#print "Topo"
		#print MyTopo.edges() 
		if len(MyTopo.edges())>0:
			flag=False
			for i in MyTopo.edges():
				if k[0]==i[0] or k[0]==i[1]:
					#print k[0],k[1],k[2]
					#print i[0]
					flag=True
			if flag==True:
				#print "YESSSS"
				#print k
				#print MyTopo.edges()
				#print 
	        		tmpPath = nx.shortest_path(MyTopo, k[0], k[1])
				#if ODPairs[k][0]==4 and ODPairs[k][1]==5:


        			l = ()
        			PathSet = list(l)
        			for j in range(len(tmpPath) - 1):
                    			theTuple = ()
                    			ll = list(theTuple)
                    			ll.append(self.My_Routers["R_" + str(tmpPath[j])])
                    			ll.append(self.My_Routers["R_" + str(tmpPath[j + 1])])
                    			PathSet.append(tuple(ll))

        			FinalResult.append([PathSet, Subnet_To_IP_Mapping["Sub_" + str(k[2])]])
		MyTopo.remove_edges_from(MyTopo.edges())
	#print "KKK"
	#print FinalResult
    	return FinalResult
    def Set_hMatrix(self,Subnet_To_Subnet,Subnet_To_Router_Mapping):
    	#print "Dakhel"
    	#print Subnet_To_Subnet
    	hMatrix = [[0 for y in range(len(Subnet_To_Subnet))] for x in range(len(self.My_Routers))]
    	#print "INJAAA"
    	#print Subnet_To_Router_Mapping
    	for i in range(len(self.My_Routers)):
            	for j in range(len(Subnet_To_Subnet)):
                	Aggregated_Traffic = 0
                	for k in range(len(Subnet_To_Subnet)):
                        	if Subnet_To_Router_Mapping["Sub_" + str(k)] == "R_" + str(i):
					Aggregated_Traffic = Aggregated_Traffic + Subnet_To_Subnet[k][j]
                        	hMatrix[i][j] = Aggregated_Traffic
    	print "hMatrix"
    	print len(hMatrix), ' ', len(hMatrix[0])
    	print "Hereeeeeeeeeeee"
    	print hMatrix
    	return hMatrix

    def _handle_portstats_received(self,event):
        """
        Handler to manage port statistics received
        Args:
            event: Event listening to PortStatsReceived from openflow
        """
	#print	self.InitializationFinished
	#print 	self.Router_Port_Router
	self.Port_Stat_Get_Switches.append(event.connection.dpid)



        for f in event.stats:
            if int(f.port_no)<65534: # used from hosts and switches interlinks
                current_bytes = f.tx_bytes  # transmitted and received
                try:
                    last_bytes = self.switches_bw[int(event.connection.dpid)][int(f.port_no)]
                except:
                    last_bytes = 0
                estim_bw = (current_bytes - last_bytes)*8/(self.Sampling_Duration)
                estim_bw = float(format(estim_bw, '.2f'))
                if estim_bw > 0:
                    	#print pox.lib.util.dpidToStr(event.connection.dpid), f.port_no, estim_bw
			#if ("R_"+str(int(event.connection.dpid)),int(f.port_no)) in self.Router_Port_Router:
			#	self.Traffic_Usage.write("\n"+str("R_"+str(int(event.connection.dpid)))+"  "+str(self.Router_Port_Router[("R_"+str(int(event.connection.dpid)),int(f.port_no))])+" "+str(estim_bw)+"\n")
			#else:
			self.Traffic_Usage.write("\n"+str("R_"+str(int(event.connection.dpid)))+"  "+str(int(f.port_no))+" "+str(estim_bw)+"\n")	
	
		
		self.switches_bw[int(event.connection.dpid)][int(f.port_no)] = (f.tx_bytes)
	
		if len(self.Port_Stat_Get_Switches)==len(self.SwitchName_to_dpid):
			self.Port_Stat_Counter+=1
			self.Port_Stat_Get_Switches=[]
			self.Traffic_Usage.write("\n ******************************************\n")
		        self.Traffic_Usage.write(str(self.Port_Stat_Counter)+"\n")
	

    def _handle_flowstats_received (self,event):
	stats = flow_stats_to_list(event.stats)
	#print("FlowStatsReceived from %s: ", dpidToStr(event.connection.dpid))
	self.Flow_Stat_Get_Switches.append(dpidToStr(event.connection.dpid))
	#self.My_Test=open("/home/saeed/My_Test.txt","ab")
	# Get number of bytes/packets in flows for web traffic only
	flow_bytes = 0
	#web_flows = 0
	flow_packet = 0
	#print stats

	#print len(self.Flow_Stat_Get_Switches)
	#print len(self.SwitchName_to_dpid)
	ThisSwitchName=self.dpid_to_SwitchName[dpidToStr(event.connection.dpid)]
	#print "This Switch"
	#print ThisSwitchName
	#print 
	for f in event.stats:
		#print "KKKKKK\n"
		#print f.match.nw_src
		#print f.match.nw_dst
		#print 
		#print f.match
		#print f
		
		if str(f.match.nw_src) in self.My_Host_To_IP_Mapping  and str(f.match.nw_dst) in self.My_Host_To_IP_Mapping:
			#print str(f.match.nw_src)
			#Src=str(f['match']['nw_src']).replace('/32','')
			#Dst=str(f['match']['nw_dst']).replace('/32','')
			#MyPort=f['actions'][0]['port']
			Subnet_Src=ipaddress.IPv4Network(unicode(str(str(f.match.nw_src)+'/24')),strict=False)
			Subnet_Dst=ipaddress.IPv4Network(unicode(str(str(f.match.nw_dst)+'/24')),strict=False)
			
			TheDSTRouter=self.Subnet_IP_To_Router_Mapping[str(Subnet_Dst)]
			
			WhichPort=f.actions[0].port
			
			if ThisSwitchName!=TheDSTRouter:
				self.TmpPathReport.append([ThisSwitchName,str(f.match.nw_dst),self.Router_Port_Router[ThisSwitchName,WhichPort]])
			
			if  (dpidToStr(event.connection.dpid)==self.SwitchName_to_dpid[self.Subnet_To_Router_Mapping[self.My_Subnet_To_IP_Mapping[str(Subnet_Dst)]]]):
				#print f
				#print f['byte_count']
				#print type(f['byte_count'])
				index1=str(self.My_Host_To_IP_Mapping[str(f.match.nw_src)]).split("_")
				index2=str(self.My_Host_To_IP_Mapping[str(f.match.nw_dst)]).split("_")
				#print index1
				#print index2
				#print f['byte_count']

				self.Traffic_Matrix[int(index1[1])][int(index2[1])]=f.byte_count#We catch the flow stats to bytes 

	#If the data of all of the routers were collected then we can process the matrix
	#print len(self.Flow_Stat_Get_Switches)==len(self.SwitchName_to_dpid) 				
	if len(self.Flow_Stat_Get_Switches)==len(self.SwitchName_to_dpid):
		
		self.Traffic_Image_Counter+=1

		np.savetxt(self.Total_Byte_Count, self.Traffic_Matrix,header='Total Byte Count ::: The Image Number '+str(self.Traffic_Image_Counter),footer='\n',fmt='%15.3f')


		#Our Images Including Subnet_To_Subnet Image and Host_To_Host Image is also in bytes
		tmpArray=np.zeros((self.TotalNumOfHosts,self.TotalNumOfHosts),dtype=np.double)
		tmpArray=np.array(self.Traffic_Matrix)
		
		tmpDict=self.Traffic_Usage_On_Links.copy() 
		self.Traffic_Usage_Image[self.Traffic_Image_Counter]=tmpDict
		
		#Host_To_Host Traffic Image in Bytes
		self.HtH_Traffic_Image[self.Traffic_Image_Counter]=tmpArray
		#Subnet-To-Subnet Conversion
		Subnet_To_Subnet=np.zeros((self.Number_Of_Subnets,self.Number_Of_Subnets),dtype=np.double)
		for i in range(self.Number_Of_Subnets):
			for j in range(self.Number_Of_Subnets):
				if i!=j:
					traffic=0
					for hst1 in self.Subnets[i]:
						for hst2 in self.Subnets[j]:
							traffic+=tmpArray[hst1][hst2]
					Subnet_To_Subnet[i][j]=traffic
		#Subnet_To_Subnet Traffic Image in Bytes
			self.Traffic_Image[self.Traffic_Image_Counter]=Subnet_To_Subnet
		
		
				
		#b Current Subnet_To_Subnet Bandwidth Usage Matrix 
		b=np.divide((self.Traffic_Image[self.Traffic_Image_Counter]-self.Traffic_Image[self.Traffic_Image_Counter-1])*8,self.Sampling_Duration)
		#Current_HtH_BW is current Host_To_Host Bandwidth Usage Matrix
		Current_HtH_BW=np.divide((self.HtH_Traffic_Image[self.Traffic_Image_Counter]-self.HtH_Traffic_Image[self.Traffic_Image_Counter-1])*8, self.Sampling_Duration)
		self.Traffic_Matrix_File=open("/home/saeed/Traffic_Matrix.txt","ab")
		self.BW_Matrix_File=open("/home/saeed/BW_Matrix.txt","ab")
		np.savetxt(self.Traffic_Matrix_File, b,header='Subnet-To-Subnet Traffic::: The Image Number '+str(self.Traffic_Image_Counter),footer='\n',fmt='%15.3f')
		#np.savetxt(self.Traffic_Matrix_File, tmpArray ,header='Host To Host  '+str(self.Traffic_Image_Counter),footer='\n',fmt='%15.3f')
		np.savetxt(self.BW_Matrix_File, Current_HtH_BW ,header='Host-To-Host Traffic::: The Image Number '+str(self.Traffic_Image_Counter),footer='\n',fmt='%15.3f')
		self.Traffic_Matrix_File.close()
		self.BW_Matrix_File.close()

		#Here We should Send the BW Matrix to CPLEX If At least has one none zero element
		
		flag=False
		for h in range(len(b)):
			for k in range(len(b[0])):
					if b[h][k]>0:
						flag=True
						break
			else:
				continue
			break
		if flag==True:
			#In the first phase CPLEX should solve our LB formulation 
			ThisFlag=False
			ViolatedVal=0
			for i in range(len(b)):
				for j in range(len(b[0])):
					if b[i,j]*self.Scale_DownGrade>10000:
						ThisFlag=True
						ViolatedVal=b[i,j]*self.Scale_DownGrade
						break
				else:
					continue
				break
			if ThisFlag==True:
				print "***********************"
				#print tmpArray
				print "Violated Val ",ViolatedVal
				np.savetxt(self.My_Log, b,header='Subnet-To-Subnet Traffic::: The Image Number '+str(self.Traffic_Image_Counter),footer='\n',fmt='15.3f')
						
													
			else:	
				p1 = Process(target=self.Paths_Installation, args=(b,Current_HtH_BW))
				p1.start()
					
				
		
		self.Flow_Stat_Get_Switches=[]
		self.Traffic_Matrix=np.zeros((self.TotalNumOfHosts,self.TotalNumOfHosts),dtype=np.double)
		self.Traffic_Usage_On_Links={}


    def Paths_Installation(self,b,Current_HtH_BW):
						print "*** --- First Phase"
						
						
						My_H_Matrix=self.Set_hMatrix(b,self.Subnet_To_Router_Mapping)
						print  "1_H_Matrix sent to My_Formulation "
						New_H=[[x*self.Scale_DownGrade for x in y] for y in My_H_Matrix]
						for k in range(len(New_H)):
							for h in range(len(New_H[0])):
								if (h not in self.Subnets[k]) and New_H[k][h]==0:
									New_H[k][h]=self.Epsilon
						print New_H
						
						#MF=My_Formulation(New_H,self.Adj,self.Subnet_To_Router_Mapping)
						MF = LB_ILP_Opt_Last_Version1(New_H,self.Adj,self.Subnet_To_Router_Mapping,self.Capacity)
						OurBestChoices=MF.Problem_Solve()
						#OurBestChoices=MF.My_Formulation()
						Old_U=OurBestChoices.pop(0)
						OldResult=self.Final_Paths_Suggestion(b,OurBestChoices,self.Subnet_To_Router_Mapping,self.My_Subnet_To_IP_Mapping)
						print OldResult
						print Old_U
						print "LR"
						Main_Loop(self.Adj,self.Subnet_To_Router_Mapping,len(self.My_Routers),self.Number_Of_Subnets,self.Link_Base_Capacity,New_H)
						
							
						"""
						#Install The New Paths On each OFSwitch
						print "Injaaa"
						tmp_Modified_Paths=[]
						

						for fl in Result:
							if fl[1] in self.My_Subnet_To_IP_Mapping:#Means that Dst is Subnet not host, so extracting the destination hosts
								#print fl[1]
								Dst_Hosts=self.Extract_Hosts_Of_Subnet(fl[1])
								#print Dst_Hosts
								Src_Hosts=[]
								Src_Hosts=self.Extract_Hosts_Of_Router(self.My_Routers_Rev[fl[0][0][0]],self.Router_To_Subnet_Mapping)	
								Final_Src_Host_List=[]
								for s in Src_Hosts:
									for h in s:
										Final_Src_Host_List.append(h)
								#print fl
								#print Src_Hosts
								#print Dst_Hosts
								#print		
								tmpPath=[]
								NewPath=[]
								for pairs in fl[0]:
									tmpPath.append(self.My_Routers_Rev[pairs[0]])
									tmpPath.append(self.My_Routers_Rev[pairs[1]])
								#print tmpPath
								NewPath.append(tmpPath[0])
								for index in range(1,len(tmpPath)):
									if tmpPath[index]!=tmpPath[index-1]:
										NewPath.append(tmpPath[index])
								#NewPath.append(tmpPath[-1])	
								#print NewPath
								for hst1 in Final_Src_Host_List:
									for hst2 in Dst_Hosts: 
										#print [hst1,hst2,NewPath]
										tmp_Modified_Paths.append([hst1,hst2,NewPath])
						#print "All Paths Should be changed"
						#print tmp_Modified_Paths

						for pth1 in tmp_Modified_Paths:
							for pth2 in self.All_End_To_End_Paths:
								if pth1[0]==pth2[0] and pth1[1]==pth2[1]:
									pth2.pop(2)
									pth2.append(pth1[2])
						self.My_Log.write("\n"+str(self.All_End_To_End_Paths)+"\n")


						#print "All_HEREEEEEEEEEE"
						#print self.All_End_To_End_Paths
										
						#Install the New Paths On each OFSwitch
						# Installing Flows On each dpid
						
						print "Installing New Paths"
                    				for con in core.openflow.connections:
                       					#print "INJA"
                        				#print con
                        				#print con.dpid
                        				#print self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))]

                        				FlowList = self.Flows_For_Each_Router(self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))])
                        				#print "FlowList ", FlowList, "\n"

                        				for flow in FlowList:
                            					msg = of.ofp_flow_mod()
								msg.command=of.OFPFC_MODIFY_STRICT
                            					msg.priority = 100
                            					#msg.idle_timeout = 0
                            					#msg.hard_timeout = 0
                            					msg.match.dl_type = 0x0800
                            					msg.match.nw_src = IPAddr(flow[0])
                            					msg.match.nw_dst = IPAddr(flow[1])
                            					#print msg.match.nw_src
                            					#print msg.match.nw_dst
                            					msg.actions.append(of.ofp_action_output(port=flow[2]))
                            					con.send(msg)				
											
								

						
						#For the second phase extract the Max Flow in the Most Congested Link and again CPLEX tries to split this flow
						#First Change the Result to Router to Router format --> [('3.3.3.3', '1.1.1.1'), ('1.1.1.1', '4.4.4.4')], '143.0.1.0/24'] --> [(3, 1), (1, 4)], 'Sub_', 3, 40964.0]
						NewPaths=[]
						for i in range(len(b[0])):
					    		for j in range(len(b)):
								My_Dst=self.My_Subnet_To_IP_Mapping["Sub_"+str(i)]
								if b[j][i]>0:
					    				for entry in OldResult:
	
			        						if entry[1]==My_Dst and entry[0][0][0]==self.My_Routers[self.Subnet_To_Router_Mapping["Sub_"+str(j)]]:
			        		   					pairs = []
			        		    					for p in entry[0]:
			        		      				  		R1=-1
			        		      				  		R2=-1
			        		     				  		for key,val in self.My_Routers.items():
			        		          				  		if val== p[0]:
			        		              					  		tmp=key.split("_")
			        		              					  		R1=int(tmp[1])+1
			        		       				  		for key, val in self.My_Routers.items():
			        		           				  		if val== p[1]:
			        		               					  		tmp=key.split("_")
			        		                				  		R2=int(tmp[1])+1
			        			        		  		pairs.append((R1,R2))
			        			   				if len(pairs)>0:
			        			       			  		NewPaths.append([pairs,"Sub_",i,b[j][i]])
	
						NewPaths=sorted(NewPaths)
						NewPaths.sort(key=lambda x: x[3])
						FinalRes=[]
						print "FinalRes"
						for i in (NewPaths):
							if i not in FinalRes:
								FinalRes.append(i)
						for i in FinalRes:
							#for j in range(4):
							print i,
						print
						LinkCong= MF.Get_Link_Congestions()
						print "Congestion over Each Link "
						#Also at the same time We want to modify the link capacities and reduce Capaicty Matrix to available BW
						NewCapacity=np.zeros((self.Number_Of_Routers,self.Number_Of_Routers),dtype=np.double)
						Used_BW=np.zeros((self.Number_Of_Routers,self.Number_Of_Routers),dtype=np.double)
						max = 0.0
						pair = [] 
						for key, val in LinkCong.items():
	    						print key, ' ', val
							
	    						if val > max:
								pair = []
								pair.append(key)
								max = val
						#print pair
						print int(pair[0][0])+1,' ',int(pair[0][1])+1, ' ', max
						OldMostCongested=(int(pair[0][0])+1,int(pair[0][1])+1)
						OldMostCongestedValue=max
					
						#Now we know most congested link, First we should extract the flow with high bandwidth usage
						MaxFlow=0
						DstOFMaxFlow=-1
						MaxFlow_Path=[]
						for flow in FinalRes:
	    						if OldMostCongested in flow[0]:
								print flow
								if flow[3]>MaxFlow:
									MaxFlow_Path=[]
									MaxFlow_Path=flow[0][:]
			    						MaxFlow=flow[3]
			    						DstOFMaxFlow=flow[2]
	
						print MaxFlow, DstOFMaxFlow , MaxFlow_Path
						#In this part we should remove all of the flows to DstOFMaxFlow by returning their capacity to LinkCong -- So we free up the BW of DstOFMaxFlow
						for entry in FinalRes:
							if entry[2]==DstOFMaxFlow:
								for LinkPath in entry[0]:
									for key,val in LinkCong.items():
										if (LinkPath[0]-1)==int(key[0]) and (LinkPath[1]-1)==int(key[1]):
											LinkCong[key]=val-(entry[3]*self.Scale_DownGrade)
											#if LinkCong[key]<1:
											#	LinkCong[key]=0
						for key, val in LinkCong.items():
	    						print key, ' ', val
						for key, val in LinkCong.items():
							Router1=int(key[0])
							Router2=int(key[1])
							NewCapacity[Router1,Router2]=self.Capacity[Router1,Router2]-val
							Used_BW[Router1,Router2]=val



	
						#First Extracting the Hosts of The DstOFMaxFlow -- Dividing to two subnets means that we should reroute the hosts of DstOFMaxFlow-- We know that we should divide by two but we don't know the division point --  For example DstOFMaxFlow has n hosts -- We should divide this subnet into two subnets -- So first we extract the amount of traffic each host of DstOFMaxFlow receive -- Then we remove all the traffic towards DstOFMaxFlow -- The total amount of the first part should be less than half of the total traffic goes to this subnet 
						MyOptions=[]
						for hst,ipadd in self.My_Host_To_IP_Mapping.items():
							tmp=hst.split("_")
							if tmp[0]=="H":#Means that It's a Host Name
								Subnet_Of_Host=ipaddress.IPv4Network(unicode(ipadd+'/24'),strict=False)
								#print "ABABA"
								#print Subnet_Of_Host
								#print self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)]
								#print str(Subnet_Of_Host)
								if str(Subnet_Of_Host)==self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)]:
									#BW Usage to this Host
									sum=0
									for i in range(len(Current_HtH_BW)):
										sum+=Current_HtH_BW[i,int(tmp[1])]
									MyOptions.append([ipadd,sum])
						print "MyOptions"					
						print MyOptions
						MyOptions.sort(key=lambda x: x[0])
						#print "Sorted "
						#print MyOptions
						#Now Dividing MyOptions 
						
						#tmpSum=0
						#for i in MyOptions:
						#	if tmpSum+i[1]<=MaxFlow/2:
						#		FirstPart.append(i[0])
						#		tmpSum+=i[1]
						#	else:
						#		SecondPart.append(i[0])
						#		tmpSum+=i[1]
						
						#Now Checking the Splitting Cost for each Splitting patter
						Splitting_Patterns=[]
						for index in range(len(MyOptions)+1):
							tmpFirst_Part=[]
							tmpSecond_Part=[]
							tmp1=MyOptions[0:index]
							tmp2=MyOptions[index:len(MyOptions)]
							
							for item in tmp1:
								tmpFirst_Part.append(item[0])
							for item in tmp2:
								tmpSecond_Part.append(item[0])
							#print "tmpFirst_Part"
							#print tmpFirst_Part
							#print "tmpSecond_Part"
							#print tmpSecond_Part
							Splitting_Patterns.append(self.Splitting_MaxFlow(MaxFlow_Path,tmpFirst_Part,tmpSecond_Part,Current_HtH_BW))
						#print "Splitting_Patterns"
						print Splitting_Patterns
						#Choosing between the splitting patterns ... The one with the least distance to 0.5 is our Best Choice

						dist=1
						for spl in Splitting_Patterns:
							if abs((spl[0]/MaxFlow)-0.5)<dist:
								dist=abs((spl[0]/MaxFlow)-0.5)
								My_Choice=spl
						print "Our Best Splitting Choice"
						print My_Choice
						FirstPart=My_Choice[2]
						SecondPart=My_Choice[3]

						print "FirstPart"
						print FirstPart
						print "SecondPart"
						print SecondPart
						
						self.My_Final_Result=open("/home/saeed/My_Final_Result.txt","ab")
						self.My_Final_Result.write("\n"+str(MaxFlow)+"\n")
						#self.My_Final_Result.write("\n"+str(Max_Flow_Split1)+"\n")
						#self.My_Final_Result.write("\n"+str(Max_Flow_Split2)+"\n")
						self.My_Final_Result.write("Split1\n"+str(My_Choice[0])+"\n")
						self.My_Final_Result.write("Split2\n"+str(My_Choice[1])+"\n")
						self.My_Final_Result.write("The Splitting Percent\n"+str(My_Choice[0]/MaxFlow)+"\n"+str(My_Choice[1]/MaxFlow)+"\n")
						self.My_Final_Result.close()

						#Now we should extract that How much each subnet send to these two groups
						FirstPart_Traffic=np.zeros(( self.Number_Of_Subnets+1, 1), dtype=np.double)
						SecondPart_Traffic=np.zeros((self.Number_Of_Subnets+1, 1), dtype=np.double)
						#For the FirstPart
						for ips in FirstPart:
						
							#Extract the Host Index
							Host_Name=self.My_Host_To_IP_Mapping[ips]
							tmp1=Host_Name.split("_")
							Host_Index=int(tmp1[1])
							for index in range(self.TotalNumOfHosts):
								if Current_HtH_BW[index,Host_Index]>0:
									#This host belongs to which subnet
									#Extract the Subnet
									Subnet_Of_Host=ipaddress.IPv4Network(unicode(self.My_Host_To_IP_Mapping["H_"+str(index)]+'/24'),strict=False)
									Subnet_Name=self.My_Subnet_To_IP_Mapping[str(Subnet_Of_Host)]
									tmp2=Subnet_Name.split("_")
									Subnet_Index=int(tmp2[1])
									if Subnet_Index<=DstOFMaxFlow:
										FirstPart_Traffic[Subnet_Index,0]+=Current_HtH_BW[index,Host_Index]
									else:
										FirstPart_Traffic[Subnet_Index+1,0]+=Current_HtH_BW[index,Host_Index]
						#For the SecondPart
						for ips in SecondPart:
						
							#Extract the Host Index
							Host_Name=self.My_Host_To_IP_Mapping[ips]
							tmp1=Host_Name.split("_")
							Host_Index=int(tmp1[1])
							Traffic_To_ThisHost=0
							for index in range(self.TotalNumOfHosts):
								if Current_HtH_BW[index,Host_Index]>0:
									#This host belongs to which subnet
									#Extract the Subnet
									Subnet_Of_Host=ipaddress.IPv4Network(unicode(self.My_Host_To_IP_Mapping["H_"+str(index)]+'/24'),strict=False)
									Subnet_Name=self.My_Subnet_To_IP_Mapping[str(Subnet_Of_Host)]
									tmp2=Subnet_Name.split("_")
									Subnet_Index=int(tmp2[1])
									if Subnet_Index<=DstOFMaxFlow:
										SecondPart_Traffic[Subnet_Index,0]+=Current_HtH_BW[index,Host_Index]
									else:
										SecondPart_Traffic[Subnet_Index+1,0]+=Current_HtH_BW[index,Host_Index]

						#Adding Epsilon to FirstPart and SecondPart

						for el in range(self.Number_Of_Subnets+1):
							if FirstPart_Traffic[el,0]==0:
								FirstPart_Traffic[el,0]=self.Epsilon
							if SecondPart_Traffic[el,0]==0:
								SecondPart_Traffic[el,0]=self.Epsilon
						print "FirstPart_Traffic"
						print FirstPart_Traffic
						print "SecondPart_Traffic"
						print SecondPart_Traffic
					
						#LinkCong2=list(LinkCong)
		
						#Transforming Aggregated Matrix from n*2n  to n*(2*n+1) just dividing the max traffic by two so we add one column more to divide
	
						MyNewArray=np.zeros(( self.Number_Of_Subnets+1, self.Number_Of_Subnets+1), dtype=np.double)
						tmpMyNewArray=np.zeros(( self.Number_Of_Subnets+1, self.Number_Of_Subnets+1), dtype=np.double)
						
						for index1 in range(self.Number_Of_Subnets):
	    						for index2 in range(self.Number_Of_Subnets):
								if index2<DstOFMaxFlow :
			    						tmpMyNewArray[index1,index2]=b[index1,index2]
								if index2>DstOFMaxFlow:
			    						tmpMyNewArray[index1,index2+1]=b[index1,index2]
						for index1 in range(self.Number_Of_Subnets):
	    						for index2 in range(self.Number_Of_Subnets):
								if index1<=DstOFMaxFlow :
			    						MyNewArray[index1,index2]=tmpMyNewArray[index1,index2]
								if index1>DstOFMaxFlow:
			    						MyNewArray[index1+1,index2]=tmpMyNewArray[index1,index2]
						
						for index1 in range(self.Number_Of_Subnets+1):
							MyNewArray[index1, DstOFMaxFlow] = FirstPart_Traffic[index1, 0]
							MyNewArray[index1, DstOFMaxFlow + 1] = SecondPart_Traffic[index1, 0]
							MyNewArray[index1,index1]=0
	
					
	
						for i in range(len(MyNewArray)):
	    						for j in range(len(MyNewArray[0])):
								#print '{:10}'.format(str(self.Demand[i][j])),
								print str(MyNewArray[i][j])+"   \"",
	    						print
						print
	
						for i in range(len(b)):
	    						for j in range(len(b[0])):
								#print '{:10}'.format(str(self.Demand[i][j])),
	       							print str(b[i][j])+"   \"",
	    						print
					
						#We divided the traffic Volume for DstOFMaxFlow but we didn't determine the Subnet Index , It means that if we have two parts, which hosts are in the first subnet and which one in the second

						#Giving this MyNewArray to CPLEX
						New_My_Subnet_To_IP_Mapping = {}
						#Shifting the Symbols
						#Constructing New_My_Subnet_To_IP_Mapping
											
						for key,val in self.My_Subnet_To_IP_Mapping.items():
	    						if "Sub" in key:
								tmp=key.split("_")
								if int(tmp[1])<DstOFMaxFlow:
			    						New_My_Subnet_To_IP_Mapping[key]=val
			    						New_My_Subnet_To_IP_Mapping[val]=key
								if int(tmp[1])==DstOFMaxFlow:
			    						New_My_Subnet_To_IP_Mapping[key] = "X1"
			    						New_My_Subnet_To_IP_Mapping["X1"] = key
			   						New_My_Subnet_To_IP_Mapping["Sub_"+str(int(tmp[1]) + 1)] = "X2"
			    						New_My_Subnet_To_IP_Mapping["X2"] = "Sub_"+str(int(tmp[1]) + 1)
								if int(tmp[1])>DstOFMaxFlow:
			    						New_My_Subnet_To_IP_Mapping["Sub_"+str(int(tmp[1]) + 1)] = val
			    						New_My_Subnet_To_IP_Mapping[val] = "Sub_"+str(int(tmp[1]) + 1)
	
						#print "Here"
						#print self.My_Subnet_To_IP_Mapping
						#print New_My_Subnet_To_IP_Mapping
	
	
						#Constructing New_Router_To_Subnet_Mapping
	
						New_Router_To_Subnet_Mapping={}
	
	
	
						#print self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)]
						for key,val in self.Router_To_Subnet_Mapping.items():
	    						#print val
	    						if self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)] in val:
								#val.remove(self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)])
								#val.append("X1")
								#val.append("X2")
								newVal=[]
								for subn in val:
									if subn!=self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)]:
										newVal.append(subn)
								newVal.append("X1")
								newVal.append("X2")
								New_Router_To_Subnet_Mapping[key]=newVal
	    						else:
								New_Router_To_Subnet_Mapping[key]=val
						#print "R2S"

						#print New_Router_To_Subnet_Mapping
	
						#Constructing New_Subnet_To_Router_Mapping
						New_Subnet_To_Router_Mapping={}
						for key,val in New_Router_To_Subnet_Mapping.items():
	    						for ips in val:
								#print ips
	       							#print New_My_Subnet_To_IP_Mapping[ips]
								New_Subnet_To_Router_Mapping[New_My_Subnet_To_IP_Mapping[ips]]=key
	
						#print New_Subnet_To_Router_Mapping
	
						print "*** --- Second Phase"
						My_H_Matrix=self.Set_hMatrix(MyNewArray,New_Subnet_To_Router_Mapping)
						print  "2_H_Matrix sent to My_Formulation "
						New_H=[[x*self.Scale_DownGrade for x in y] for y in My_H_Matrix]
						print New_H
						
						print "NewCapacity"
						print NewCapacity
						print "Used BW"
						print Used_BW
						
						MF=LB_ILP_Opt_Last_Version2(New_H,self.Adj,New_Subnet_To_Router_Mapping,self.Capacity,Used_BW)
						OurBestChoices=MF.Problem_Solve()
						print "CPLEX"
						print OurBestChoices
						#print "GLPK"
						#MF=My_Formulation(New_H,self.Adj,New_Subnet_To_Router_Mapping,NewCapacity,Used_BW)
						#OurBestChoices2=MF.My_Formulation()
						#print OurBestChoices2
						
						New_U=OurBestChoices.pop(0)

						print "Old_U vs New_U"
						print Old_U
						print New_U
						#print "Rounded"
						#print self.float_round(Old_U, 3)
						#print self.float_round(New_U, 3)
						#print "Difference"
						#print Old_U-New_U
						
						NewResult=self.Final_Paths_Suggestion(MyNewArray,OurBestChoices,New_Subnet_To_Router_Mapping,New_My_Subnet_To_IP_Mapping)
						

						#Here we should remove the paths which is going to change in NewResult (Removing Duplicated Paths between Old and New)
						New_OldResult=[]
					    	for entry in OldResult:
							if entry[1]!=self.My_Subnet_To_IP_Mapping["Sub_"+str(DstOFMaxFlow)]:
								New_OldResult.append(entry)
						print "New Old Result --- After removing Duplicated Paths"
						print New_OldResult


						print "New Result"
						print NewResult
						#In this step we should add the NewResult to OldResult and calculate the Most Congested Link again
						#First Extract the congestion of each link 
						LinkCong2= MF.Get_Link_Congestions()
						print "Congestion over Each Link New Capacity"
						for key, val in LinkCong2.items():
	    						print key, ' ', val
						#We add the new congestion to old congestion over each link and then extract the most congested link
						for key1, val1 in LinkCong2.items():
							for key2, val2 in LinkCong.items():
								if key1[0]==key2[0] and key1[1]==key2[1]:
									LinkCong[key2]=val1+val2
						
						NewMostCongestedValue = 0.0
						NewMostCongested = [] 
						for key, val in LinkCong.items():
	    						print key, ' ', val
							
	    						if val > NewMostCongestedValue:
								NewMostCongested = []
								NewMostCongested.append(key)
								NewMostCongestedValue = val
						#print pair
						#New Most Congested Link and Value
						print "Old && New Most Congested Link and Its Value"
						print "Old Most Congested "
						print OldMostCongested 
						print OldMostCongestedValue
						print "New Most Congested"
						print NewMostCongested
						print NewMostCongestedValue
						self.My_Final_Result=open("/home/saeed/My_Final_Result.txt","ab")
						self.My_Final_Result.write("\n"+str(self.Traffic_Image_Counter)+"\nOld U "+str(OldMostCongestedValue*self.Scale_DownGrade)+"\nNew U "+str(NewMostCongestedValue*self.Scale_DownGrade)+"\n Improvement \n"+str((OldMostCongestedValue*self.Scale_DownGrade)-(NewMostCongestedValue*self.Scale_DownGrade))+"\n")
						self.My_Final_Result.close()

						

						if NewMostCongestedValue<OldMostCongestedValue:				
							#First Append the Old Result to New Result
							for item in NewResult:
								New_OldResult.append(item)
							print "Final Result"
							print New_OldResult
							self.My_Test=open("/home/saeed/My_Test.txt","ab")
							self.My_Test.write("\n"+str(OldMostCongested)+"\n")
							self.My_Test.write("\n"+str(NewMostCongested)+"\n")
							myoutput2=[]
							for p in New_OldResult:
								myoutput1=[]
								for q in p[0]:
									myoutput1.append(self.My_Routers_Rev[q[0]])
								myoutput1.append(self.My_Routers_Rev[p[0][-1][1]])
								myoutput2.append([myoutput1,p[1]])
							self.My_Test.write("\n"+str(myoutput2)+"\n")
							self.My_Test.write("\n X1 "+str(FirstPart)+"\n")
							self.My_Test.write("\n X2 "+str(SecondPart)+"\n")
							self.My_Test.write("\n ------------------------------------------------------------- \n")
							self.My_Test.close()
	
				
							#After that the results should be given to POX to reroute the traffic

						
							#Install The New Paths On each OFSwitch
							print "Injaaa"	
							tmp_Modified_Paths=[]
							for fl in New_OldResult:
								
								if fl[1]=="X1":
									Dst_Hosts=list(FirstPart)
									Src_Hosts=[]
									Src_Hosts=list(self.Extract_Hosts_Of_Router(self.My_Routers_Rev[fl[0][0][0]],New_Router_To_Subnet_Mapping))
									Final_Src_Host_List=[]
									for s in Src_Hosts:
										for h in s:
											Final_Src_Host_List.append(h)
									#print fl
									#print Src_Hosts
									#print Dst_Hosts
									#print		
									tmpPath=[]
									NewPath=[]
									for pairs in fl[0]:
										tmpPath.append(self.My_Routers_Rev[pairs[0]])
										tmpPath.append(self.My_Routers_Rev[pairs[1]])
									#print tmpPath
									NewPath.append(tmpPath[0])
									for index in range(1,len(tmpPath)):
										if tmpPath[index]!=tmpPath[index-1]:
											NewPath.append(tmpPath[index])
									#NewPath.append(tmpPath[-1])	
									#print NewPath
									#self.My_Log.write("\nX1SrcHost\n"+str(self.My_Routers_Rev[fl[0][0][0]])+"\n")
									#self.My_Log.write("\nX1SrcHost\n"+str(Final_Src_Host_List)+"\n")
									#self.My_Log.write("\nX1DstHosts\n"+str(Dst_Hosts)+"\n")
									for hst1 in Final_Src_Host_List:
										for hst2 in Dst_Hosts: 
											#print [hst1,hst2,NewPath]
											tmp_Modified_Paths.append([hst1,hst2,NewPath])	

								elif fl[1]=="X2":
							
									Dst_Hosts=list(SecondPart)
									Src_Hosts=[]
									Src_Hosts=list(self.Extract_Hosts_Of_Router(self.My_Routers_Rev[fl[0][0][0]],New_Router_To_Subnet_Mapping))
									Final_Src_Host_List=[]
									for s in Src_Hosts:
										for h in s:
											Final_Src_Host_List.append(h)
									#print fl
									#print Src_Hosts
									#print Dst_Hosts
									#print		
									tmpPath=[]
									NewPath=[]
									for pairs in fl[0]:
										tmpPath.append(self.My_Routers_Rev[pairs[0]])
										tmpPath.append(self.My_Routers_Rev[pairs[1]])
									#print tmpPath
									NewPath.append(tmpPath[0])
									for index in range(1,len(tmpPath)):
										if tmpPath[index]!=tmpPath[index-1]:
											NewPath.append(tmpPath[index])
									#NewPath.append(tmpPath[-1])	
									#print NewPath
									self.My_Log.write("\nX2SrcHost\n"+str(self.My_Routers_Rev[fl[0][0][0]])+"\n")
									self.My_Log.write("\nX2SrcHost\n"+str(Final_Src_Host_List)+"\n")
									self.My_Log.write("\nX2DstHosts\n"+str(Dst_Hosts)+"\n")
									for hst1 in Final_Src_Host_List:
										for hst2 in Dst_Hosts: 
											#print [hst1,hst2,NewPath]
											tmp_Modified_Paths.append([hst1,hst2,NewPath])	
								elif fl[1] in New_My_Subnet_To_IP_Mapping:#Means that Dst is Subnet not host, so extracting the destination hosts
									Dst_Hosts=self.Extract_Hosts_Of_Subnet(fl[1])
									Src_Hosts=[]
									Src_Hosts=list(self.Extract_Hosts_Of_Router(self.My_Routers_Rev[fl[0][0][0]],New_Router_To_Subnet_Mapping))
									Final_Src_Host_List=[]
									for s in Src_Hosts:
										for h in s:
											Final_Src_Host_List.append(h)
									#print fl
									#print Src_Hosts
									#print Dst_Hosts
									#print		
									tmpPath=[]
									NewPath=[]
									for pairs in fl[0]:
										tmpPath.append(self.My_Routers_Rev[pairs[0]])
										tmpPath.append(self.My_Routers_Rev[pairs[1]])
									#print tmpPath
									NewPath.append(tmpPath[0])
									for index in range(1,len(tmpPath)):
										if tmpPath[index]!=tmpPath[index-1]:
											NewPath.append(tmpPath[index])
									#NewPath.append(tmpPath[-1])	
									#print NewPath
									#self.My_Log.write("\nBasicSrcHost\n"+str(self.My_Routers_Rev[fl[0][0][0]])+"\n")
									#self.My_Log.write("\nBasicSrcHost\n"+str(New_Router_To_Subnet_Mapping)+"\n")
									#self.My_Log.write("\nBasicSrcHost\n"+str(Src_Hosts)+"\n")
									#self.My_Log.write("\nBasicDstHosts\n"+str(Dst_Hosts)+"\n")
									for hst1 in Final_Src_Host_List:
										for hst2 in Dst_Hosts: 
											#print [hst1,hst2,NewPath]
											tmp_Modified_Paths.append([hst1,hst2,NewPath])

							#self.My_Log.write("\n"+str(self.All_End_To_End_Paths)+"\n")
							#self.My_Log.write("\n TMP \n"+str(tmp_Modified_Paths)+"\n")
							#print "All Paths Should be changed"
							#print
							#print tmp_Modified_Paths
							#self.All_End_To_End_Paths=[]
							#self.All_End_To_End_Paths=tmp_Modified_Paths[:]
							for pth1 in tmp_Modified_Paths:
								for pth2 in self.All_End_To_End_Paths:
									if pth1[0]==pth2[0] and pth1[1]==pth2[1]:
										pth2[2]=[]
										pth2[2]=pth1[2]										
										#for item in pth1:
										#	pth2.append(item)
										#pth2.append(pth1[2])
							#self.My_Log.write("\n \n"+str(self.All_End_To_End_Paths)+"\n")
							#self.My_Log.write("\n \n"+str(self.Router_Port_Router)+"\n")
							#self.My_Log.write("\n \n"+str(self.Router_To_Router_Ports)+"\n")
							#print "All_HEREEEEEEEEEE"
							#print
							#print self.All_End_To_End_Paths
										
							#Install the New Paths On each OFSwitch
							# Installing Flows On each dpid
							print "Installing New Paths"
							print core.openflow.connections
                    					for con in core.openflow.connections:
                       						#print "INJA"
                        					#print con
                        					#print con.dpid
                        					#print self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))]

                        					FlowList = self.Flows_For_Each_Router(self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))])
                        					#print "FlowList ", FlowList, "\n"
								#self.My_Log.write("\n "+str(self.dpid_to_mac(con.dpid))+"\n")
								#self.My_Log.write("\n "+str(FlowList)+"\n\n")

                        					for flow in FlowList:
                            						msg = of.ofp_flow_mod()
									msg.command=of.OFPFC_MODIFY_STRICT
                            						msg.priority = 100
                            						msg.idle_timeout = 0
                            						msg.hard_timeout = 0
                            						msg.match.dl_type = 0x0800
                            						msg.match.nw_src = IPAddr(flow[0])
                            						msg.match.nw_dst = IPAddr(flow[1])
                            						#print msg.match.nw_src
                            						#print msg.match.nw_dst
                            						msg.actions.append(of.ofp_action_output(port=int(flow[2])))
                            						con.send(msg)
									#time.sleep(0.5)		
								#self.My_Log.write("\n"+"-----------------------------------------------------------------------"+"\n")



						"""

    def Splitting_MaxFlow(self,MaxFlow_Path,FirstPart,SecondPart,Current_HtH_BW):

	#Here We want to check If the MaxFlow in Most_Congested_Link is being splitted or not ???
	#Just we need to extract the H2H flows over the path OldMostCongested and we want to know MaxFlow is splitted or not
	#The pattern is like this [[(2, 1)], 'Sub_', 0, 24817482.346666668], so SRC and DST node is clear
	#First we extract Hosts of SRC and DST and check which H2H flows getting involved in MaxFlow in MCL
	#1- Extract the Hosts of SRC
	MaxFlowSrc=MaxFlow_Path[0][0]
	MaxFlowDst=MaxFlow_Path[-1][-1]
	Src_Hosts=self.Extract_Hosts_Of_Router("R_"+str(MaxFlowSrc-1),self.Router_To_Subnet_Mapping)
	Dst_Hosts=self.Extract_Hosts_Of_Router("R_"+str(MaxFlowDst-1),self.Router_To_Subnet_Mapping)
	#print "SRC*****DST"
	#print Src_Hosts
	#print Dst_Hosts
	Final_Src_Host_List=[]
	for s in Src_Hosts:
		for h in s:
			#Convert to Host_Number --> self.My_Host_To_IP_Mapping["145.0.1.1"]="H_21"
			tmp=self.My_Host_To_IP_Mapping[h]
			Host_Index=tmp.split("_")
			Final_Src_Host_List.append(int(Host_Index[1]))
	Final_Dst_Host_List=[]
	for s in Dst_Hosts:
		for h in s:
			#Convert to Host_Number --> self.My_Host_To_IP_Mapping["145.0.1.1"]="H_21"
			tmp=self.My_Host_To_IP_Mapping[h]
			Host_Index=tmp.split("_")
			Final_Dst_Host_List.append(int(Host_Index[1]))

	print Final_Src_Host_List
	print Final_Dst_Host_List
	#2- Now we can check that from which src hosts to dst hosts there is a traffic -- just we want the dst hosts
	Traffic_Over_MaxFlow=[]
	for srchst in Final_Src_Host_List:
		for dsthst in Final_Dst_Host_List:
			Traffic_Over_MaxFlow.append([self.My_Host_To_IP_Mapping["H_"+str(srchst)],self.My_Host_To_IP_Mapping["H_"+str(dsthst)],Current_HtH_BW[srchst,dsthst]])
	#print "Traffic_Over_MaxFlow"
	#print Traffic_Over_MaxFlow	
	#print "Inja1"
	#print FirstPart
	#print "Inja2"
	#print SecondPart
	#3- Now I want to answer this question that How much percent of the MaxFlow Traffic has been splitted?
	Max_Flow_Split1=[]
	Max_Flow_Split2=[]
	Max_Flow_Split1_Traf_Volume=0
	Max_Flow_Split2_Traf_Volume=0
	for entry in Traffic_Over_MaxFlow:
		if entry[1] in FirstPart:
			Max_Flow_Split1.append([entry[0],entry[1]])
			Max_Flow_Split1_Traf_Volume+=entry[2]
		if entry[1] in SecondPart:
			Max_Flow_Split2.append([entry[0],entry[1]])
			Max_Flow_Split2_Traf_Volume+=entry[2]		
	return [Max_Flow_Split1_Traf_Volume,Max_Flow_Split2_Traf_Volume,FirstPart,SecondPart]


    def Extract_Hosts_Of_Subnet(self,subnet):
	MyHosts=[]
	for hostname,ip in self.My_Host_To_IP_Mapping.items():# For each Host we should check It's belong the subnet ..
			a=hostname.split("_")
			#print a[0]
			if a[0]!="H":#Means that It's an IP Address ...
				Subnet_Of_Host=ipaddress.IPv4Network(unicode(hostname+'/24'),strict=False)
				#print str(subnet)==str(Subnet_Of_Host)
				if str(subnet)==str(Subnet_Of_Host):
					MyHosts.append(hostname)
	#print MyHosts
	return MyHosts
    def Extract_Hosts_Of_Router(self,RouterName,Router_To_Subnet_Mapping):
	#Convert the Router Name self.My_Routers["R_0" ] ="1.1.1.1"
	
	#Extract the Subnets
	MySubnets=Router_To_Subnet_Mapping[RouterName]
	#print MySubnets
	#Which Hosts Belongs to this Subnet
	if MySubnets[0]=="X1" and MySubnets[1]=="X2":
		MySubnets=self.Router_To_Subnet_Mapping[RouterName]
	MyHosts_In_Router=[]
	for subnet in MySubnets:
		MyHosts_In_Router.append(self.Extract_Hosts_Of_Subnet(subnet))
	return MyHosts_In_Router
							
		
    def _handle_LinkEvent(self, event):

        l = event.link
        sw1 = l.dpid1
	#print "HALA"
	#print sw1
	#print int(sw1)
	#print
        if self.dpid_to_mac(sw1) not in self.dpid_to_SwitchName:
            self.dpid_to_SwitchName[str(self.dpid_to_mac(sw1))] = "R_" + str(int(sw1)-1)
        # print self.dpid_to_mac(sw1)
        sw2 = l.dpid2
        if self.dpid_to_mac(sw2) not in self.dpid_to_SwitchName:
            self.dpid_to_SwitchName[str(self.dpid_to_mac(sw2))] = "R_" + str(int(sw2)-1)

        if (self.dpid_to_mac(sw1), self.dpid_to_mac(sw2)) not in self.Router_To_Router_Ports:
            self.Router_To_Router_Ports[(self.dpid_to_SwitchName[str(self.dpid_to_mac(sw1))],
                                         self.dpid_to_SwitchName[str(self.dpid_to_mac(sw2))])] = (l.port1, l.port2)
	    self.Router_Port_Router[(self.dpid_to_SwitchName[str(self.dpid_to_mac(sw1))],l.port1)]=str(self.dpid_to_SwitchName[str(self.dpid_to_mac(sw2))])
        self.LinkCounter += 1
        
        # If LinkCounter=2*NumbOfLinks then install Flows
        if self.LinkCounter == 2 * self.TotalNumOfLinks:
	    print "Router to port"
	    print self.Router_Port_Router
	    self.Traffic_Usage.write("Router_To_Router_Ports\n")
	    self.Traffic_Usage.write(str(self.Router_To_Router_Ports)+"\n")
            self.InitializationFinished = True

    def ReadPaths(self):
        # Read the Paths
        Tmp2 = []
        Paths_File = open("/home/saeed/paths5.txt", "r")
        Tmp1 = Paths_File.readlines()
        print Tmp1, "\n"
        for parts in Tmp1:
            Tmp2.append(parts.rstrip())
        print Tmp2
        print "\n"

        for parts in Tmp2:
            self.All_Shortest_Paths.append(parts.split(' '))
        print "ALL SHORTEST PATHS ", self.All_Shortest_Paths, "\n"

    def _handle_ConnectionUp(self, event):

        # remember the connection dpid for switch

        # self.sendTableStatsRequest(event)
        print "ConnectionUp: ", dpidToStr(event.connection.dpid)
        self.MydpIds.append(event.connection.dpid)

  

    def End_To_End_Paths_Extraction(self):
        # global Host_To_Router,All_End_To_End_Paths,Host_To_Router_Ports
	print "E2E"
	print self.Host_To_Router
        for ip1, sw1 in self.Host_To_Router.items():
            for ip2, sw2 in self.Host_To_Router.items():
                if ip1 != ip2:
                    for sp in self.All_Shortest_Paths:
                        if sp[0] == sw1 and sp[len(sp) - 1] == sw2:
                            self.All_End_To_End_Paths.append([ip1, ip2, sp])
        print 'All Paths ',self.All_End_To_End_Paths,'\n'

    def Flows_For_Each_Router(self, router):
        # global 	All_End_To_End_Paths,Router_To_Router_Ports
        FlowList = []
        # print "Flow For Router ",router,"\n"
        # print "All End To End Paths ",self.All_End_To_End_Paths,"\n"
	#print "Router"
	#print router
	#print "Host_To_Router"
	#print self.Host_To_Router_Ports
	#print
        for eachPath in self.All_End_To_End_Paths:
	    corepath=[]
	    for i in eachPath[2]:
		corepath.append(i)
            #corepath = eachPath[2]#Path
            for index in range(len(corepath)-1):
                if corepath[index] == router:
                    #if index < len(corepath) - 1:	
                    FlowList.append([eachPath[0], eachPath[1], self.Router_To_Router_Ports[router, corepath[index + 1]][0]])
                    #elif index == len(corepath) - 1:
			#if (eachPath[1], router) not in self.Host_To_Router_Ports:
			#	print self.All_End_To_End_Paths
			#	print eachPath
            if corepath[-1]==router:
		FlowList.append([eachPath[0], eachPath[1], self.Host_To_Router_Ports[eachPath[1], router]])

        return FlowList

    def dpid_to_mac(self, dpid):
        return EthAddr("%012x" % (dpid & 0xffFFffFFffFF,))

    def _handle_PacketIn(self, event):

        dpid = event.connection.dpid
        inport = event.port
        #print event.connection
        # Handling ARP Reply
        packet = event.parsed
        # print packet
        #print "\n", packet.type
        #print packet

        if packet.type == 2054:
            # ARP Reply
            pkt = packet.find("arp")

            if pkt.protosrc not in self.Host_To_Router and self.InitializationFinished == True and str(
                    pkt.protodst) != "8.8.8.8":
                self.Host_To_Router[str(pkt.protosrc)] = self.dpid_to_SwitchName[
                    str(self.dpid_to_mac(dpid))]  # IP to Switch Name , 144.0.1.2 --> R1
                self.Host_To_Router_Ports[str(pkt.protosrc), self.dpid_to_SwitchName[
                    str(self.dpid_to_mac(dpid))]] = inport  # (IP,SwitchName) --> port
                self.Host_To_Mac[str(pkt.protosrc)] = str(pkt.hwsrc)  # IP --> MAC
                self.HostCounter += 1
                if len(self.Host_To_Mac) == self.TotalNumOfHosts and self.HostCollectingFinished == False:
                    self.HostCollectingFinished = True

                    self.ReadPaths()
                    self.End_To_End_Paths_Extraction()
                    # Installing Flows On each dpid
                    for con in core.openflow.connections:
                        #print "INJA"
                        #print con
                        #print con.dpid
                        #print self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))]

                        FlowList = self.Flows_For_Each_Router(self.dpid_to_SwitchName[str(self.dpid_to_mac(con.dpid))])
                        #print "FlowList ", FlowList, "\n"

                        for flow in FlowList:
                            msg = of.ofp_flow_mod()
                            msg.priority = 100
                            msg.idle_timeout = 0
                            msg.hard_timeout = 0
                            msg.match.dl_type = 0x0800
                            msg.match.nw_src = IPAddr(flow[0])
                            msg.match.nw_dst = IPAddr(flow[1])
                            #print msg.match.nw_src
                            #print msg.match.nw_dst
                            msg.actions.append(of.ofp_action_output(port=flow[2]))
                            con.send(msg)
                            # print self.Host_To_Router

                            # We want to Reply the ARP Request, But All of the Hosts should be collected

            if self.HostCollectingFinished == True and self.InitializationFinished == True and str(
                    pkt.protodst) != "8.8.8.8":
                r = arp()
                r.hwtype = pkt.hwtype
                r.prototype = pkt.prototype
                r.hwlen = pkt.hwlen
                r.protolen = pkt.protolen
                r.opcode = arp.REPLY
                r.hwdst = pkt.hwsrc
                r.protodst = pkt.protosrc
                r.protosrc = pkt.protodst
                #print "Here"
                mac = EthAddr(self.Host_To_Mac[str(pkt.protodst)])
                r.hwsrc = mac
                e = ethernet(type=ethernet.ARP_TYPE, src=self.dpid_to_mac(dpid), dst=pkt.hwsrc)
                e.payload = r
                #print("%s answering ARP for \n")
                #print r.hwsrc
                #print r.protosrc,
                #print r.protodst
                #print r.hwdst
                #print inport
                # print r,'\n'
                msg = of.ofp_packet_out()
                msg.data = e.pack()
                msg.actions.append(of.ofp_action_output(port=of.OFPP_IN_PORT))
                msg.in_port = event.port
                # log.info("MSG %s\n",str(msg))
                event.connection.send(msg)


def launch():
    # MySim=MySimulation()
    # flow_tracker = FlowTracker()
    # core.register('openflow_flow_tracker', flow_tracker)
    core.registerNew(MySimulation)

# timer set to execute every five seconds

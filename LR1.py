#In this module we'll get the BW demand matrix and calculate the three sub_problems related to our decomosition

#We need
#1: network adjacency Matrix
#2: Bandwidth Demand Matrix (h(n,d))
#3: The quefficients (miu(d,l) , kisi(l))

from Graph import Graph
import networkx as nx
from networkx.algorithms.tree import branchings
import numpy as np
from numpy import linalg as LA
import time
import edmonds
import matplotlib.pyplot as plt
import Test_Abor_Main
from collections import defaultdict, namedtuple
import copy
import sys
class LR1:

	def __init__(self,hMatrix, Adj, Capacity, Subnet_To_Router_Mapping,Num_Of_Routers,Num_Of_Subnets):
		
		self.Capacity=Capacity
		self.Adj=Adj
		self.Adj_Dict={}
		for i in range(len(self.Adj)):
			self.Adj_Dict[i]={}
		for i in range(len(self.Adj)):
			for j in range(len(self.Adj[0])):
				if self.Adj[i][j]==1:
					self.Adj_Dict[i].update({j:0.0})
	
		self.hMatrix=hMatrix
		self.Subnet_To_Router_Mapping=Subnet_To_Router_Mapping
		self.ODPairs={}
		self.Links={}
		self.Subnets=[]
		self.TotalNumOfRouters=Num_Of_Routers
		self.TotalNumOfSubnets=Num_Of_Subnets
		TotalNumOfLinks=0
		for i in range(len(self.Adj)):
			for j in range(len(self.Adj[0])):
				if self.Adj[i][j]==1:
					TotalNumOfLinks+=1
		self.TotalNumOfLinks=TotalNumOfLinks
		self.TotalNumOfNodes=len(self.Adj[0])
		#print "TotalNodes"
		#print self.TotalNumOfNodes
		self.nu={}
		self.nu_history=[]
		self.mu={}
		
		self.M=1000
	def Extract_ODPairs(self):
		for i in range(len(self.hMatrix)):
			for j in range(len(self.hMatrix[0])):
				tmp=self.Subnet_To_Router_Mapping["Sub_"+str(j)]
				tmp2=tmp.split("_")
				Dest_Router=int(tmp2[1])
				if i!=Dest_Router:
					self.ODPairs[(i,j)]=self.hMatrix[i][j]
	
			
	def Extract_Subnets(self):
		for key in self.Subnet_To_Router_Mapping:
			self.Subnets.append(key)
	
	def Extract_Links(self):
		for i in range(len(self.Adj)):
			for j in range(len(self.Adj[0])):
				if self.Adj[i][j]!=0:
					self.Links[(i,j)]=self.Adj[i][j]
	def Sub1(self):
		Sum=0.0

		#for key,val in self.nu.items():
		for l in self.Links:
			Sum+=self.nu[l]*self.Capacity
		Sub1_Val=1.0-Sum
		#print "WHY",Sum
		#print "nu",self.nu
		if Sub1_Val>=0.0:
			return [0.0,0.0]
		else:
			return [Sub1_Val,1]

	def Sub2(self):
		
		#Here we should construct the network with the new link costs 
		#For each OD-pair the shortest-path with the new given cost for each link should be calculated
		# Constrcut Topology for that OD-Pair and Find the Path (OD-Pair means Node to Destination)
		Cost_List=[]
		#X is defined like X{ODPair}=(Path,Cost)
		X={}
		
		#For each OD-Pair we should construct the graph and do the shortest-path 
		for od in self.ODPairs:
			#Cost=0
			
			#Here setting the edges and their related costs has been finished so just we need to run the shortest path algorithm to find the minimum path towards the destination
			g = nx.DiGraph() 
			
			for l in self.Links:
				
				Sec_Part=0.0
				for i in range(self.TotalNumOfSubnets):
					if i==od[1]:
						Sec_Part+=self.mu[(i,l)]
				#print ">> ",self.nu[l], self.mu[(od[1],l)],
				LinkCost=self.nu[l]*self.hMatrix[od[0]][od[1]]+Sec_Part
				#print LinkCost
				g.add_edge(l[0], l[1], weight=LinkCost)
			#print "SP_TOPO"
			#print "OD ",od[0],od[1]
			#print g.edges(data=True)			
			#for (u, v, wt) in g.edges.data('weight'):
			#	print('(%d, %d, %.3f)' % (u, v, wt))
			#for l in self.Links:
			#	print G.add_edge(0,1,key='a',weight=7)
			Src_Router=od[0]
			tmp=self.Subnet_To_Router_Mapping["Sub_"+str(od[1])] 
			tmp2=tmp.split("_")
			Dest_Router=int(tmp2[1])

			(length,path)=nx.single_source_dijkstra(g, source=Src_Router, target=Dest_Router,weight='weight')
			#dist=nx.dijkstra_path_length(g, Src_Router, Dest_Router, 'distance')
			#l = nx.dijkstra_path(g, Src_Router, Dest_Router, 'distance')
			if  length==0:
				self.nu_history.append("NoPath")
			#if length==0:
			#	sys.exit()
			X[(od[0],od[1])]=[path,length]
			del g
			#Cost+=dist
			#Cost_List.append(Cost)
		return X 


	def Sub3(self):


		#Y is the Binary variable to tell that link l is on the aborescence tree or not
		#Converting Adj to dict
		
					
		#print self.Adj_Dict
		
		Abor_Links={}
		for i in range(self.TotalNumOfSubnets):
			
			Arc = namedtuple('Arc', ('tail', 'weight', 'head'))
			tmp=self.Subnet_To_Router_Mapping["Sub_"+str(i)]
			tmp2=tmp.split("_")
			Sink=int(tmp2[1])
			g=copy.deepcopy(self.Adj_Dict)
			for l in self.Links:
				#print i,"  ",l,self.mu[(i,l)],"  ",-1.0*self.M*self.mu[(i,l)]
				LinkCost=-1.0*self.M*self.mu[(i,l)]
				#g.add_edge(l[0], l[1], weight=LinkCost)
				g[l[0]][l[1]]=LinkCost
				Abor_Links[(i,l)]=[0.0,0]
			
			newG=[]
			for node1,adj in g.items():
				for node2,cost in adj.items():
					newG.append(Arc(node1,cost,node2))

			#if i==4 or i==5:
			#	print "Hereee"
			#	print g
			#	print newG
			#print "Sink ",Sink
			#print "Len ",len(newG)
			MSA=Test_Abor_Main.min_spanning_arborescence(newG,Sink)
			if len(MSA)==0:
				self.nu_history.append("Sefr")
			#print MSA
			#print "Len MSA ",len(MSA)
			for key,val in MSA.items():
				#print "DAHANESHoo",i,(val[2],val[0]),[val[1],1]
				Abor_Links[(i,(val[0],val[2]))]=[val[1],1]
			#print Abor_Links
			del Arc
			del g
			del newG

		#print Abor_Links
		
		return Abor_Links


	def SubGrad_Vector(self,alpha,X,Abor):
		Total_Sub_mu={}
		Total_Sub_nu={}

		
		#print "Check"
		#print X
		#First Calculating mu
		for i in range(self.TotalNumOfSubnets):
			for l in self.Links:
				Sum1=0.0
				for od in self.ODPairs:
					if i==od[1]:
						tmp=X[(od[0],od[1])]
						path=tmp[0]
						for index in range(len(path)-1):
							if path[index]==l[0] and path[index+1]==l[1]:
								Sum1+=1.0
				#print "KJKJLJL"
				#print Sum1,-self.M*(Abor[i,(l[0],l[1])][1])
				Total_Sub_mu[(i,l)]=Sum1-(self.M*(Abor[(i,l)][1]))
				
				#print "Injaaaa"
				#print Sum1, self.M,Y[i,l]
				
								 

		#Second Calulating Sub_nu
		#print self.Links
		for l in self.Links:
			Sum2=0.0
			for od in self.ODPairs:
				tmp=X[(od[0],od[1])]
				path=tmp[0]
				for index in range(len(path)-1):
					if path[index]==l[0] and path[index+1]==l[1]:
						Sum2+=self.hMatrix[od[0]][od[1]]		

			Total_Sub_nu[l]=Sum2-(alpha*self.Capacity)
			#print "alpha inside ",Total_Sub_nu[l],Sum2,alpha

		#print "Inside"
		#print alpha
		
		#Merging Total_Sub_mu and Totla_Sub_nu in SubGradient
		SubGradient=[]
		#print "Len"
		#print len(SubGradient)

		#print (Total_Sub_mu)
		#print len(Total_Sub_nu)
		
		
		SubGradient=[Total_Sub_mu,Total_Sub_nu] 
		return SubGradient
			
			
	def SubGrad_Norm(self,SubGradient):
		Merged=np.zeros(self.TotalNumOfSubnets*self.TotalNumOfLinks+self.TotalNumOfLinks,np.float)
		Index=0
		#print "SUBBBBBBBBBBBBBBBBBBBBBB"
		#print SubGradient
		for key1,val1 in SubGradient[0].items():
			Merged[Index]=val1
			Index+=1
		for key2,val2 in SubGradient[1].items():
			Merged[Index]=val2
			Index+=1
		#print Merged
		#print len(Merged)
		Sum=0.0
		for item in Merged:
			Sum+=item*item
		#print "Norm Inside"
		#Sum= np.linalg.norm(Merged)

		#print self.TotalNumOfSubnets
		#print self.TotalNumOfLinks
		#print len(Merged)
		#print Index
		return Sum
	

	

def Main_Loop(Adj,Subnet_To_Router_Mapping,Num_Of_Routers,Num_Of_Subnets,Capacity,hMatrix):
	start_time = time.time()

	#This function is just for testing the LR1 module -- Initializing the network and subnets


	TotalNumOfSteps=10000
	step=0	
	Theta=np.zeros(TotalNumOfSteps,np.float)
	Quiescence_Threshold=100
	quiescence_age=0
	#Lambda=np.ones(TotalNumOfSteps)
	Lambda=2.0

	
	#print hMatrix
	#1)Initializing mu and nu to zero (Like default), UB should be 1
	LB=0.0
	UB=1.0
	MyLR=LR1(hMatrix, Adj, Capacity, Subnet_To_Router_Mapping,Num_Of_Routers,Num_Of_Subnets)

	

	print "SetLinks"
	MyLR.Extract_Links()
	print MyLR.Links

	print "ODPairs"
	#print MyLR.ODPairs
	MyLR.Extract_ODPairs()
	print MyLR.ODPairs
	print len(MyLR.ODPairs)
	print "Subnets"
	print MyLR.Subnets
	MyLR.Extract_Subnets()
	print MyLR.Subnets

	for i in MyLR.Links:
		MyLR.nu[i]=0.0

	for i in range(MyLR.TotalNumOfSubnets):
		for l in MyLR.Links:
			MyLR.mu[(i,l)]=0.0
	My_Costs={}
	My_SPs={}
	My_Abors={}
	My_Alphas={}
	for i in range(TotalNumOfSteps):
		My_Costs[i]=0.0
		My_SPs[i]=0.0
		My_Abors[i]=0.0
		My_Alphas[i]=0.0

	Min_Vals=[]
	Test=[]
	
	#2)Extracting alpha, X and Y by solving the subproblems
	while(step<TotalNumOfSteps):
		
		
		Sub1=MyLR.Sub1()
		Sub1_Val=Sub1[0]
		Alpha=Sub1[1]
		print "Check "
		#print MyLR.nu		
		print Alpha
	

		#print "Sub2"
		#print "X"
		X=MyLR.Sub2()
		#print X
		#print len(X)
		#Sub2_Value
		Sub2_Total_Cost=0.0
		for key,val in X.items():
			#print val[1]
			Sub2_Total_Cost+=val[1]
		#print val[1]
		#print "Sub2_Value"
		#print Sub2_Total_Cost
		
		#print "Sub3"
		Abor_Links=MyLR.Sub3()
		
		
		#print len(Abor_Links)
		#Sub3_Value
		Sub3_Value=np.zeros(MyLR.TotalNumOfSubnets,np.float)
		#for i in range(MyLR.TotalNumOfSubnets):
		#	cost=0.0
		Total_Abor_Cost=0.0
		for key,val in Abor_Links.items():
			if key[0]==4 or key[0]==5:
				print key,val
			Total_Abor_Cost+=val[0]
		
		#print Sub3_Value
		
		
		#print "Total Abor Costs"

		#for i in Sub3_Value:
		#	Total_Abor_Cost+=i

		#print Total_Abor_Cost
		#3)Calculating the Subgradient_Mu and Subgradient_Nu
		
		Subgradient=MyLR.SubGrad_Vector(Alpha,X,Abor_Links)
		#print "SubGradient "
		#print Subgradient
		
		#4)Calculating the Norm of the Total Subgradient Vector, The size of this vector is one column and |N|*|L|+|L| rows
		Subgradient_Norm=MyLR.SubGrad_Norm(Subgradient)
		print "Here ",step
		print "Sub1_Alpha ",Sub1_Val
		print "Sub2_ShortestPath ",Sub2_Total_Cost
		print "Sub3_Total Abor ",Total_Abor_Cost
		#print Alpha+Sub2_Total_Cost+Total_Abor_Cost
		print "Sub_Norm",Subgradient_Norm
		My_Alphas[step]=Sub1_Val
		My_SPs[step]=Sub2_Total_Cost
		My_Abors[step]=Total_Abor_Cost
		#5)In each round by calculating the Norm vector we can calculate the Theta(k)
		print "Z_Dual"
		Z_Dual= Sub1_Val+Sub2_Total_Cost+Total_Abor_Cost
		print Z_Dual
		print "LB"
		print LB
		
		
		 
		if Z_Dual>LB:
			LB=Z_Dual
			quiescence_age=0
		else:
			quiescence_age=quiescence_age+1

		if quiescence_age>=Quiescence_Threshold:
			Lambda=Lambda/2.0
			quiescence_age=0

		Theta[step]=(Lambda*(UB-Z_Dual))/(Subgradient_Norm)
		#print Subgradient
		print "Theta",Theta[step]

		#6)Calculating the main function
		#Tot_Cost=MyLR.Main_Func_Value(Alpha,X,Abor_Links)
		#print "Total_Cost",Tot_Cost
		My_Costs[step]=Z_Dual
		
		print X[(0,4)]
		print X[(1,4)]
		#print X[(0,9)]
		#print X
		
		#7)Finally we can Calculate mu(k+1) and nu(k+1) and going to step 2
		#First Merging mu and nu
		#print "INJAAAAAAAA"
		for key1,val1 in Subgradient[0].items():
			#print MyLR.mu[key1],Theta[step],val1
			#print key1,Theta[step],val1
			tmp1=MyLR.mu[key1]+(Theta[step]*val1)

			#print tmp,MyLR.mu[key],Theta[step],Subgradient[0][key]
			if tmp1<0:
				MyLR.mu[key1]=0
			else:
				MyLR.mu[key1]=tmp1
			#print MyLR.mu[key1]
			#print MyLR.mu[key]
		#print "QQQQQQQQQ"
		#print Subgradient[0]
		#print Subgradient[1]
		for key2,val2 in Subgradient[1].items():
			#print key2,val2
			#print MyLR.nu[key2],Theta[step],val2
			tmp2=MyLR.nu[key2]+(Theta[step]*val2)

			if tmp2<0:
				MyLR.nu[key2]=0
			else:
				MyLR.nu[key2]=tmp2
			#print MyLR.nu[key2]
			#print MyLR.nu[key]
		#print MyLR.mu
		#print MyLR.nu
			#print 

		#if Z_Dual>0.3:
		#	sys.exit()
		#print "Historys"
		#print X
		#print MyLR.nu_history
		#time.sleep(0.1)
		step+=1
		
	print len(MyLR.nu_history)
	#print My_Costs
	#print "Here"
	print MyLR.mu
	print MyLR.nu
	#print Theta
	print("--- %s seconds ---" % (time.time() - start_time))
	print "Min_Vals"
	#print Min_Vals
	print Lambda
	print quiescence_age
	print LB
	print MyLR.ODPairs
	print hMatrix
	#print Test
	#print len(MyLR.Links)
	plt.figure("Z_Dual")
	plt.plot(My_Costs.values()) # Plot list. x-values assumed to be [0, 1, 2, 3]
	plt.figure("Theta")
	plt.plot(Theta)
	plt.figure("Alpha")
	plt.plot(My_Alphas.values())
	plt.figure("Shortest Path")
	plt.plot(My_SPs.values())
	plt.figure("Abor")
	plt.plot(My_Abors.values())
	plt.show()
	
	

		
Adj = np.array([[0,1,0,0,1],[1,0,1,1,1],[0,1,0,1,0],[0,1,1,0,1],[1,1,0,1,0]])
Subnet_To_Router_Mapping={}

Subnet_To_Router_Mapping["Sub_0"]="R_0"
Subnet_To_Router_Mapping["Sub_1"]="R_0"
Subnet_To_Router_Mapping["Sub_2"]="R_1"
Subnet_To_Router_Mapping["Sub_3"]="R_1"
Subnet_To_Router_Mapping["Sub_4"]="R_2"
Subnet_To_Router_Mapping["Sub_5"]="R_2"
Subnet_To_Router_Mapping["Sub_6"]="R_3"
Subnet_To_Router_Mapping["Sub_7"]="R_3"
Subnet_To_Router_Mapping["Sub_8"]="R_4"
Subnet_To_Router_Mapping["Sub_9"]="R_4"
Num_Of_Subnets=10
Num_Of_Routers=5
Capacity=1000.0
#Router to Subnet BW demand 
hMatrix = np.array([[0.0 for y in range(Num_Of_Subnets)] for x in range(Num_Of_Routers)],np.float)
hMatrix[0][4]=600.0
hMatrix[1][5]=800.0
 	
Main_Loop(Adj,Subnet_To_Router_Mapping,Num_Of_Routers,Num_Of_Subnets,Capacity,hMatrix)

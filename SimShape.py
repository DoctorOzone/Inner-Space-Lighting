import os
import numpy as np


#No DAT protection

light_config_file = 'pegboard.txt'
output_filename = 'pegboard_sim.txt'
WM_ll = 1.9
WM_ul = 2.3



######

TotalS = 10000
Csamp_max = 50


ShapeC = []
Node=[]
sNode = []

outpath = os.getcwd()
        
readFile = open('%s/%s'%(outpath,light_config_file),'r')
sepfile = readFile.read().split('\n')
for a in range (0,len(sepfile)):
    xandy = sepfile[a].split(',')
    ShapeC.append([float(xandy[0]),float(xandy[1]),float(xandy[2])])
    Node.append(int(xandy[3]))
    if int(xandy[3])==1:
        sNode.append([float(xandy[0]),float(xandy[1]),float(xandy[2])])

Dist=[]
WM = np.zeros((len(sNode),len(sNode)))
ShapeCt = 0
Kct = 0
for a in range (0,len(ShapeC)):
    xm = []
    for b in range (0,len(sNode)):
        dd = (((ShapeC[a][0]-sNode[b][0])**2)+((ShapeC[a][1]-sNode[b][1])**2)+((ShapeC[a][2]-sNode[b][2])**2))**0.5
        if dd>0:
            xm.append(1/(dd**3))
        else:
            xm.append(999)
    if np.amax(xm)==999:#checks if we're on a sNode
        
        for b in range (0,len(sNode)):
            dd = (((ShapeC[a][0]-sNode[b][0])**2)+((ShapeC[a][1]-sNode[b][1])**2)+((ShapeC[a][2]-sNode[b][2])**2))**0.5
            if WM_ll<=dd<=WM_ul:
                WM[ShapeCt,b] = 1
                Kct += 1
        ShapeCt += 1
                
    Dist.append(xm)



def Bulk():
    x = np.random.randint(0,256,250)
    return x
        


def GetI(uu,vv):
    Ksum=0.0; Kct=0; NCct=0
    for a in range (0,len(uu)):
        for b in range (0,len(uu)):
            if (WM[a,b]==1):#detects neighboring cell, allowing for diagonal directions
                Ksum+= (((uu[a])*(uu[b]))+((vv[a])*(vv[b])))
                Kct+=1
            NCct+=1
            
    SSQ_K = len(uu)
    MORAN = ((len(uu)*Ksum)/(float(Kct)*float(SSQ_K)))
    return MORAN


maxon = 255
def GetColors(sims):
    
    MaxI = -9999
    
    for mm in range (0,sims):
    
        colors = Bulk()
        offset = 0
        
        xNodeConfig=[]
        xreds=[]
        xgreens=[]
        xblues=[]
        U=[]
        V=[]
        for lights in range (0,len(sNode)):
            slider = (colors[-1+offset])
            uidx = -2+offset
            sector = -9999
            while sector < -1:
                if colors[uidx] < 252:
                    sector = colors[uidx]%6
                uidx -= 1
                
            offset = uidx
            
                
            if sector == 0:
                R,G,B = maxon,slider,0
            if sector == 1:
                R,G,B = slider,maxon,0
            if sector == 2:
                R,G,B = 0,maxon,slider
            if sector == 3:
                R,G,B = 0,slider,maxon
            if sector == 4:
                R,G,B = slider,0,maxon
            if sector == 5:
                R,G,B = maxon,0,slider
            

            xreds.append(R)
            xgreens.append(G)
            xblues.append(B)
            
            xNodeConfig.append([R,G,B])
            
            theta = (np.pi*(1/3)*sector)+((slider/256)*np.pi*(1/3))
            U.append(np.cos(theta))
            V.append(np.sin(theta))
            
        I = GetI(U,V)
        #print(I,MaxI)
        if I > MaxI:
            reds = xreds
            greens = xgreens
            blues = xblues
            NodeConfig = xNodeConfig
            MaxI = I
        
    Config = []
    NodeCt=0
    for lights in range (0,len(ShapeC)):
        if Node[lights]==1:
            Config.append(NodeConfig[NodeCt])
            NodeCt += 1
        else:
            R = np.average(reds,weights=Dist[lights])
            G = np.average(greens,weights=Dist[lights])
            B = np.average(blues,weights=Dist[lights])
            Config.append([R,G,B])
            
    
            
    return Config,MaxI
        
outfile = open('%s/%s'%(outpath,output_filename),'w')

print('for n-th batch, time to complete ~ n^2')
for mm in range (1,Csamp_max+1):
    for a in range (0,TotalS):
        UColors,MI = GetColors(mm)
        outfile.write('%f,%d\n'%(MI,mm))
    print('Batch %d of %d'%(mm,Csamp_max))

    
outfile.close()
    



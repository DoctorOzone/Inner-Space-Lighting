import board
import neopixel
import busio
import os
import sys
import serial
import numpy as np
from serial.tools import list_ports
import time
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import scipy.stats

detectlights = 150
StartLight = 6
light_config_file = 'Basket.txt'
simulation_file = 'Simulations_BasketGradient.txt'
WM_ll = 1.9
WM_ul = 3.1
Csamp_scale = 10

Msorted = []
readFile = open('/home/pi/%s'%simulation_file,'r')
sepfile = readFile.read().split('\n')
for a in range (0,len(sepfile)-1,10000):
    XXsim=[]
    for b in range (0,10000):
        xandy = sepfile[a+b].split(',')
        XXsim.append(float(xandy[0]))
    Xsorted = sorted(XXsim)
    Msorted.append(Xsorted)

ShapeC = []
Node=[]
sNode = []
        
readFile = open('/home/pi/%s'%light_config_file,'r')
sepfile = readFile.read().split('\n')
for a in range (0,len(sepfile)-1):
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


pixels = neopixel.NeoPixel(board.D18, detectlights, brightness=1)
pixels.fill((0,0,0))

ports=dict()  
ports_avaiable = list(list_ports.comports())
rng_com_port = None
for temp in ports_avaiable:
    if temp[1].startswith("TrueRNG"):
        print('Found:           ' + str(temp))
        if rng_com_port == None:        # always chooses the 1st TrueRNG found
            rng_com_port=str(temp[0])
print('Using com port:  ' + str(rng_com_port))
print('==================================================')
sys.stdout.flush()
try:
    ser = serial.Serial(port=rng_com_port,timeout=10)  # timeout set at 10 seconds in case the read fails
except:
    print('Port Not Usable!')
    print('Do you have permissions set to read ' + rng_com_port + ' ?')
if(ser.isOpen() == False):
    ser.open()
ser.setDTR(True)
ser.flushInput()
sys.stdout.flush()


starttime = int(time.time()*1000)

outfile = open('/home/pi/dataout/WSlights6dev_%d.txt'%(starttime),'w')
modfile = open('/home/pi/dataout/WSlights6dev_%d_summary.txt'%(starttime),'w')


def M2P(MIv,Nsim):
    idx = 0
    Mxy = Msorted[Nsim-1]
    for a in range (0,len(Mxy)):
        if Mxy[a]>MIv:
            idx += 1
    if idx==0:
        idx += 1
    p_i = idx/10000
    #print(idx,MIv,np.amin(Msorted),np.amax(Msorted))
    return p_i


def Bulk():
    ser.flushInput()
    x = ser.read(250)
    for a in range (0,len(x)):
        outfile.write('%d,'%x[a])
    outfile.write('%d\n'%(int(time.time()*1000)))
    outfile.flush()
    os.fsync(outfile.fileno())
    return x
        
def Flash(bulb,red,green,blue):
    #print(bulb,red,green,blue)
    dimF = 0.4
    red = int(red*dimF)
    green = int(green*dimF)
    blue = int(blue*dimF)
    pixels[bulb] = [red,green,blue]
    #if bulb==6:
    #    print(red,green,blue)
    


def Kill():
    pixels.fill((0,0,0))

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
    #print(sims)
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
        
def MiniA0(current,target):
    bitct = 0
    for a in range (0,60):
        X = Bulk()
        for b in range (0,len(X)):
            strnode = str(bin(256+int(X[b])))[3:]
            bitct += (int(strnode[0])+int(strnode[1])+int(strnode[2])+int(strnode[3])+int(strnode[4])+int(strnode[5])+int(strnode[6])+int(strnode[7]))
        
        
        if a%6==0:
            
            for c in range (0,len(ShapeC)):
                
                
                
                Rnow = UColors[c][0]
                Rprv = PrvColors[c][0]
                Rdo = ((Rnow-Rprv)*(a/60))+Rprv

                Gnow = UColors[c][1]
                Gprv = PrvColors[c][1]
                Gdo = ((Gnow-Gprv)*(a/60))+Gprv

                Bnow = UColors[c][2]
                Bprv = PrvColors[c][2]
                Bdo = ((Bnow-Bprv)*(a/60))+Bprv
                
                FlVal = c+StartLight
        
                Flash(FlVal,Rdo,Gdo,Bdo)
                
                #if c==16:
                #    print(Rdo,Gdo,Bdo)

        
        
        
        time.sleep(1)
        
        
        
    EX = bitct - (250*8*60*0.5)
    SNPQ = (250*8*60*0.25)**0.5
    Zfinal = EX/SNPQ
    return(Zfinal)

PrvColors = GetColors(1)[0]#having trouble doing more than a few sims here...ugh. limitations of rpi draw from RNG?. p-values seem high given drawing 50 numbers though.

#show where nodes are to calibrate
Kill()
for a in range (0,len(ShapeC)):
    FlVal = a+StartLight
        
    if Node[a]==1:
        Flash(FlVal,150,150,150)
time.sleep(10)
Kill()

Z_A0 = 0


#shutdown init#

GPIO.setmode(GPIO.BCM)

GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

 

# Our function on what to do when the button is pressed
ShutdownNext = [0]
def Shutdown(channel):
    ShutdownNext[0] = 1
    print('shutdown sequence start')

def CleanShutdown():
    outfile.close()
    modfile.close()
    
    #outfileStr = '/home/pi/WSlights_%d.txt'%(starttime)
    #os.system('node /home/pi/web3/put-files.js --token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweGI3ZjcwNkYyMmYwNzY4ODU4ZGYyNThCZjM1MEEyQzNjRUE1NDkzNWQiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2MzcwMjc5NTkyODEsIm5hbWUiOiJSTkd1cGxvYWQifQ.QnYU5pbzt5oBcWjvDzL_1B4v0PFP6s3uq6zwEhp8xTM /home/pi/WSlights_%d.txt'%(starttime))

    #shellfile = open('/home/pi/upload.sh','w')
    #shellfile.write('node /home/pi/web3/put-files.js --token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweGI3ZjcwNkYyMmYwNzY4ODU4ZGYyNThCZjM1MEEyQzNjRUE1NDkzNWQiLCJpc3MiOiJ3ZWIzLXN0b3JhZ2UiLCJpYXQiOjE2MzcwMjc5NTkyODEsIm5hbWUiOiJSTkd1cGxvYWQifQ.QnYU5pbzt5oBcWjvDzL_1B4v0PFP6s3uq6zwEhp8xTM /home/pi/WSlights_%d.txt'%(starttime))
    #shellfile.close()

    Kill()

    print("Shutting Down")
    os.system("sudo shutdown -h now")

 

# Add our function to execute when the button pressed event happens

GPIO.add_event_detect(21, GPIO.FALLING, callback=Shutdown, bouncetime=2000)

#####


Run = [1]


plt.style.use('dark_background')
fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
#ax3 = fig.add_subplot(313)


figManager = plt.get_current_fig_manager()
figManager.full_screen_toggle()

def stop(self):
    ShutdownNext[0] = 1
    print('shutdown sequence start')

    
axkil = plt.axes([0.15, 0.05, 0.07, 0.05])
bkil = Button(axkil, 'stop', color = '0.5', hovercolor='0.8')
bkil.on_clicked(stop)

#axes = plt.axes([0.81, 0.000001, 0.1, 0.075])
#bnext = Button(axes, 'Add',color="yellow")
#bnext.on_clicked(add)

ult_t=[]
ult_Y1a=[]
ult_Y1b=[]
ult_Y2a=[]
ult_Y2b=[]

KMln = 0
KZln = 0

MI_pval_save=[]
Z_pval_save=[]

while Run[0]==1:
    Csamp = int((np.abs(Z_A0)*Csamp_scale)/np.e)
    if Csamp > 50:
        Csamp = 50
    if Csamp < 1:
        Csamp = 1
    outfile.write('Getting %d Samples\n'%Csamp)
    outfile.flush()
    os.fsync(outfile.fileno())
    UColors,MI = GetColors(Csamp)
    MI_pval = M2P(MI,Csamp)
    MI_pval_save.append(MI_pval)
    
    pi_onetail = scipy.stats.norm.sf(Z_A0)
    
    if pi_onetail<=0.5:
        pi_twotail = 2*pi_onetail
    else:
        pi_twotail = 2*(1-pi_onetail)
        
    Z_pval_save.append(pi_twotail)
    
    KMln += np.log(MI_pval)
    KZln += np.log(pi_twotail)
    
    CumMP = scipy.stats.chi2.sf(-2*KMln,2*len(MI_pval_save))
    CumZP = scipy.stats.chi2.sf(-2*KZln,2*len(MI_pval_save))
    
    ult_Y1a.append(1/MI_pval)
    ult_Y1b.append(1/pi_twotail)
    ult_Y2a.append(CumMP)
    ult_Y2b.append(CumZP)
    ult_t.append(len(ult_Y1a))
    
    print(MI,MI_pval)
    modfile.write('%d,%f,%f,%f\n'%(int(time.time()*1000),MI,MI_pval,Z_A0))
    modfile.flush()
    os.fsync(modfile.fileno())
    
    
    outfile.write('Coherence sampling\n')
    outfile.flush()
    os.fsync(outfile.fileno())
    Z_A0 = MiniA0(PrvColors,UColors)
    PrvColors = UColors
    

    
    ax1.clear()
    ax1.plot(ult_t,ult_Y1a,color='magenta', label='M')
    ax1.plot(ult_t,ult_Y1b,color='aqua', label='Z')
    ax1.set_yscale('log')
    ax1.legend(loc=2)

    
    ax2.clear()
    ax2.plot(ult_t,ult_Y2a,color='magenta', label='M')
    ax2.plot(ult_t,ult_Y2b,color='aqua', label='Z')
    ax2.set_ylim([0,1])
    ax2.legend(loc=2)
    
    plt.pause(0.05)
    
    if ShutdownNext[0]==1:
        CleanShutdown()
    

plt.show()


#z and colors maintain independence ... show both. lk previous screen strawberry
#skip first one because Z_A0 not populated yet.
#z_a0-p and mi-p instint and cumulative ... see strawberry prv but also wonder if can make princeton-like chart for these 2 params.


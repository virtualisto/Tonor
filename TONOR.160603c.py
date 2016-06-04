file='TONOR.160603b.py'
#-----------------------------------------------------------
#----IMPORT-------------------------------------------------
#-----------------------------------------------------------
import pdb
import random
import time
import threading
import logging
import pickle
import os
import glob
import sys

#-----------------------------------------------------------
#----ARDUINO------------------------------------------------
#-----------------------------------------------------------
DING = 8
APIN = [8,10,12,16,18,22,24]
port=[APIN[i] for i in range(1,len(APIN))]
# Since PIN[0] is for the interrupt,
# and six bits gives a choice of 1 out of 64 tons.
#####################################################
#     Uno           WAV Trigger
#     ===           ===========
#     GND  <------> GND
#     Pin9 <------> RX
#####################################################
#       RPi     shifter1    shifter2    Uno
#       ===     ========    ========    ===
#       6 GND   LV GND
#               HV GND                  GND on POWER
#       8       LV1      
#       10      LV2      
#       12      LV3      
#       16      LV4      
#               HV1                     D2 = INTO
#               HV2                     D3 = B0
#               HV3                     D4 = B1
#               HV4                     D5 = B2
#       1 3V3   LV
#               HV                      5V  on POWER
#####################################################
#       6 GND               LV GND
#                           HV GND      GND on POWER
#       18                  LV1
#       22                  LV2
#       24                  LV3
#                           (LV4)
#                           HV1         D6 = B3
#                           HV2         D7 = B4
#                           HV3         D8 = B5
#                           (HV4)        
#       1 3V3               LV
#                           HV          5V  on POWER
#####################################################
PTON=[
'TAMB', 'SHEK', 'BEL2', 'BLIK', 'BIPP', 'TONE', 'BONG', 'WHOM', 'G#1', 'A1','A#1', 'B1', 
'C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2','G#2', 'A2', 'A#2', 'B2', 
'C3', 'C#3', 'D3','D#3', 'E3', 'F3','F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3', 
'C4', 'C#4', 'D4', 'D#4','E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4', 
'C5', 'C#5', 'D5','D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5', 
'C6','C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6'
] 
#-----------------------------------------------------------
#----GLOBAL-------------------------------------------------
#-----------------------------------------------------------
arguments=sys.argv[1:]
gpioflag    = 0
kybdflag    = 0
WORKDIR     = os.path.dirname(os.path.abspath(__file__))
loggflag    = 1        # Default 1 records to .log file in source file directory.
runflag     = 0        # 1 to repeat CURRENT pattern
quitflag    = 1        # 0 to leave for PYTHON?
tonsflag    = 1        # 1 to show ton name per beat
RUNLENGTH   = 16
RUNTONES    = []
RUNDECAYS   = []
NEWNAME     = ''
SAVEDPARTS  = dict()
SECPERMIN   = 60
mSPERSEC    = 1000
SLOWTEMPO   =   1.0   # minimum PlsPerMin
FASTTEMPO   = 1200.0   # maximum PlsPerMin
CURRENT     = dict()
MUTANT      = dict()
PARTSLIST   = []
PARTSNAMES  = []
DOTS        = []
PARTICLE    = ''
#-----------------------------------------------------------
#----GPIO AND KEYBOARD SETUP--------------------------------
#-----------------------------------------------------------
print('Current file      = '+file)
print('Working directory = '+WORKDIR)
print(arguments)
if len(arguments)==2:
    print('There are two parameters.')
    if arguments[0]=='gpio' or int(arguments[0])==1:
        gpioflag=1
        print('GPIO is enabled.')
    else:
        gpioflag=0
        print('GPIO is disabled.')
    if arguments[1]=='kybd' or int(arguments[1])==1:
        kybdflag=1
        print('KEYBOARD is enabled.')
    else:
        kybdflag=0
        print('KEYBOARD is disabled.')
else:
    print('Expected two parameters at terminal commandline.')
    print('The assumption now is that you are in the IDLE shell.')
    print('Therefore, kybdflag is cleared to 0.')
    kybdflag=0
    x=int(input('Enter 1 for gpioflag: '))
    if x==1:
        gpioflag=1
    else:
        gpioflag=0
    print('gpioflag={0} kybdflag={1}'.format(gpioflag,kybdflag))
#...........................................................
#....GPIO SETUP FOR RIGHTSYSTEM--->ARDUINO..................
#...........................................................
print('====Check for GPIO:===========================================')
def LEFTtrigger(x):
    print("received signal from LEFTSYSTEM")
    setPort(PTON.index('F4'))
    trigger(DING)
    
if gpioflag:
        import RPi.GPIO as GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(40,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        for i in APIN:
            GPIO.setup(i,GPIO.OUT)
            GPIO.output(i,1)
        GPIO.add_event_detect(40,GPIO.FALLING,callback=LEFTtrigger,bouncetime=10)
        print('====GPIO   setup done.========================================')
else:
        print('====No GPIO right now.========================================')

#https://bytes.com/topic/python/answers/648488-how-convert-number-binary
dec2bin = lambda x: (dec2bin(x//2) + str(x%2)) if x else ''

def setPort(d):
    b=[]
    b=list(map(eval,list(dec2bin(d))))
    b.reverse()
    #print(b)
    #print(port)
    #pdb.set_trace()
    for k in range(0,len(port)):
            GPIO.output(port[k],0)
    for j in range(0,len(b)):
        #print('j='+str(j)+' b[j]='+str(b[j])+' port[j]='+str(port[j]))
        GPIO.output(port[j],b[j])
    return

def trigger(pin):
    GPIO.output(pin,0)
    time.sleep(.001)
    GPIO.output(pin,1)
    return

def toIno(a,b,d):   # d is in Seconds, e.g., 0.25 S
    for h in range(a,b+1):
        print(h)
        setPort(h+1)
        trigger(DING)
        time.sleep(d)
#...........................................................
#....SETUP FOR LINUX TERMINAL KEYBOARD......................
#...........................................................
# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select
#-----------------------------------------------------------
#----UTILITY------------------------------------------------
#----printing-----------------------------------------------
def dictate(D):
    if type(D)==dict:
        if D == {}:
            print('D={}')
        else:
            for i in D: print('{0}->{1}'.format(i,D[i]))
    else:
        print('Parameter is not a dictionary.')

def printl(list):
    for x in list: print(x)
        
def dotlbl(x,w):
    return '{d: >{width}}'.format(d=str(x), width=w)

#-----------------------------------------------------------
#----CLASS--------------------------------------------------
#-----------------------------------------------------------
class Graph:
    def __init__(self,s):   # s is a string name for the graph
        self.n=s
        self.sons={}        # {x:[<son dots of x>]}
        self.dads={}        # {x:[<dad dots of x>]}

    def dots(self):
        return list(self.sons.keys())
    
    def arrows(self):
        m='{'
        for k in list(self.sons.keys()):
            for j in self.sons[k]:
                m=m+str(k)+'->'+str(j)+','
        return m[0:len(m)-1]+'}'

    def addDot(self,name):
        self.sons[name]=[]
        self.dads[name]=[]

    def addArrow(self,tail,head):
        if not tail in self.sons.keys():
            self.addDot(tail)
        if not head in self.sons.keys():
            self.addDot(head)
        if not head in self.sons[tail]:
            self.sons[tail].append(head)
        if not tail in self.dads[head]:
            self.dads[head].append(tail)

    def matrix(self):
        D=self.dots()
        L=len(D)
        V=range(0,L)
        R=[[0 for _ in D] for _ in D]
        for x in V:
            for y in V:
                R[x][y]=1 if D[y] in self.sons[D[x]] else 0
        Z=[]
        for y in V:
            Z.append(dotlbl(D[y],6)+'|'+''.join(list(map(lambda e:dotlbl(e,4),R[y])))   )
        Z.append('      |'+''.join(['-' for _ in range(0,4*L)]))
        Z.append('  --->|'+''.join(list(map(lambda e:dotlbl(e,4),D))))
        printl(Z)
        return
#...........................................................
class Part(Graph):
    def __init__(self,s):
        super().__init__(s)
        self.tons={}        # {p:[<particle p tons upon timeout>]}
        self.time={}        # {p:<decay time of p>}
        self.prob={}        # {(p,q):<probint from p to q>}
        self.subp={}        # {p:[sub-part names of p]}
        self.SUBPARTS=[]    # [<list of sub-part names>]
        '''
        self.PlsPerPtn = 0       # hierarchy
        self.TonPerPls = 0       # hierarchy
        self.TonPerPtn = 0       # hierarchy
        self.NncPerTon = 0       # hierarchy
        self.AtmPerPtn = 0       # hierarchy
        '''
        self.PlsPerMin = 0       # timing
        #self.SecPerPls = 0       # timing
        #self.mSPerPls  = 0       # timing
        #self.mSPerTon  = 0       # timing
        #self.mSPerPtn  = 0       # timing
        self.TimeAtom  = 0       # timing
#...........................................................        
#....timing.................................................
#...........................................................        
    def setPlsPerMin(self,ppm): # ASSUME ppm is a positive integer
        self.PlsPerMin=max(SLOWTEMPO,min(FASTTEMPO,ppm))
        #self.SecPerPls=SECPERMIN/self.PlsPerMin
        self.TimeAtom = mSPERSEC*SECPERMIN/self.PlsPerMin

    def showTiming(self):
        for x in self.dots():
            print('Timeout {0} = {1} mS'.format(x,self.time[x]*self.TimeAtom))
        print('PlsPerMin = {0}'.format(self.PlsPerMin))
        print(' TimeAtom = {0}'.format(self.TimeAtom ))     
        
    def setTimeout(self,x,m):   # m is a multiplier of TimeAtom [mS]
        self.time[x]=m
        
#...........................................................            
#....hierarchy..............................................
#...........................................................
    '''
    def setPlsPerPtn(self,ppp):
        self.PlsPerPtn=ppp

    def setTonPerPls(self,tpp):
        self.TonPerPls=tpp
        self.TonPerPtn=self.TonPerPls*self.PlsPerPtn

    def setNncPerTon(self,npt):
        self.NncPerTon=npt

    def defaultHierarchy(self):
        self.setPlsPerPtn(16)
        self.setTonPerPls(4)
        self.setNncPerTon(4)
        self.AtmPerPtn   =self.NncPerTon*self.TonPerPls*self.PlsPerPtn

    def showHierarchy(self):
        print('PlsPerPtn={0} TonPerPls={1} NncPerTon={2} AtmPerPtn={3}'
              .format(self.PlsPerPtn,self.TonPerPls,self.NncPerTon,self.AtmPerPtn))
    '''
#...........................................................
#....connectivity...........................................
#...........................................................
    def addDot(self,x): 
        super().addDot(x)
        self.tons[x]=[]
        self.time[x]=1  # time[x] is a multiple of TimeAtom [mS]
        self.subp[x]=[]
        
    def addArrow(self,x,y,p):
        if x in self.dots() and y in self.dots() and type(p)==int and p>0:
            super().addArrow(x,y)
            self.prob[(x,y)]=p
        else:
            print('{0} or {1} is not a dot, or {2} is not a probint.'.format(x,y,p))
        
    def matrix(self):
        D=self.dots()
        L=len(D)
        V=range(0,L)
        R=[[0 for _ in D] for _ in D]
        for i in V:
            for j in V:
                R[i][j]=self.prob[(D[i],D[j])] if (D[i],D[j]) in self.prob.keys() else 0
        Z=[]
        for y in V:
            Z.append(dotlbl(D[y],6)+'|'+''.join(list(map(lambda e:dotlbl(e,4),R[y])))   )
        Z.append('      |'+''.join(['-' for _ in range(0,4*L)]))
        Z.append('  --->|'+''.join(list(map(lambda e:dotlbl(e,4),D))))
        printl(Z)
        return

    def showSubParts(self):
        for S in self.SUBPARTS:
            print('PART {0} has {1}'.format(S,[x for x in self.dots() if S in self.subp[x]]))
            
#...........................................................
#....tonality...............................................
#...........................................................
    def addTon(self,x,ton,sbpn):
        if x in self.dots() and ton in PTON:
            self.tons[x].append(PTON.index(ton))
            self.subp[x].append(sbpn)
            if not sbpn in self.SUBPARTS:
                self.SUBPARTS.append(sbpn)
        else:
            print('{0} is not a dot, or {1} is not a ton.'.format(x,ton))

#...........................................................
#....operating..............................................
#...........................................................
    def Next(self,x):
        D=self.prob
        L=[(D[z],z[1]) for z in D if z[0]==x]
        if D and L:
            M=range(len(L))
            s=float(sum([L[i][0] for i in M]));
            K=[L[i][0]/s for i in M]
            r=random.random()
            i=0
            s=0
            b=0
            while(b==0):
                s+=K[i]
                if(r>s):
                    i+=1
                else:
                    b=1
        else:
            return x
        return L[i][1]

    def Timeout(self,x):    # time[x] is a multiple of TimeAtom (which is in mS)
        mS=self.time[x]*self.TimeAtom
        S=mS/1000
        time.sleep(S)
        return mS
        

    def showPart(self):
        print('----Part = {0}-----------------------------------------------'.format(self.n))
        self.matrix()
        #self.showHierarchy()
        self.showTiming()
        self.showSubParts()

    def PlayTon(self,x,L):
        #pdb.set_trace()
        if self.tons[x] and set(self.subp[x]) & set(L):
            t=self.Timeout(x)
            print('t={0}'.format(t))

# For each sub-part in L, play only the ton of x for that sub-part. addTon pairs
# added ton with its sbpn. So, given sbpn in L, it has an index in self.sbpn, or
# not. If it has an index in self.sbpn, that is paired with a ton via the index
# in self.tons. That is the ton of the sbpn to play.

            for s in L:
                for i in range(0,len(self.subp[x])):
                    if self.subp[x][i]==s and gpioflag:
                        ton=self.tons[x][i]
                        setPort(ton+1)  # Because WAV Trigger starts at 1 for TAMB
                        trigger(DING)
                        print('{0} {1} {2}'.format(x,PTON[ton],self.subp[x]))
        
    def RunPart(self,x,n,L):    # x=start dot, n=number of steps, L=list of sub-parts
        while n>0:
            self.PlayTon(x,L)
            y=self.Next(x)
            print('{3}:{0}--{2}-->{1}'.format(x,y,self.time[x]*self.TimeAtom,self.prob[(x,y)]))
            x=y
            n-=1
#-----------------------------------------------------------
#----EXAMPLE GRAPH------------------------------------------
#-----------------------------------------------------------
F112=Graph('F112')
F112.addArrow(  1,9  )
F112.addArrow(  1,2  )
F112.addArrow(  2,1  )
F112.addArrow(  3,4  )
F112.addArrow(  4,5  )
F112.addArrow(  5,3  )
F112.addArrow(  6,9  )
F112.addArrow(  9,8  )
F112.addArrow(  8,7  )
F112.addArrow(  7,6  )
F112.addArrow(  3,8  )
F112.addArrow(  3,9  )
F112.addArrow(  1,6  )
F112.addArrow(  2,7  )
F112.addArrow(  2,8  )
F112.addArrow(  12,13)
F112.addArrow(  13,14)
F112.addArrow(  14,12)
F112.addArrow(  10,11)
F112.addArrow(  11,10)
F112.addArrow(  6,12 )
F112.addArrow(  7,13 )
F112.addArrow(  3,14 )
F112.addArrow(  5,11 )
F112.addArrow(  11,14)
F112.addArrow(  10,12)
#-----------------------------------------------------------
#----EXAMPLE PART-------------------------------------------
#-----------------------------------------------------------
TEST=Part('TEST')
TEST.setPlsPerMin(120)
TEST.addDot('U')
TEST.addDot(1)
TEST.setTimeout(1,3)
TEST.addDot(2)
TEST.addDot('X')
TEST.addDot('Y')
TEST.addDot('Z')
TEST.setTimeout('Z',7)
TEST.addDot('W')
TEST.addTon('X','A4',0)
TEST.addTon('X','A5',0)
TEST.addTon(1,'F5',0)
TEST.addTon(2,'C5',1)
TEST.addTon('U','D4',1)
TEST.addTon('U','E4',1)
TEST.addTon('Y','C3',2)
TEST.addTon('Z','B4',2)
TEST.addTon('W','G#1',3)
TEST.addTon('W','A2',3)
TEST.addTon('W','B2',3)
TEST.addArrow('Y','X',16)
TEST.addArrow('X','Z',5)
TEST.addArrow('X',1,3)
TEST.addArrow('Y',1,5)
TEST.addArrow('X',2,9)
TEST.addArrow(2,1,6)
TEST.addArrow(1,'Z',2)
TEST.addArrow('Z',2,5)
TEST.addArrow('U','X',4)
TEST.addArrow('X','W',5)
TEST.addArrow('W','X',1)
TEST.addArrow(2,'U',1)
TEST.showPart()
#-----------------------------------------------------------
KUNG=Part('KUNG')
KUNG.setPlsPerMin(120)
for i in range(1,23):
    KUNG.addDot(i)
for i in range(1,23):
    KUNG.addArrow(i,i+1,1)
KUNG.addArrow(22,1,1)
KUNGTIME=[2,1,2,2,1,2,2,1,1,2,3,2,1,2,2,1,2,2,1,2,2,3]
for i in range(1,23):
    KUNG.setTimeout(i,KUNGTIME[i-1])
KUNG.addTon(22,'BEL2','bel')
KUNG.addTon(22,'C4','bel')
KUNG.addTon(22,'A4','kng')
KUNG.addTon(1 ,'D3','kng')
KUNG.addTon(2 ,'BIPP','clv')
KUNG.addTon(3 ,'F3','kng')
KUNG.addTon(4 ,'D4','bel')
KUNG.addTon(4 ,'BEL2','bel')
KUNG.addTon(5 ,'C3','kng')
KUNG.addTon(6 ,'BIPP','clv')
KUNG.addTon(6 ,'A4','kng')
KUNG.addTon(7 ,'D3','kng')
KUNG.addTon(8 ,'BEL2','bel')
KUNG.addTon(8 ,'E4','bel')
KUNG.addTon(9 ,'F3','kng')
KUNG.addTon(10,'BEL2','bel')
KUNG.addTon(10,'F4','bel')
KUNG.addTon(11,'BIPP','clv')
KUNG.addTon(11,'A4','kng')
KUNG.addTon(12,'D3','kng')
KUNG.addTon(13,'BEL2','bel')
KUNG.addTon(13,'G4','bel')
KUNG.addTon(14,'F3','kng')
KUNG.addTon(15,'BIPP','clv')
KUNG.addTon(16,'C3','kng')
KUNG.addTon(17,'BEL2','bel')
KUNG.addTon(17,'A5','bel')
KUNG.addTon(17,'A4','kng')
KUNG.addTon(18,'F3','kng')
KUNG.addTon(19,'BIPP','clv')
KUNG.addTon(20,'WHOM','kng')
KUNG.addTon(20,'A3','kng')
KUNG.addTon(21,'BEL2','bel')
KUNG.addTon(21,'B5','bel')
KUNG.showPart()
#-----------------------------------------------------------
TIME=Part('TIME')
TIME.setPlsPerMin(120)
for i in range(1,5):
    TIME.addDot(i)
for i in range(1,5):
    TIME.addArrow(i,i+1,1)
TIME.addArrow(4,1,1)
TIME.addTon(1,'WHOM',1)
TIME.addTon(2,'BEL2',2)
TIME.addTon(3,'WHOM',1)
TIME.addTon(4,'BEL2',2)
TIME.showPart()
#-----------------------------------------------------------
KUN2=Part('KUN2')
KUN2.setPlsPerMin(300)
for i in range(1,15):
    KUN2.addDot(i)
for i in range(1,15):
    KUN2.addArrow(i,i+1,1)
KUN2.addArrow(14,1,1)
KUN2TIME=[2,1,1,2,2,1,1,4,1,1,2,2,2,2,2]
for i in range(1,15):
    KUN2.setTimeout(i,KUN2TIME[i-1])
KUN2.addTon(14,'C3','kn2')
KUN2.addTon(1 ,'G3','kn2')
KUN2.addTon(2 ,'D3','kn2')
KUN2.addTon(3 ,'E3','kn2')
KUN2.addTon(4 ,'C3','kn2')
KUN2.addTon(5 ,'G3','kn2')
KUN2.addTon(6 ,'D3','kn2')
KUN2.addTon(7 ,'E3','kn2')
KUN2.addTon(8 ,'G3','kn2')
KUN2.addTon(9 ,'D3','kn2')
KUN2.addTon(10,'E3','kn2')
KUN2.addTon(11,'C3','kn2')
KUN2.addTon(12,'G3','kn2')
KUN2.addTon(13,'D3','kn2')
KUN2.showPart()
#-----------------------------------------------------------
KUN3=Part('KUN3')
KUN3.setPlsPerMin(1200)
for i in range(1,16):
    KUN3.addDot(i)
for i in range(1,16):
    KUN3.addArrow(i,i+1,1)
KUN3.addArrow(15,1,1)
KUN3TIME=[4,1,1,2,2,1,1,4,1,1,2,2,2,2]
for i in range(1,15):
    KUN3.setTimeout(i,KUN3TIME[i-1])
KUN3.addTon(15,'BEL2','prt1')
KUN3.addTon(15,'G4','prt3')
KUN3.addTon(1 ,'D4','prt3')
KUN3.addTon(2 ,'BIPP','prt2')
KUN3.addTon(2 ,'E4','prt3')
KUN3.addTon(3 ,'BEL2','prt1')
KUN3.addTon(3 ,'G4','prt3')
KUN3.addTon(4 ,'BIPP','prt2')
KUN3.addTon(4 ,'G4','prt3')
KUN3.addTon(5 ,'D4','prt3')
KUN3.addTon(6 ,'BEL2','prt1')
KUN3.addTon(6 ,'E4','prt3')
KUN3.addTon(7 ,'BEL2','prt1')
KUN3.addTon(8 ,'BIPP','prt2')
KUN3.addTon(8 ,'G4','prt3')
KUN3.addTon(9 ,'D4','prt3')
KUN3.addTon(10,'BEL2','prt1')
KUN3.addTon(10,'E4','prt3')
KUN3.addTon(11 ,'BIPP','prt2')
KUN3.addTon(11,'C4','prt3')
KUN3.addTon(12,'G4','prt3')
KUN3.addTon(13,'BIPP','prt2')
KUN3.addTon(13,'D4','prt3')
KUN3.addTon(14,'BEL2','prt1')
KUN3.addTon(14,'C4','prt3')
KUN3.showPart() 




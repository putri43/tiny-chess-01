import json, os, random, sys, urllib.error, urllib.request
V=(0,100,320,330,500,900,0)
KN=(-33,-31,-18,-14,14,18,31,33); KI=(-17,-16,-15,-1,1,15,16,17)
BD=(-17,-15,15,17); RD=(-16,-1,1,16)
_R=random.Random(1234)
Z=[[ _R.getrandbits(64) for _ in range(128)] for _ in range(13)]
ZS=_R.getrandbits(64); ZC=[_R.getrandbits(64) for _ in range(16)]; ZE=[_R.getrandbits(64) for _ in range(8)]
def on(s): return 0<=s<128 and not (s&0x88)
def _mk(a):
    w=[0]*128
    for s in range(128):
        if s&0x88: continue
        f=s&7; r=s>>4; cen=14-abs(2*f-7)-abs(2*r-7)
        if a==1: w[s]=100+(6-r)*(9 if 2<=f<=5 else 4)+(4 if 2<=f<=5 else 0)+(20 if r==1 else 0)
        elif a==2: w[s]=320+cen*4
        elif a==3: w[s]=330+cen*3
        elif a==4: w[s]=500+cen*2+(12 if r==6 else 0)
        elif a==5: w[s]=900+cen*2
    return w
PT=[0]+[_mk(a) for a in range(1,7)]
def P(v,s):
    a=abs(v); return PT[a][s] if v>0 else -PT[a][s^0x70]
def kb(v,s,mat):
    f=s&7; r=s>>4; cen=14-abs(2*f-7)-abs(2*r-7); b=cen*3 if mat<=1400 else -cen*2
    return b if v>0 else -b
def H(k0,k1,b):
    s=0
    for k,pc,dr in ((k0,1,-16),(k1,-1,16)):
        c=0
        for df in (-1,0,1):
            q=k+dr+df
            if on(q) and b[q]==pc: c+=1
        v=12*c-(25 if c==0 else 0)
        s+= v if pc>0 else -v
    return s
class E:
    def __init__(self):
        self.b=[0]*128; self.t=1; self.c=0; self.e=-1; self.k=[0,0]
        self.pl=[[],[]]; self.sc=0; self.h=0; self.st=[]; self.bc=[0,0]; self.mat=0; self.np=[0,0]; self.rp=set()
        self.nd=0; self.lm=35000; self.tt={}; self.ki=[[0,0] for _ in range(128)]; self.hi={}
    def parse(self,fen):
        p=fen.split(); mp={'p':1,'n':2,'b':3,'r':4,'q':5,'k':6}
        for r,row in enumerate(p[0].split('/')):
            f=0
            for ch in row:
                if ch.isdigit(): f+=int(ch)
                else:
                    v=mp[ch.lower()]*(1 if ch.isupper() else -1); sq=r*16+f
                    self.b[sq]=v; self.pl[0 if v>0 else 1].append(sq)
                    self.sc+=P(v,sq); self.h^=Z[v+6][sq]
                    if abs(v)==6: self.k[0 if v>0 else 1]=sq
                    if abs(v)==3: self.bc[0 if v>0 else 1]+=1
                    if abs(v)!=6: self.mat+=V[abs(v)]
                    if abs(v) not in (1,6): self.np[0 if v>0 else 1]+=V[abs(v)]
                    f+=1
        self.t=1 if p[1]=='w' else -1; self.c=0
        if len(p)>2:
            if 'K' in p[2]: self.c|=1
            if 'Q' in p[2]: self.c|=2
            if 'k' in p[2]: self.c|=4
            if 'q' in p[2]: self.c|=8
        self.h^=ZC[self.c]
        if self.t<0: self.h^=ZS
        self.e=-1
        if len(p)>3 and p[3]!='-':
            self.e=(ord(p[3][0])-97)+(8-int(p[3][1]))*16; self.h^=ZE[self.e&7]
        if self.bc[0]>=2: self.sc+=30
        if self.bc[1]>=2: self.sc-=30
        self.sc+=kb(6,self.k[0],self.mat)+kb(-6,self.k[1],self.mat)
    def T(self,sq,by):
        b=self.b
        if by>0:
            if on(sq+17) and b[sq+17]==1: return True
            if on(sq+15) and b[sq+15]==1: return True
        else:
            if on(sq-17) and b[sq-17]==-1: return True
            if on(sq-15) and b[sq-15]==-1: return True
        for o in KN:
            to=sq+o
            if on(to) and b[to]==by*2: return True
        for o in KI:
            to=sq+o
            if on(to) and b[to]==by*6: return True
        for o in BD:
            s=sq+o
            while on(s):
                v=b[s]
                if v:
                    if v==by*3 or v==by*5: return True
                    break
                s+=o
        for o in RD:
            s=sq+o
            while on(s):
                v=b[s]
                if v:
                    if v==by*4 or v==by*5: return True
                    break
                s+=o
        return False
    def V(self):
        return self.sc*self.t+H(self.k[0],self.k[1],self.b)*self.t
    def G(self):
        b=self.b; t=self.t; ms=[]; ap=ms.append
        for s in list(self.pl[0 if t>0 else 1]):
            v=b[s]; a=abs(v)
            if a==1:
                d=-16*t; f=s+d
                if on(f) and b[f]==0:
                    if (f>>4)==(0 if t>0 else 7):
                        for pr in (5,4,3,2): ap(s|(f<<7)|(pr<<14))
                    else:
                        ap(s|(f<<7))
                        f2=s+2*d
                        if ((s>>4)==(6 if t>0 else 1)) and b[f2]==0: ap(s|(f2<<7))
                for o in (d-1,d+1):
                    to=s+o
                    if not on(to): continue
                    w=b[to]
                    if w and (w>0)!=(t>0):
                        if (to>>4)==(0 if t>0 else 7):
                            for pr in (5,4,3,2): ap(s|(to<<7)|(pr<<14))
                        else: ap(s|(to<<7))
                    elif to==self.e and w==0: ap(s|(to<<7))
            elif a in (2,6):
                for o in (KN if a==2 else KI):
                    to=s+o
                    if not on(to): continue
                    w=b[to]
                    if w==0 or (w>0)!=(t>0): ap(s|(to<<7))
                if a==6:
                    if t>0 and s==116:
                        if self.c&1 and b[117]==0 and b[118]==0 and b[119]==4 and not self.T(116,-t) and not self.T(117,-t) and not self.T(118,-t): ap(116|(118<<7))
                        if self.c&2 and b[115]==0 and b[114]==0 and b[113]==0 and b[112]==4 and not self.T(116,-t) and not self.T(115,-t) and not self.T(114,-t): ap(116|(114<<7))
                    if t<0 and s==4:
                        if self.c&4 and b[5]==0 and b[6]==0 and b[7]==-4 and not self.T(4,-t) and not self.T(5,-t) and not self.T(6,-t): ap(4|(6<<7))
                        if self.c&8 and b[3]==0 and b[2]==0 and b[1]==0 and b[0]==-4 and not self.T(4,-t) and not self.T(3,-t) and not self.T(2,-t): ap(4|(2<<7))
            else:
                for o in (BD if a==3 else RD if a==4 else BD+RD):
                    to=s+o
                    while on(to):
                        w=b[to]
                        if w==0: ap(s|(to<<7))
                        else:
                            if (w>0)!=(t>0): ap(s|(to<<7))
                            break
                        to+=o
        return ms
    def K(self,m):
        s=m&127; to=(m>>7)&127; pr=m>>14; b=self.b; v=b[s]; cap=b[to]
        epcap=0; epsq=-1
        if abs(v)==1 and to==self.e and cap==0:
            epsq=to+16*self.t; epcap=b[epsq]
        oldc=self.c; olde=self.e
        self.sc-=kb(6,self.k[0],self.mat)+kb(-6,self.k[1],self.mat)
        self.h^=ZC[self.c]
        if olde>=0: self.h^=ZE[olde&7]
        self.st.append((m,cap,epcap,epsq,oldc,olde))
        self.sc-=P(v,s); self.h^=Z[v+6][s]
        if cap:
            self.sc-=P(cap,to); self.h^=Z[cap+6][to]; self.mat-=V[abs(cap)]
            if abs(cap)!=1: self.np[0 if cap>0 else 1]-=V[abs(cap)]
        if epcap:
            self.sc-=P(epcap,epsq); self.h^=Z[epcap+6][epsq]; b[epsq]=0; self.mat-=100
            self.pl[0 if epcap>0 else 1].remove(epsq)
        if cap: self.pl[0 if cap>0 else 1].remove(to)
        nv=pr*self.t if pr else v
        if pr: self.mat+=V[pr]-100; self.np[0 if v>0 else 1]+=V[pr]
        b[to]=nv; b[s]=0
        self.sc+=P(nv,to); self.h^=Z[nv+6][to]
        pl=self.pl[0 if v>0 else 1]; pl.remove(s); pl.append(to)
        if pr==3:
            self.bc[0 if v>0 else 1]+=1
            if self.bc[0 if v>0 else 1]==2: self.sc+=30 if v>0 else -30
        if abs(v)==6:
            self.k[0 if v>0 else 1]=to
            if to-s==2:
                r=b[to+1]; b[to-1]=r; b[to+1]=0; self.sc-=P(r,to+1); self.sc+=P(r,to-1); self.h^=Z[r+6][to+1]; self.h^=Z[r+6][to-1]
                pl.remove(to+1); pl.append(to-1)
            elif to-s==-2:
                r=b[to-2]; b[to+1]=r; b[to-2]=0; self.sc-=P(r,to-2); self.sc+=P(r,to+1); self.h^=Z[r+6][to-2]; self.h^=Z[r+6][to+1]
                pl.remove(to-2); pl.append(to+1)
            self.c&=~(3 if v>0 else 12)
        if abs(v)==4:
            if s==112: self.c&=~2
            if s==119: self.c&=~1
            if s==0: self.c&=~8
            if s==7: self.c&=~4
        if cap:
            if to==112: self.c&=~2
            if to==119: self.c&=~1
            if to==0: self.c&=~8
            if to==7: self.c&=~4
        if cap and abs(cap)==3:
            self.bc[0 if cap>0 else 1]-=1
            if self.bc[0 if cap>0 else 1]==1: self.sc-=30 if cap>0 else -30
        self.e=(s+to)//2 if abs(v)==1 and abs(to-s)==32 else -1
        if self.e>=0: self.h^=ZE[self.e&7]
        self.h^=ZC[self.c]
        self.sc+=kb(6,self.k[0],self.mat)+kb(-6,self.k[1],self.mat)
        self.t=-self.t; self.h^=ZS
    def N(self):
        m,cap,epcap,epsq,oldc,olde=self.st.pop()
        s=m&127; to=(m>>7)&127; pr=m>>14; b=self.b; v=b[to]
        self.sc-=kb(6,self.k[0],self.mat)+kb(-6,self.k[1],self.mat)
        if pr: self.mat-=V[pr]-100; self.np[0 if v>0 else 1]-=V[pr]
        if cap: self.mat+=V[abs(cap)]
        if cap and abs(cap)!=1: self.np[0 if cap>0 else 1]+=V[abs(cap)]
        self.h^=ZC[self.c]
        if self.e>=0: self.h^=ZE[self.e&7]
        self.sc-=P(v,to); self.h^=Z[v+6][to]
        if pr==3:
            self.bc[0 if v>0 else 1]-=1
            if self.bc[0 if v>0 else 1]==1: self.sc-=30 if v>0 else -30
        pl0=self.pl[0 if v>0 else 1]
        if abs(v)==6 and to-s==2:
            r=b[to-1]; b[to+1]=r; b[to-1]=0; self.sc-=P(r,to-1); self.sc+=P(r,to+1); self.h^=Z[r+6][to-1]; self.h^=Z[r+6][to+1]
            pl0.remove(to-1); pl0.append(to+1)
        elif abs(v)==6 and to-s==-2:
            r=b[to+1]; b[to-2]=r; b[to+1]=0; self.sc-=P(r,to+1); self.sc+=P(r,to-2); self.h^=Z[r+6][to+1]; self.h^=Z[r+6][to-2]
            pl0.remove(to+1); pl0.append(to-2)
        pl=self.pl[0 if v>0 else 1]; pl.remove(to)
        mover=(-self.t) if pr else v
        b[s]=mover; b[to]=cap
        self.sc+=P(mover,s); self.h^=Z[mover+6][s]
        if cap:
            self.sc+=P(cap,to); self.h^=Z[cap+6][to]
            self.pl[0 if cap>0 else 1].append(to)
            if abs(cap)==3:
                self.bc[0 if cap>0 else 1]+=1
                if self.bc[0 if cap>0 else 1]==2: self.sc+=30 if cap>0 else -30
        pl.append(s)
        if epcap:
            b[epsq]=epcap; self.sc+=P(epcap,epsq); self.h^=Z[epcap+6][epsq]; self.mat+=100; self.pl[0 if epcap>0 else 1].append(epsq)
        if abs(v)==6: self.k[0 if v>0 else 1]=s
        self.c=oldc; self.e=olde; self.t=-self.t; self.h^=ZS
        self.h^=ZC[self.c]
        if olde>=0: self.h^=ZE[olde&7]
        self.sc+=kb(6,self.k[0],self.mat)+kb(-6,self.k[1],self.mat)
    def O(self,ms,ply,ttm):
        b=self.b
        def sc(m):
            s_=m&127; to=(m>>7)&127; pr=m>>14; v=b[to]; x=0
            if m==ttm: x+=10000
            if v: x+=10*V[abs(v)]-V[abs(b[s_])]
            if pr: x+=900+V[pr]
            if m==self.ki[ply][0]: x+=500
            elif m==self.ki[ply][1]: x+=400
            x+=self.hi.get(m,0)//16
            return -x
        return sorted(ms,key=sc)
    def q(self,al,be,ply,qd=0):
        self.nd+=1
        if self.nd>self.lm: raise TimeoutError
        if qd>6: return self.V()
        inchk=self.T(self.k[0 if self.t>0 else 1],-self.t)
        if not inchk:
            st=self.V()
            if st>=be: return be
            if st>al: al=st
        ms=self.G()
        if not inchk:
            ms=[m for m in ms if self.b[(m>>7)&127]!=0 or (m>>14) or ((m>>7)&127)==self.e]
        ms=self.O(ms,ply,None)
        legal=0
        for m in ms:
            if not inchk:
                to=(m>>7)&127; cv=V[abs(self.b[to])] if self.b[to] else (100 if to==self.e else 0)
                if (m>>14): cv+=V[m>>14]
                if st+cv+200<al: continue
            self.K(m)
            if self.T(self.k[0 if self.t<0 else 1], self.t):
                self.N(); continue
            legal+=1
            sc=-self.q(-be,-al,ply+1,qd+1)
            self.N()
            if sc>=be: return be
            if sc>al: al=sc
        if inchk and legal==0: return -99999+ply
        return al
    def ab(self,al,be,d,ply):
        self.nd+=1
        if self.nd>self.lm: raise TimeoutError
        if d<=0: return self.q(al,be,ply)
        ent=self.tt.get(self.h); ttm=0
        if ent and ent[0]>=d:
            _,sc,fl,bm=ent; ttm=bm
            if fl==0: return sc
            if fl==1 and sc>=be: return sc
            if fl==2 and sc<=al: return sc
        inchk=self.T(self.k[0 if self.t>0 else 1],-self.t)
        if d>=3 and not inchk and self.np[0 if self.t>0 else 1]>0:
            oe=self.e; oc=self.c; oh=self.h
            if oe>=0: self.h^=ZE[oe&7]
            self.e=-1; self.t=-self.t; self.h^=ZS
            try: sc=-self.ab(-be,-be+1,d-3,ply+1)
            except TimeoutError:
                self.e=oe; self.c=oc; self.h=oh; self.t=-self.t; raise
            self.e=oe; self.c=oc; self.h=oh; self.t=-self.t
            if sc>=be: return be
        ms=self.O(self.G(),ply,ttm)
        best=0; orig=al; legal=0; first=True
        for m in ms:
            to=(m>>7)&127; quiet=self.b[to]==0 and not (m>>14) and to!=self.e
            self.K(m)
            if self.T(self.k[0 if self.t<0 else 1], self.t):
                self.N(); continue
            legal+=1
            if first:
                sc=-self.ab(-be,-al,d-1,ply+1); first=False
            elif d>=3 and legal>4 and quiet and not inchk:
                sc=-self.ab(-al-1,-al,d-2,ply+1)
                if sc>al: sc=-self.ab(-be,-al,d-1,ply+1)
            else:
                sc=-self.ab(-al-1,-al,d-1,ply+1)
                if al<sc<be: sc=-self.ab(-be,-al,d-1,ply+1)
            self.N()
            if sc>=be:
                self.tt[self.h]=(d,be,1,m)
                if quiet:
                    if m!=self.ki[ply][0]: self.ki[ply][1]=self.ki[ply][0]; self.ki[ply][0]=m
                    self.hi[m]=self.hi.get(m,0)+d*d
                return be
            if sc>al: al=sc; best=m
        if legal==0:
            return -99999+ply if inchk else 0
        fl=0 if al>orig else 2
        self.tt[self.h]=(d,al,fl,best)
        return al
    def R(self,depth):
        ms=self.O(self.G(),0,None)
        best=0; al=-1000000; legal=0; first=True
        for m in ms:
            self.K(m)
            if self.T(self.k[0 if self.t<0 else 1], self.t):
                self.N(); continue
            legal+=1
            try:
                if first:
                    sc=-self.ab(-1000000,1000000,depth-1,1); first=False
                else:
                    sc=-self.ab(-al-1,-al,depth-1,1)
                    if al<sc<1000000: sc=-self.ab(-1000000,-al,depth-1,1)
            except TimeoutError:
                self.N(); raise
            self.N()
            if sc>al: al=sc; best=m
        return (best,al) if legal else (None,al)
    def C(self,limit=45000):
        self.lm=limit; self.nd=0; self.tt={}
        best=None
        for d in range(1,8):
            try:
                r=self.R(d)
                if r and r[0]: best=r[0]
                else: break
            except TimeoutError:
                break
        return best
ENV_URL=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("EURL is not set")
def post(path,body):
    req=urllib.request.Request(ENV_URL+path,data=json.dumps(body).encode(),headers={"content-type":"application/json"})
    try:
        with urllib.request.urlopen(req) as res: return json.load(res)
    except urllib.error.HTTPError as e:
        sys.exit(f"{path} {e.code}")
def uci(m):
    f="abcdefgh"; s=m&127; t=(m>>7)&127; pr=m>>14
    return f[s&7]+str(8-(s>>4))+f[t&7]+str(8-(t>>4))+("qrbn"[pr-2] if pr else "")
if __name__=="__main__":
    while True:
        g=post("/game",{})
        if g["status"]=="done": break
        while g["status"]=="your_move":
            e=E(); e.parse(g["fen"])
            m=e.C()
            if m is None: m=e.legal()[0]
            mv=uci(m)
            if mv not in g["legal_moves"]: mv=g["legal_moves"][0]
            g=post("/move",{"game":g["game"],"move":mv})
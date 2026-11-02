# Fifth House motto fix at full res (1080x1920): I EXPRESS -> I CREATE, harvesting gold letters from sibling House cards.
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import distance_transform_edt, map_coordinates, gaussian_filter
sys.path.insert(0,'/tmp/w')
K=2; W=1080; Y0,Y1=1120,1800; H=Y1-Y0; CX=540; TOP=326.0  # settled cap top row (band coords) = (723-560)*2
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; SIZE=86.4; SS=2
L=lambda f: np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
shapeLD=np.load('/tmp/w/shape.npy'); ALD=np.load('/tmp/w/A.npy')
def bgf(i):
  s=L('/tmp/w/sky_%03d.png'%i)[560:900]; b=s*(1-ALD[i-1]*(1-shapeLD))[...,None]
  return np.asarray(Image.fromarray(np.clip(b,0,255).astype(np.uint8)).resize((W,H),Image.BICUBIC)).astype(np.float32)
def glyphs(word):
  f=ImageFont.truetype(F,int(round(SIZE*SS)),layout_engine=ImageFont.Layout.RAQM)
  d=ImageDraw.Draw(Image.new('L',(10,10))); l,t,r,b=d.textbbox((0,0),word,font=f); x0=CX*SS-(r-l)/2-l
  def render(s): im=Image.new('L',(W*SS,400*SS)); ImageDraw.Draw(im).text((x0,0),s,font=f,fill=255); return np.asarray(im).astype(np.float32)
  out=[]; prev=np.zeros((400*SS,W*SS),np.float32)
  for i in range(1,len(word)+1):
    cur=render(word[:i]); m=np.clip(cur-prev,0,255); prev=cur
    if word[i-1]!=' ': out.append((word[i-1],m.reshape(400,SS,W,SS).mean((1,3))/255))
  allm=sum(m for _,m in out); top=np.where(allm.max(1)>0.3)[0].min()
  res=[]
  for ch,m in out:
    full=np.zeros((H,W),np.float32); dy=int(TOP)-top; full[max(dy,0):dy+400]=m[max(-dy,0):H-dy] if dy+400>H else m[max(-dy,0):]
    res.append((ch,full))
  return res
G024=glyphs('I VALUE')
SRC={'027':glyphs('I EXPRESS'),'025':glyphs('I CONNECT'),'032':glyphs('I ACHIEVE')}
TGT=glyphs('I CREATE')
PLAN=[('027',0),('025',1),('027',4),('027',1),('032',1),('025',7),('027',5)]
FIT=np.load('/tmp/w/fit.npy',allow_pickle=True).item()
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def warp(img,a,top):
  xs=CX+(xx-CX)/a; ys=TOP+(yy-top)/a
  return map_coordinates(img,[ys,xs],order=1,cval=0)
def owner(masks,a,top):
  ds=np.stack([distance_transform_edt(warp(m,a,top)<0.3) for _,m in masks]); return ds.argmin(0),ds.min(0),ds
def centerx(m): xs=np.where(m.max(0)>0.3)[0]; return (xs.min()+xs.max())/2.0
def shiftx(img,dx):
  if img.ndim==2: return map_coordinates(img,[yy,xx-dx],order=1,cval=0)
  return np.stack([map_coordinates(img[...,c],[yy,xx-dx],order=1,cval=0) for c in range(3)],-1)
def frame(i):
  C=L('027_%03d.png'%i)
  if i<81 or i>=143: return C
  band=C[Y0:Y1].copy(); b=bgf(i)
  if i<98: a,top,_=FIT[i]; top=(top+1.5)*K
  else: a,top=1.0,TOP
  R=(50 if i>=134 else 36)*a; RR=(62 if i>=134 else 46)*a
  oo,od,_=owner(SRC['027'],a,top)
  rm=np.clip((RR-od)/12,0,1)[...,None]; out=band*(1-rm)+b*rm
  srcs={k:L('%s_%03d.png'%(k,i))[Y0:Y1] for k in SRC}
  own={k:owner(SRC[k],a,top) for k in SRC}
  to,td,tds=owner(TGT,a,top)
  if i<134:   # gold letters: sharp sky recovered under the old shadow/glow, new shadow/glow modelled, letter faces harvested
    sS,gC=1.369,np.array([132.7,83.45,38.08],np.float32)
    aO=np.clip(sum(warp(m,a,top) for _,m in SRC['027']),0,1); aN=np.clip(sum(warp(m,a,top) for _,m in TGT),0,1)
    BsO=gaussian_filter(aO,10*a); BgO=gaussian_filter(aO,14*a); BsN=gaussian_filter(aN,10*a); BgN=gaussian_filter(aN,14*a)
    den=np.maximum(1-sS*BsO,0.2)[...,None]
    inv=(band-gC*BgO[...,None])/den
    near=np.clip((11*a-od)/(4*a),0,1)[...,None]          # inside/at old letters: no sky info, use the soft sky
    sky=inv*(1-near)+b*near
    out=sky*(1-sS*BsN)[...,None]+gC*BgN[...,None]
    for j,(k,si) in enumerate(PLAN):
      dx=a*(centerx(TGT[j][1])-centerx(SRC[k][si][1]))
      S=shiftx(srcs[k],dx)
      al=np.clip((warp(TGT[j][1],a,top)-0.15)/0.6,0,1)[...,None]
      out=out*(1-al)+S*al
  else:       # flare / glitter: additive particle layers, soft partition
    d24=distance_transform_edt(np.clip(sum(warp(m,a,top) for _,m in G024),0,1)<0.3)
    c24=L('024_%03d.png'%i)[Y0:Y1]; w24=np.clip((d24-28)/10,0,1)[...,None]
    bb=c24*w24+b*(1-w24)
    out=band*(1-rm)+bb*rm
    e=np.exp(-(tds-tds.min(0))/6); wt=e/e.sum(0); env=np.clip((50-td)/15,0,1)
    layer=np.zeros_like(out)
    for j,(k,si) in enumerate(PLAN):
      dx=centerx(TGT[j][1])-centerx(SRC[k][si][1])
      ds=own[k][2]; es=np.exp(-(ds-ds.min(0))/4); ws=(es/es.sum(0))[si]
      Dsrc=np.maximum(srcs[k]-b,-6)*ws[...,None]
      layer+=shiftx(Dsrc,dx)*wt[j][...,None]
    reg=np.clip((R*1.6-od)/12,0,1)  # where old content was removed
    out=out+layer*np.maximum(env,reg)[...,None]
  res=C.copy(); res[Y0:Y1]=out
  if 140<=i<=142: t=(i-139)/4; res=res*(1-t)+C*t
  return res
if __name__=='__main__':
  rng=range(1,176) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
  for i in rng: Image.fromarray(np.clip(frame(i),0,255).astype(np.uint8)).save('out/h_%03d.png'%i)

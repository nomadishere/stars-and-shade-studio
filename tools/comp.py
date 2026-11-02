import numpy as np, sys
sys.path.insert(0,'.')
from glyph import glyph_masks
from PIL import Image
from scipy.ndimage import distance_transform_edt, map_coordinates, gaussian_filter, binary_opening
L=lambda f: np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
Y0,Y1=560,900
shape=np.load('shape.npy'); A=np.load('A.npy')
def bgf(i): s=L('sky_%03d.png'%i)[Y0:Y1]; return s*(1-A[i-1]*(1-shape))[...,None]
H,W=Y1-Y0,540
def gm(word):
  return [(ch,m[Y0:Y1]) for ch,m in glyph_masks(word)]
SRC={'c':gm('I EXPRESS'),'025':gm('I CONNECT'),'032':gm('I ACHIEVE')}
TGT=gm('I CREATE')
# target letter -> (card, index in source word)
PLAN=[('c',0),('025',1),('c',4),('c',1),('032',1),('025',7),('c',5)]  # I C R E A T E
def centerx(m): xs=np.where(m.max(0)>0.3)[0]; return (xs.min()+xs.max())/2.0
def owner(masks, a, top, cx_t):
  """partition map: nearest glyph index for each pixel, glyphs transformed for frame (scale a about x=270, rows top)"""
  dist=[]
  for _,m in masks:
    mt=warp(m,a,top,cx_t)
    dist.append(distance_transform_edt(mt<0.3))
  dist=np.stack(dist); return dist.argmin(0), dist.min(0)
def warp(img,a,top,cx_t):
  """settled-space image -> frame space: x' = cx_t + a*(x-270); y' = top + a*(y-163) (163 = settled top row 723 in band coords)"""
  yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
  xs=270+(xx-cx_t)/a; ys=163+(yy-top)/a
  if img.ndim==2: return map_coordinates(img,[ys,xs],order=1,cval=0)
  return np.stack([map_coordinates(img[...,c],[ys,xs],order=1,cval=0) for c in range(img.shape[2])],-1)
# per-frame transform from 027's own motto
def transform(i,b):
  D=L('c_%03d.png'%i)[Y0:Y1]-b; m=binary_opening(D.sum(2)>90,np.ones((2,2))); m[:40]=False
  ys,xs=np.where(m)
  top=np.percentile(ys,2); bot=np.percentile(ys,98)
  a=min(1.0,(bot-top)/31.0); cx=(np.percentile(xs,1)+np.percentile(xs,99))/2
  return a,top,cx
def frame_harvest(i):
  R=18 if i>=134 else 10
  b=bgf(i)
  FIT=np.load('fit.npy',allow_pickle=True).item()
  if i<98: a,top,_=FIT[i]; top+=1.5; cx=270.0
  else: a,top,cx=1.0,163.0,270.0   # settled
  cx_t=cx  # word center in frame
  out=L('c_%03d.png'%i)[Y0:Y1].copy()
  # remove old motto: replace region around old glyphs (dilated) with bg
  oldo,oldd=owner(SRC['c'],a,top,cx_t)
  rm=np.clip((R*a-oldd)/4,0,1)[...,None]   # feathered region within ~10px of old glyphs
  out=out*(1-rm)+b*rm
  srcs={k:L('%s_%03d.png'%(k,i))[Y0:Y1] for k in SRC}
  owns={k:owner(SRC[k],a,top,cx_t) for k in SRC}
  tgto,tgtd=owner(TGT,a,top,cx_t)
  yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
  for j,(k,si) in enumerate(PLAN):
    xs_src=centerx(SRC[k][si][1]); xs_tgt=centerx(TGT[j][1])
    dx=a*(xs_tgt-xs_src)
    S=srcs[k]; o,d=owns[k]
    sel=((o==si)&(d<=R*a)).astype(np.float32)
    # shift source pixels by dx (subpixel)
    sh=lambda img: map_coordinates(img,[yy,xx-dx],order=1,cval=0) if img.ndim==2 else np.stack([map_coordinates(img[...,c],[yy,xx-dx],order=1,cval=0) for c in range(3)],-1)
    Ssh=sh(S); Bsh=sh(b); w=sh(sel)
    w=w*((tgto==j)|(tgtd>R*a))   # don't spill into another target glyph's zone
    w=np.clip(w,0,1)
    w=w*np.clip((R*a-tgtd)/4,0,1)  # feather
    diff=Ssh-Bsh; alpha=np.clip(np.abs(diff).sum(2)/90,0,1)[...,None]
    val=Ssh*alpha+(b+diff)*(1-alpha)
    out=out*(1-w[...,None])+val*w[...,None]
  return out
SQ=None
def frame_squeeze(i):
  b=bgf(i); C=L('c_%03d.png'%i)[Y0:Y1]; D=np.maximum(C-b,-6)
  r=215.0/236.0
  yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
  Dq=np.stack([map_coordinates(D[...,c],[yy,270+(xx-270)/r],order=1,cval=0) for c in range(3)],-1)
  # region mask: rows 620..860 abs, feathered
  reg=np.zeros((H,W),np.float32); reg[620-Y0:860-Y0, 40:500]=1; reg=gaussian_filter(reg,6)[...,None]
  new=b+Dq
  return C*(1-reg)+new*reg
def full(i):
  F=L('c_%03d.png'%i).copy()
  if 81<=i<=133: F[Y0:Y1]=frame_harvest(i)
  elif 134<=i<=139: F[Y0:Y1]=frame_dissolve(i)
  elif 140<=i<=142:
    t=(i-139)/4; F[Y0:Y1]=frame_dissolve(i)*(1-t)+frame_squeeze(i)*t
  elif 143<=i<=170: F[Y0:Y1]=frame_squeeze(i)
  return np.clip(F,0,255).astype(np.uint8)
def soft(masks,a,top,cx,tau=5.0):
  ds=np.stack([distance_transform_edt(warp(m,a,top,cx)<0.3) for _,m in masks])
  e=np.exp(-(ds-ds.min(0))/tau); return e/e.sum(0), ds.min(0)
def frame_dissolve(i):
  b=bgf(i); C=L('c_%03d.png'%i)[Y0:Y1]
  reg=np.zeros((H,W),np.float32); reg[600-Y0:800-Y0,90:460]=1; reg=gaussian_filter(reg,6)[...,None]
  out=C*(1-reg)+b*reg
  yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
  wt,dt=soft(TGT,1,163,270)
  env=np.clip((40-dt)/10,0,1)
  layer=np.zeros((H,W,3),np.float32)
  srcsoft={k:soft(SRC[k],1,163,270) for k in SRC}
  for j,(k,si) in enumerate(PLAN):
    dx=centerx(TGT[j][1])-centerx(SRC[k][si][1])
    S=L('%s_%03d.png'%(k,i))[Y0:Y1]; Dsrc=np.maximum(S-b,-6)*srcsoft[k][0][si][...,None]
    Dsh=np.stack([map_coordinates(Dsrc[...,c],[yy,xx-dx],order=1,cval=0) for c in range(3)],-1)
    layer+=Dsh*wt[j][...,None]
  return out+layer*env[...,None]*reg

if __name__=='__main__':
  import os; os.makedirs('out',exist_ok=True)
  rng=range(1,176) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
  for i in rng:
    Image.fromarray(full(i)).save('out/n_%03d.png'%i)


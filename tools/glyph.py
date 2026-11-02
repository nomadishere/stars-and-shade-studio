import numpy as np
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SS=4; SIZE=43.2
def glyph_masks(word, cx=270):
  """per-letter masks (list of (char, mask HxW at 540x960 scale)) for word centered at cx, settled rows."""
  f=ImageFont.truetype(F,int(round(SIZE*SS)),layout_engine=ImageFont.Layout.RAQM)
  d=ImageDraw.Draw(Image.new('L',(10,10)))
  l,t,r,b=d.textbbox((0,0),word,font=f); w=r-l
  x0=cx*SS - w/2 - l
  # full word mask
  def render(s, color_idx=None):
    im=Image.new('L',(540*SS,960*SS)); dd=ImageDraw.Draw(im); dd.text((x0,0),s,font=f,fill=255); return im
  full=np.asarray(render(word)).astype(np.float32)
  masks=[]; prev=np.zeros_like(full)
  for i in range(1,len(word)+1):
    cur=np.asarray(render(word[:i])).astype(np.float32)
    m=np.clip(cur-prev,0,255); prev=cur
    if word[i-1]!=' ': masks.append((word[i-1],m))
  out=[]
  for ch,m in masks:
    m=m.reshape(960,SS,540,SS).mean((1,3))/255
    out.append((ch,m))
  # vertical alignment: shift so that cap rows top align with 723
  allm=sum(m for _,m in out); ys=np.where(allm.max(1)>0.3)[0]
  dy=723-ys.min()
  out=[(ch,np.roll(m,dy,0)) for ch,m in out]
  return out
if __name__=='__main__':
  for w in ['I EXPRESS','I CREATE','I PARTNER','I CONNECT']:
    g=glyph_masks(w)
    print(w,[(ch,int(np.where(m.max(0)>0.3)[0].min()),int(np.where(m.max(0)>0.3)[0].max())) for ch,m in g], 'rows', np.where(sum(m for _,m in g).max(1)>0.3)[0][[0,-1]])

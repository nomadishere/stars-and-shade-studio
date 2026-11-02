import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
L=lambda f: np.asarray(Image.open(f).convert('RGB')).astype(np.float32)
Y0,Y1=560,900
fr=list(range(40,81))
C=np.stack([L('c_%03d.png'%i)[Y0:Y1] for i in fr]); S=np.stack([L('sky_%03d.png'%i)[Y0:Y1] for i in fr])
num=gaussian_filter((C*S).sum((0,3)),12); den=gaussian_filter((S*S).sum((0,3)),12)
shape=num/den; np.save('shape.npy',shape)
print('shape',shape.min(),shape.max(),'resid',np.abs(C-shape[None,...,None]*S).mean())
edge=np.zeros_like(shape,bool); edge[:, :55]=True; edge[:, 485:]=True
A={}
for i in range(1,176):
  c=L('c_%03d.png'%i)[Y0:Y1]; s=L('sky_%03d.png'%i)[Y0:Y1]
  # ratio = 1 - A(1-shape)  -> c = s*(1-A*(1-shape)) ; solve LS on edge pixels
  u=(s*(1-shape)[...,None])[edge]; v=(s-c)[edge]
  A[i]=float((u*v).sum()/(u*u).sum())
np.save('A.npy',np.array([A[i] for i in range(1,176)]))
print([round(A[i],2) for i in range(1,176,5)])
for i in [100,110,140,160]:
  c=L('c_%03d.png'%i)[Y0:Y1]; s=L('sky_%03d.png'%i)[Y0:Y1]; bg=s*(1-A[i]*(1-shape))[...,None]
  print(i, 'resid edges', np.abs(c-bg)[edge].mean(), 'resid row30', np.abs(c-bg)[0:40].mean())

import numpy as np, sys
sys.path.insert(0,'.')
from comp import L,bgf,warp,Y0,Y1
from scipy.optimize import minimize
T=np.maximum(np.abs(L("c_110.png")[Y0:Y1]-bgf(110)).sum(2)-15,0); T[:120]=0; T[230:]=0
res={}
for i in range(81,100):
  O=np.maximum(np.abs(L("c_%03d.png"%i)[Y0:Y1]-bgf(i)).sum(2)-15,0); O[:30]=0; O[230:]=0
  best=None
  for a in np.arange(0.40,1.01,0.02):
    for cx in np.arange(262,282,1.0):
      # top via centroid alignment
      Wt=warp(T,a,0,cx); ys=np.arange(Wt.shape[0]); cyw=(Wt.sum(1)*ys).sum()/Wt.sum(); cyo=(O.sum(1)*ys).sum()/O.sum()
      top=cyo-cyw
      Wt=warp(T,a,top,cx)
      sc=(Wt*O).sum()/np.sqrt((Wt*Wt).sum()*(O*O).sum()+1e-6)
      if best is None or sc>best[0]: best=(sc,a,top,cx)
  res[i]=best[1:]; print(i,[round(float(x),3) for x in best])
np.save('fit.npy',res)

import numpy as np
import segmentationmod 
import stlpair
from stl import mesh

def projectionpt(planedef, point):
    a=planedef[0]
    b=planedef[1]
    c=planedef[2]
    d=planedef[3]
    
    x0=point[0]
    y0=point[1]
    z0=point[2]
    
    t=(-d-a*x0-b*y0-c*z0)/(a*a+b*b+c*c)
    
    x=x0+t*a
    y=y0+t*b
    z=z0+t*c
    
    return [x,y,z]

slicingplane=[]
slicingplane.append([1 ,1, 1, -80])
slicingplane.append([1 ,1, 1, -100])
slicingplane.append([1 ,1, 1, -120])
slicingplane.append([1 ,1, 1, -140])
slicingplane.append([1 ,1, 1, -150])

#define the slicing planes above

originalmesh=mesh.Mesh.from_file('V8 3+2 -whole.stl')

#read the STL file above


stlpairs=[]
stlpairs.append(segmentationmod.segment(originalmesh, slicingplane[0]))
for i in range(1, len(slicingplane)):
    stlpairs.append(segmentationmod.segment(stlpairs[i-1].topstl,slicingplane[i]))
    stlpairs[i-1].topcog=stlpairs[i].bottomcog
    stlpairs[i-1].topstl=stlpairs[i].bottomstl
    stlpairs[i-1].bottomstl.save(str(i-1)+'segment.stl')

#the block above slices the STL into segments. the stlpair object
#contains the 'top' and 'bottom' stl file, along with the COG of each
#and the slicing plane.


#transpose the topcog and get the final centroidonplane

for j in range(0, len(stlpairs)):
    stlpairs[j].centroidonplane=projectionpt(stlpairs[j].planedef, stlpairs[j].topcog)
    print(stlpairs[j].planedef)
    print(stlpairs[j].centroidonplane)
    



    
    


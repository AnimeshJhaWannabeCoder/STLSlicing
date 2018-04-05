import pandas as pd
import numpy as np
from stl import mesh
import stlpair

#sliced returns 1 if all pts are +ve, 2 if all pts are -ve and 3 if the face
#is sliced
def sliced(p1, p2 ,p3, planedef):
    delta1= p1[0]*planedef[0]+p1[1]*planedef[1]+p1[2]*planedef[2]+planedef[3]
    delta2= p2[0]*planedef[0]+p2[1]*planedef[1]+p2[2]*planedef[2]+planedef[3]
    delta3= p3[0]*planedef[0]+p3[1]*planedef[1]+p3[2]*planedef[2]+planedef[3]
    planeside=[False, False, False]
    if delta1>0 : 
        planeside[0]= True
    else:
        pass
    if delta2>0:
        planeside[1]= True
    else:
        pass
    if delta3>0:
        planeside[2]= True
    else:
        pass

    return planeside

#original function above- gave 1 +ve, 2-ve and 3 for sliced

def intersectionpoint(p1 ,p2, planedef):
    
    if np.dot(p1, planedef[0:3])+planedef[3]==0:
        return p1
    elif np.dot(p2, planedef[0:3])+planedef[3]==0:
        return p2
    else:
    
        delx=p2[0]-p1[0]
        dely=p2[1]-p1[1]
        delz=p2[2]-p1[2]
    
        rhs=-(planedef[0]*p1[0]+planedef[1]*p1[1]+planedef[2]*p1[2]+planedef[3])
        lhs=(planedef[0]*delx+planedef[1]*dely+planedef[2]*delz)
        t=rhs/lhs
    
    
        x=p1[0]+delx*t
        y=p1[1]+dely*t
        z=p1[2]+delz*t
    
        return [x,y,z]


    
def segment(playmesh, planedef):
    #playmesh=mesh.Mesh.from_file('V8 3+2 -whole.stl')
    #a=1
    #b=1
    #c=1
    #d=-130
    #planedef=[a,b,c,d]


    positivefile=np.empty([1,9], dtype=float)
    negativefile=np.empty([1,9], dtype=float)
    slicedarr=np.empty([1,9], dtype=float)

    for i in range(0, len(playmesh)):
        p1=playmesh.points[i][0:3].tolist()
        p2=playmesh.points[i][3:6].tolist()
        p3=playmesh.points[i][6:9].tolist()
    
        if np.sum(sliced(p1, p2, p3, planedef))==3:
            positivefile=np.vstack([positivefile, playmesh[i]]) 
        elif np.sum(sliced(p1,p2, p3, planedef))==0:
            negativefile=np.vstack([negativefile, playmesh[i]])
        else:
            slicedarr=np.vstack([slicedarr, playmesh[i]])

    print('boodram')
    positivef=positivefile[1:]
    negativef=negativefile[1:]
    slicef=slicedarr[1:]


#hmm okay this kinda works. Lets get intersection points and stuff, and make new faces.

    planepts=np.asarray([1,1,1])

    for j in range(0, len(slicef)):
        p=[0,0,0]
        p[0]=slicef[j][0:3]
        p[1]=slicef[j][3:6]
        p[2]=slicef[j][6:9]
        boolmap=sliced(p[0], p[1], p[2], planedef)

        if(np.sum(boolmap)==2): #two are on the positive side 
            intersection1= intersectionpoint(p[np.where(np.invert(boolmap))[0][0]], p[np.where(boolmap)[0][0]], planedef)
            intersection2= intersectionpoint(p[np.where(np.invert(boolmap))[0][0]], p[np.where(boolmap)[0][1]], planedef)
            newpface1= np.hstack((p[np.where(boolmap)[0][0]], np.hstack((intersection1, p[np.where(boolmap)[0][1]]))))
            newpface2= np.hstack((intersection2, np.hstack((intersection1, p[np.where(boolmap)[0][1]]))))
            newnface=  np.hstack((intersection2, np.hstack((intersection1, p[np.where(np.invert(boolmap))[0][0]]))))
                             
            positivef=np.vstack([positivef, newpface1]) 
            positivef=np.vstack([positivef, newpface2])
            negativef=np.vstack([negativef, newnface])

        else: #two are on the negative side 
            intersection1=intersectionpoint(p[np.where(np.invert(boolmap))[0][0]], p[np.where(boolmap)[0][0]], planedef)
            intersection2=intersectionpoint(p[np.where(np.invert(boolmap))[0][1]], p[np.where(boolmap)[0][0]], planedef)
            newnface1= np.hstack((p[np.where(np.invert(boolmap))[0][0]], np.hstack((intersection1, p[np.where(np.invert(boolmap))[0][1]]))))
            newnface2= np.hstack((intersection2, np.hstack((intersection1, p[np.where(np.invert(boolmap))[0][1]]))))
            newpface=  np.hstack((intersection2, np.hstack((intersection1, p[np.where(boolmap)[0][0]]))))
        
            positivef=np.vstack((positivef, newpface))
            negativef=np.vstack([negativef, newnface1])
            negativef=np.vstack([negativef, newnface2])

        planepts=np.vstack([planepts,intersection1])
        planepts=np.vstack([planepts,intersection2])

    if len(slicef)>0:
        planepts=planepts[1:]
        baseface=np.empty([1,9], dtype=float)
        midpoints=np.asarray([np.average(planepts[:,0]),np.average(planepts[:,1]), np.average(planepts[:,2])])
        for i3 in range(0, len(planepts)-1, 2):
            planef=np.hstack((midpoints, np.hstack ((planepts[i3], planepts[i3+1]))))
            baseface=np.vstack((baseface, planef))

        baseface=baseface[1:]
        positivef=np.vstack([positivef, baseface])
        negativef=np.vstack([negativef, baseface])
    else:
        pass

    posstl = mesh.Mesh(np.zeros(positivef.shape[0], dtype=mesh.Mesh.dtype))
    posstl.points=positivef
    posstl.save('pos.stl')


    negstl= mesh.Mesh(np.zeros(negativef.shape[0], dtype=mesh.Mesh.dtype))
    negstl.points=negativef
    negstl.save('negstl.stl')



    posstl=mesh.Mesh.from_file('pos.stl')
    negstl=mesh.Mesh.from_file('negstl.stl')
    volumep, cogp, inertiap = posstl.get_mass_properties()
    volumen, cogn, inertian = negstl.get_mass_properties()
    result=stlpair.stlpair()
    
    result.topstl=posstl
    result.bottomstl=negstl
    result.topcog=cogp
    result.bottomcog=cogn
    result.planedef=planedef
    

    return result
    
    #print("Centroid of positive side = {0}".format(cogp))
    #print("Centroid of negative side = {0}".format(cogn))

    



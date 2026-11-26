"""FoodClock: integer allocation with deadline and capacity constraints."""
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint

def allocate(batches, recipients, delay=0, buffer=15, optimized=True):
    edges=[]
    for i,b in enumerate(batches):
        for j,r in enumerate(recipients):
            # Fictional coordinate grid in kilometers; not live routing.
            distance=((b['x']-r['x'])**2+(b['y']-r['y'])**2)**0.5
            travel=int(np.ceil(distance*3))+10+delay
            slack=b['minutes']-travel-buffer
            if r['active'] and b['verified'] and b['storage']==r['storage'] and slack>=0:
                edges.append((i,j,travel,slack,distance))
    if not edges: return []
    supply=[b['meals'] for b in batches]; demand=[min(r['demand'],r['capacity']) for r in recipients]
    if optimized:
        A=np.zeros((len(supply)+len(demand),len(edges)))
        for k,(i,j,*_) in enumerate(edges): A[i,k]=1; A[len(supply)+j,k]=1
        bounds=LinearConstraint(A,0,supply+demand)
        result=milp(-np.ones(len(edges)),integrality=np.ones(len(edges)),bounds=Bounds(0,np.inf),constraints=bounds)
        if not result.success: raise RuntimeError('Allocation solver failed')
        # Preserve maximum meals, then favor urgent batches and shorter trips.
        total=round(sum(result.x))
        costs=np.array([t + min(batches[i]['minutes'],1440)/10 for i,j,t,s,d in edges])
        second=milp(costs,integrality=np.ones(len(edges)),bounds=Bounds(0,np.inf),constraints=[bounds,LinearConstraint(np.ones((1,len(edges))),total,total)])
        quantities=np.rint(second.x if second.success else result.x).astype(int)
    else:
        quantities=np.zeros(len(edges),dtype=int)
        for k in sorted(range(len(edges)),key=lambda k:(edges[k][0],edges[k][4])):
            i,j,*_=edges[k]; q=min(supply[i],demand[j]); quantities[k]=q; supply[i]-=q; demand[j]-=q
    return [dict(batch=batches[i]['name'],recipient=recipients[j]['name'],meals=int(q),travel_minutes=t,latest_start_in_minutes=s,storage=batches[i]['storage']) for (i,j,t,s,d),q in zip(edges,quantities) if q>0]

def explain(batches, recipients, plan, delay=0, buffer=15):
    """Explain unallocated supply without claiming food safety."""
    rows=[]
    for b in batches:
        left=b['meals']-sum(p['meals'] for p in plan if p['batch']==b['name'])
        if left<=0: continue
        compatible=[r for r in recipients if r['active'] and r['storage']==b['storage'] and min(r['demand'],r['capacity'])>0]
        feasible=[r for r in compatible if b['minutes']>=int(np.ceil(((b['x']-r['x'])**2+(b['y']-r['y'])**2)**.5*3))+10+delay+buffer]
        reason=('Handling unconfirmed' if not b['verified'] else 'Deadline elapsed' if b['minutes']<=0 else 'No available compatible recipient' if not compatible else 'No match within deadline' if not feasible else 'Recipient demand or capacity exhausted / competing donations')
        rows.append(dict(batch=b['name'],unallocated_meals=left,reason=reason))
    return rows

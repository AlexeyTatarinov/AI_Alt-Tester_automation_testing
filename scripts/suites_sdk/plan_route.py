# -*- coding: utf-8 -*-
"""Планирование маршрута Beach: от точки остановки бота к LocationExit по данным коллайдеров (Reports/evidence/logs/colliders_corridor_beach.json). Только расчёт, игру не трогает."""
import json, math, heapq, os, sys
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
c=json.load(open(os.path.join(ROOT,"Reports/evidence/logs/colliders_corridor_beach.json"),encoding="utf-8"))
start=(-87.9,-361.1); goal=(-62.83,-358.87)
margin=float(sys.argv[1]) if len(sys.argv)>1 else 0.05
caprad={"BeachPalm(Polybrush Clone)":0.28*1.13,"Palm2(Polybrush Clone)":0.72,"Palm(Polybrush Clone)":0.63}
obs=[]
for n,t,x,y,z in c:
    if n in("LocationExit",) or "Landmass" in n or n=="Seabed": continue
    if t=="BoxCollider": r=0.15+0.3+margin if "Bamboo" in n else 1.5
    elif t=="CapsuleCollider": r=caprad.get(n,0.7)+0.3+margin
    elif t=="SphereCollider": r=0.5
    else: r=1.2
    obs.append((x,z,r))
x0,x1,z0,z1=-100,-55,-380,-340; h=0.2
W=int((x1-x0)/h); H=int((z1-z0)/h)
bl=[[False]*H for _ in range(W)]
for ox,oz,r in obs:
    for i in range(max(0,int((ox-r-x0)/h)),min(W,int((ox+r-x0)/h)+1)):
        for j in range(max(0,int((oz-r-z0)/h)),min(H,int((oz+r-z0)/h)+1)):
            if math.hypot(x0+i*h-ox,z0+j*h-oz)<=r: bl[i][j]=True
cell=lambda p:(int((p[0]-x0)/h),int((p[1]-z0)/h))
s,g=cell(start),cell(goal)
bl[s[0]][s[1]]=False
pq=[(0,s)]; came={s:None}; cost={s:0}
while pq:
    _,u=heapq.heappop(pq)
    if u==g: break
    for di,dj in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
        v=(u[0]+di,u[1]+dj)
        if not(0<=v[0]<W and 0<=v[1]<H) or bl[v[0]][v[1]]: continue
        nc=cost[u]+math.hypot(di,dj)
        if v not in cost or nc<cost[v]:
            cost[v]=nc; came[v]=u; heapq.heappush(pq,(nc+math.hypot(g[0]-v[0],g[1]-v[1]),v))
if g not in came:
    best=min(came,key=lambda v:math.hypot(g[0]-v[0],g[1]-v[1]))
    print("маршрута нет (запас %.2f м). Ближайшая достижимая точка %s, до цели %.1f м, клеток %d"%(margin,(round(x0+best[0]*h,1),round(z0+best[1]*h,1)),math.hypot(g[0]-best[0],g[1]-best[1])*h,len(came)))
else:
    path=[];u=g
    while u: path.append((x0+u[0]*h,z0+u[1]*h)); u=came[u]
    path=path[::-1]
    L=sum(math.hypot(path[i+1][0]-path[i][0],path[i+1][1]-path[i][1]) for i in range(len(path)-1))
    D=math.hypot(goal[0]-start[0],goal[1]-start[1])
    lat=max(abs((goal[0]-start[0])*(start[1]-p[1])-(start[0]-p[0])*(goal[1]-start[1]))/D for p in path)
    # прореживание: точки, где курс меняется
    way=[path[0]]
    for p in path[1:]:
        if math.hypot(p[0]-way[-1][0],p[1]-way[-1][1])>=5: way.append(p)
    way.append(path[-1])
    print("маршрут найден: длина %.1f м (прямая %.1f), макс. боковое смещение %.1f м"%(L,D,lat)); print("вехи:",[(round(a,1),round(b,1)) for a,b in way])
    json.dump({"waypoints":way,"length_m":L,"straight_m":D,"max_lateral_m":lat,"margin_m":margin},open(os.path.join(ROOT,"Reports/evidence/logs/scene03_route_plan.json"),"w"))

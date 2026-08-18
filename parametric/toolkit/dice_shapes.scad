// Blank base shapes for the story-dice family. Rounded convex polyhedra.
mode="one"; shape="d6"; size=18; round_r=1.2; $fn=32;
phi=(1+sqrt(5))/2;
c10=0.1056;   // ring height for a TRUE pentagonal trapezohedron (apex = 9.4721*c)
function pts(s) =
  s=="d4"  ? [[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]] :
  s=="d6"  ? [for(x=[-1,1],y=[-1,1],z=[-1,1]) [x,y,z]] :
  s=="d8"  ? [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]] :
  s=="d10" ? concat([[0,0,1],[0,0,-1]],
               [for(i=[0:4]) [cos(72*i),      sin(72*i),       c10]],
               [for(i=[0:4]) [cos(72*i+36),   sin(72*i+36),   -c10]]) :
  s=="d12" ? concat([for(x=[-1,1],y=[-1,1],z=[-1,1]) [x,y,z]],
               [for(y=[-1,1],z=[-1,1]) [0, y/phi, z*phi]],
               [for(x=[-1,1],y=[-1,1]) [x/phi, y*phi, 0]],
               [for(x=[-1,1],z=[-1,1]) [x*phi, 0, z/phi]]) :
  s=="d20" ? concat([for(y=[-1,1],z=[-1,1]) [0, y, z*phi]],
               [for(x=[-1,1],y=[-1,1]) [x, y*phi, 0]],
               [for(x=[-1,1],z=[-1,1]) [x*phi, 0, z]]) : [];
module die(s, sz, rr){
  p = pts(s);
  mx = max([for(q=p) max(abs(q[0]),abs(q[1]),abs(q[2]))]);
  k  = (sz/2 - rr)/mx;
  hull() for(q=p) translate(q*k) sphere(r=rr);
}
NM=["d4","d6","d8","d10","d12","d20"]; SZ=[22,18,24,22,24,32];
if(mode=="family") for(i=[0:5]) translate([i*34-85,0,0]) die(NM[i], SZ[i], 1.2);
else die(shape, size, round_r);

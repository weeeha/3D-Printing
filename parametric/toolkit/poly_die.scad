// Polyhedral story die: one icon per face, any Platonic solid.
shape="d8"; size=34; rr=1.2; glyph=10; depth=0.6; $fn=40;
icons=["","","","","","","",""];
phi=(1+sqrt(5))/2;
function pts(s) =
  s=="d4"  ? [[1,1,1],[1,-1,-1],[-1,1,-1],[-1,-1,1]] :
  s=="d6"  ? [for(x=[-1,1],y=[-1,1],z=[-1,1]) [x,y,z]] :
  s=="d8"  ? [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]] :
  s=="d12" ? concat([for(x=[-1,1],y=[-1,1],z=[-1,1]) [x,y,z]],
               [for(y=[-1,1],z=[-1,1]) [0,y/phi,z*phi]],
               [for(x=[-1,1],y=[-1,1]) [x/phi,y*phi,0]],
               [for(x=[-1,1],z=[-1,1]) [x*phi,0,z/phi]]) :
  s=="d20" ? concat([for(y=[-1,1],z=[-1,1]) [0,y,z*phi]],
               [for(x=[-1,1],y=[-1,1]) [x,y*phi,0]],
               [for(x=[-1,1],z=[-1,1]) [x*phi,0,z]]) : [];
// face normals = the DUAL solid's vertex directions
function nrm(s) =
  s=="d4"  ? [for(p=pts("d4"))  -p/norm(p)] :
  s=="d6"  ? [for(p=pts("d8"))   p/norm(p)] :
  s=="d8"  ? [for(p=pts("d6"))   p/norm(p)] :
  s=="d12" ? [for(p=pts("d20"))  p/norm(p)] :
  s=="d20" ? [for(p=pts("d12"))  p/norm(p)] : [];
K   = (size/2 - rr) / max([for(q=pts(shape)) norm(q)]);
module body(){ hull() for(q=pts(shape)) translate(q*K) sphere(r=rr); }
module cut(i){
  n = nrm(shape)[i];
  d = max([for(q=pts(shape)) (q*K)*n]) + rr;      // supporting plane distance
  u0 = abs(n[2])>0.9 ? [0,1,0] : [0,0,1];
  u  = (u0 - n*(u0*n)) / norm(u0 - n*(u0*n));     // up, projected into face
  r  = cross(u,n);
  multmatrix([[r[0],u[0],n[0], n[0]*d],
              [r[1],u[1],n[1], n[1]*d],
              [r[2],u[2],n[2], n[2]*d],
              [0,0,0,1]])
    translate([0,0,-depth]) linear_extrude(height=depth+0.5)
      resize([glyph,glyph,0],auto=true) import(icons[i],center=true);
}
difference(){ body(); union(){ for(i=[0:len(nrm(shape))-1]) if(icons[i]!="") cut(i); } }

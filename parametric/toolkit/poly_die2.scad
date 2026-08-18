// Polyhedral story die with icon + label per face. Faces oriented apex-up.
shape="d8"; size=42; rr=1.4; glyph=10; tsize=4.2; icon_y=3.5; text_y=-5.2; depth=0.6; $fn=40;
icons=[]; labels=[];
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
function nrm(s) =
  s=="d4"  ? [for(p=pts("d4"))  -p/norm(p)] : s=="d6" ? [for(p=pts("d8")) p/norm(p)] :
  s=="d8"  ? [for(p=pts("d6"))   p/norm(p)] : s=="d12"? [for(p=pts("d20")) p/norm(p)] :
  s=="d20" ? [for(p=pts("d12"))  p/norm(p)] : [];
function vsum(v,i=0) = i>=len(v) ? [0,0,0] : v[i]+vsum(v,i+1);
K = (size/2 - rr) / max([for(q=pts(shape)) norm(q)]);
module body(){ hull() for(q=pts(shape)) translate(q*K) sphere(r=rr); }
module cut(i){
  n  = nrm(shape)[i];
  DM = max([for(q=pts(shape)) (q*K)*n]);
  FV = [for(q=pts(shape)) if (((q*K)*n) > DM-0.01) q*K];   // this face's vertices
  C  = vsum(FV)/len(FV);
  u  = (FV[0]-C)/norm(FV[0]-C);                            // up = toward a vertex (apex-up)
  r  = cross(u,n);
  d  = DM + rr;
  multmatrix([[r[0],u[0],n[0], n[0]*d],[r[1],u[1],n[1], n[1]*d],
              [r[2],u[2],n[2], n[2]*d],[0,0,0,1]])
    translate([0,0,-depth]) linear_extrude(height=depth+2){
      translate([0,icon_y,0]) resize([glyph,glyph,0],auto=true) import(icons[i],center=true);
      if(labels[i]!="") translate([0,text_y,0])
        text(labels[i],size=tsize,font="Helvetica:style=Bold",halign="center",valign="center");
    }
}
difference(){ body(); for(i=[0:len(nrm(shape))-1]) cut(i); }

size=18; chamf=1.6; glyph=10; depth=0.6; $fn=48;
icons=["","","","","",""];
module rdie(){ minkowski(){ cube(size-2*chamf,center=true); sphere(r=chamf);} }
module fc(f){ translate([0,0,size/2-depth]) linear_extrude(height=depth+2) resize([glyph,glyph,0],auto=true) import(f,center=true); }
difference(){
  rdie();
  if(icons[0]!="")                              fc(icons[0]);
  if(icons[1]!="") rotate([180,0,0])            fc(icons[1]);
  if(icons[2]!="") rotate([0,90,0]) rotate([0,0,90])  fc(icons[2]);
  if(icons[3]!="") rotate([0,-90,0]) rotate([0,0,-90]) fc(icons[3]);
  if(icons[4]!="") rotate([-90,0,0]) rotate([0,0,180]) fc(icons[4]);
  if(icons[5]!="") rotate([90,0,0])             fc(icons[5]);
}

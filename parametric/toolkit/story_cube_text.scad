size=28; chamf=2.2; glyph=12; tsize=4.4; gap=2.2; depth=0.6; $fn=48;
icons=["","","","","",""]; labels=["","","","","",""];
stack  = glyph + gap + tsize;
icon_y = stack/2 - glyph/2;
text_y = stack/2 - glyph - gap;
module rdie(){ minkowski(){ cube(size-2*chamf,center=true); sphere(r=chamf);} }
module fc(f,lab){
  translate([0,0,size/2-depth]) linear_extrude(height=depth+2){
    translate([0,icon_y,0]) resize([glyph,glyph,0],auto=true) import(f,center=true);
    if(lab!="") translate([0,text_y,0]) text(lab,size=tsize,font="Helvetica:style=Bold",halign="center",valign="top");
  }
}
difference(){
  rdie();
  if(icons[0]!="")                                     fc(icons[0],labels[0]);
  if(icons[1]!="") rotate([180,0,0])                   fc(icons[1],labels[1]);
  if(icons[2]!="") rotate([0,90,0]) rotate([0,0,90])   fc(icons[2],labels[2]);
  if(icons[3]!="") rotate([0,-90,0]) rotate([0,0,-90]) fc(icons[3],labels[3]);
  if(icons[4]!="") rotate([-90,0,0]) rotate([0,0,180]) fc(icons[4],labels[4]);
  if(icons[5]!="") rotate([90,0,0])                    fc(icons[5],labels[5]);
}

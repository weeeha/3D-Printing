rr=1.0; glyph=8.00; tsize=3.36; depth=0.6; $fn=32;
iy=2.280; ty=-4.600; K=8.000000;
V=[[-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1], [1, -1, -1], [1, -1, 1], [1, 1, -1], [1, 1, 1]];
F=[[-1.0, 0.0, 0.0, 0.0, 0.707107, -0.707107, 1.0], [-0.0, -1.0, -0.0, -0.707107, 0.0, 0.707107, 1.0], [0.0, 0.0, -1.0, 0.707107, -0.707107, 0.0, 1.0], [-0.0, -0.0, 1.0, -0.707107, 0.707107, 0.0, 1.0], [0.0, 1.0, 0.0, 0.707107, 0.0, -0.707107, 1.0], [1.0, -0.0, -0.0, 0.0, -0.707107, 0.707107, 1.0]];
icons=["/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/sun-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/cloud-rain-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/smiley-meh-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/question-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/infinity-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/dots-three-fill.svg"];
labels=["HAPPY", "TRAGIC", "BITTER", "UNKNOWN", "CIRCLE", "CLIFF"];
module body(){ hull() for(q=V) translate(q*K) sphere(r=rr); }
module cut(i){
  n=[F[i][0],F[i][1],F[i][2]]; u=[F[i][3],F[i][4],F[i][5]]; d=F[i][6]*K+rr;
  r=cross(u,n);
  multmatrix([[r[0],u[0],n[0],n[0]*d],[r[1],u[1],n[1],n[1]*d],[r[2],u[2],n[2],n[2]*d],[0,0,0,1]])
    translate([0,0,-depth]) linear_extrude(height=depth+0.6){
      translate([0,iy,0]) resize([glyph,glyph,0],auto=true) import(icons[i],center=true);
      if(labels[i]!="") translate([0,ty,0]) text(labels[i],size=tsize,font="Helvetica:style=Bold",halign="center",valign="center");
    }
}
difference(){ body(); union(){ for(i=[0:len(F)-1]) cut(i); } }

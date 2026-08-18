rr=1.0; glyph=8.00; tsize=3.36; depth=0.6; $fn=32;
iy=2.280; ty=-4.600; K=19.595932;
V=[[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1]];
F=[[0.57735, 0.57735, 0.57735, -0.408248, -0.408248, 0.816497, 0.57735], [0.57735, 0.57735, -0.57735, -0.408248, 0.816497, 0.408248, 0.57735], [0.57735, -0.57735, 0.57735, -0.408248, -0.816497, -0.408248, 0.57735], [0.57735, -0.57735, -0.57735, -0.408248, 0.408248, -0.816497, 0.57735], [-0.57735, 0.57735, 0.57735, 0.408248, 0.816497, -0.408248, 0.57735], [-0.57735, 0.57735, -0.57735, 0.408248, -0.408248, -0.816497, 0.57735], [-0.57735, -0.57735, 0.57735, 0.408248, 0.408248, 0.816497, 0.57735], [-0.57735, -0.57735, -0.57735, 0.408248, -0.816497, 0.408248, 0.57735]];
icons=["/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/buildings-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/church-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/mountains-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/road-horizon-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/house-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/bank-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/tent-fill.svg", "/private/tmp/claude-502/-Users-nickv-ClaudeCode-Projects-CreativeToolkit-Physical/24a8fd0e-39dc-4e6a-b5b0-d86131477d14/scratchpad/icons/planet-fill.svg"];
labels=["CITY", "TOWN", "WILD", "ROAD", "HOME", "CIVIC", "CAMP", "VOID"];
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

import FreeCAD as App, os, MeshPart
for n in ("csign_airgap","csign_clankers","csign_bilingual"):
    doc = App.openDocument(os.path.join(os.getcwd(), n+".FCStd"))
    print("==", n)
    for o in doc.Objects:
        if o.TypeId != "Part::Feature":
            continue
        sh = o.Shape
        m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.06,
                                   AngularDeflection=0.5, Relative=False)
        print("   %-14s valid=%-5s solids=%-3d faces=%-5d meshSolid=%-5s nonManifold=%-5s selfInt=%s"
              % (o.Name, sh.isValid(), len(sh.Solids), len(sh.Faces),
                 m.isSolid(), m.hasNonManifolds(), m.hasSelfIntersections()))
    App.closeDocument(doc.Name)

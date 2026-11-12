import math
NAVY="#10233F"; GOLD="#C98B2B"; ORANGE="#F26B1D"; CREAM="#FFF6E6"; WHITE="#FFFFFF"

def play(cx, cy, s, fill):
    # equilateral-ish play triangle centred optically
    h = s; w = s*0.9
    x0 = cx - w*0.42; 
    return f'<path d="M{x0:.1f},{cy-h/2:.1f} L{x0+w:.1f},{cy:.1f} L{x0:.1f},{cy+h/2:.1f} Z" fill="{fill}" stroke="{fill}" stroke-width="{s*0.08:.1f}" stroke-linejoin="round"/>'

def icon_A(cx=600, cy=600, R=480):
    k=R/480
    s=[]
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{NAVY}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{R-18*k}" fill="none" stroke="{GOLD}" stroke-width="{20*k}"/>')
    for i in range(36):
        a=2*math.pi*i/36
        s.append(f'<circle cx="{cx+430*k*math.cos(a):.1f}" cy="{cy+430*k*math.sin(a):.1f}" r="{9*k:.1f}" fill="{GOLD}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{395*k}" fill="none" stroke="{GOLD}" stroke-width="{6*k}"/>')
    for i in range(56):
        a=2*math.pi*i/56
        x1,y1=cx+340*k*math.cos(a),cy+340*k*math.sin(a); x2,y2=cx+380*k*math.cos(a+0.05),cy+380*k*math.sin(a+0.05)
        s.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{GOLD}" stroke-width="{6*k}" stroke-linecap="round"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{325*k}" fill="none" stroke="{GOLD}" stroke-width="{6*k}"/>')
    # 14-ray sun star
    n=14; pts=[]
    for i in range(2*n):
        a=-math.pi/2+math.pi*i/n
        r=(290 if i%2==0 else 150)*k
        pts.append(f"{cx+r*math.cos(a):.1f},{cy+r*math.sin(a):.1f}")
    s.append(f'<polygon points="{" ".join(pts)}" fill="{GOLD}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="{135*k}" fill="{ORANGE}"/>')
    s.append(play(cx+8*k, cy, 130*k, WHITE))
    return "\n".join(s)

def icon_B(cx=600, cy=600, R=480):
    k=R/480; s=[]
    s.append(f'<rect x="{cx-R}" y="{cy-R}" width="{2*R}" height="{2*R}" rx="{200*k}" fill="{CREAM}"/>')
    # pages
    sp_top=(cx, cy-150*k); sp_bot=(cx, cy+250*k)
    L=f'M{cx},{cy-150*k} C{cx-90*k},{cy-230*k} {cx-250*k},{cy-240*k} {cx-360*k},{cy-200*k} L{cx-360*k},{cy+200*k} C{cx-250*k},{cy+160*k} {cx-90*k},{cy+170*k} {cx},{cy+250*k} Z'
    Rp=f'M{cx},{cy-150*k} C{cx+90*k},{cy-230*k} {cx+250*k},{cy-240*k} {cx+360*k},{cy-200*k} L{cx+360*k},{cy+200*k} C{cx+250*k},{cy+160*k} {cx+90*k},{cy+170*k} {cx},{cy+250*k} Z'
    s.append(f'<path d="{L}" fill="{NAVY}"/>')
    s.append(f'<path d="{Rp}" fill="{ORANGE}"/>')
    # film perforations on outer edges
    for j in range(6):
        y=cy-165*k+j*68*k
        s.append(f'<rect x="{cx-340*k}" y="{y:.1f}" width="{26*k}" height="{36*k}" rx="{6*k}" fill="{CREAM}"/>')
        s.append(f'<rect x="{cx+314*k}" y="{y:.1f}" width="{26*k}" height="{36*k}" rx="{6*k}" fill="{CREAM}"/>')
    # text lines on left page
    for j in range(4):
        y=cy-110*k+j*70*k
        s.append(f'<path d="M{cx-280*k},{y+10*k:.1f} C{cx-200*k},{y-20*k:.1f} {cx-110*k},{y-20*k:.1f} {cx-50*k},{y+10*k:.1f}" fill="none" stroke="{GOLD}" stroke-width="{14*k}" stroke-linecap="round"/>')
    # play on right page
    s.append(play(cx+185*k, cy+10*k, 190*k, CREAM))
    # spine glow / bookmark gold
    s.append(f'<path d="M{cx},{cy-150*k} L{cx},{cy+250*k}" stroke="{GOLD}" stroke-width="{12*k}"/>')
    return "\n".join(s)

def icon_C(cx=600, cy=600, R=480):
    k=R/480; s=[]
    s.append(f'<rect x="{cx-R}" y="{cy-R}" width="{2*R}" height="{2*R}" rx="{200*k}" fill="{NAVY}"/>')
    # scroll sheet
    x0,x1=cx-300*k,cx+300*k; y0,y1=cy-190*k,cy+190*k
    s.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{CREAM}"/>')
    # rolled ends
    for xe in (x0, x1):
        s.append(f'<rect x="{xe-45*k}" y="{y0-40*k}" width="{90*k}" height="{(y1-y0)+80*k}" rx="{45*k}" fill="{GOLD}"/>')
        s.append(f'<rect x="{xe-20*k}" y="{y0-70*k}" width="{40*k}" height="{(y1-y0)+140*k}" rx="{20*k}" fill="{ORANGE}"/>')
    # timeline across scroll
    s.append(f'<line x1="{x0+70*k}" y1="{cy+120*k}" x2="{x1-70*k}" y2="{cy+120*k}" stroke="{NAVY}" stroke-width="{10*k}" stroke-linecap="round"/>')
    for t in (0.15,0.5,0.85):
        xx=x0+70*k+(x1-x0-140*k)*t
        s.append(f'<circle cx="{xx:.1f}" cy="{cy+120*k:.1f}" r="{18*k}" fill="{ORANGE if t==0.5 else NAVY}"/>')
    s.append(f'<circle cx="{cx}" cy="{cy-30*k}" r="{105*k}" fill="{ORANGE}"/>')
    s.append(play(cx+6*k, cy-30*k, 100*k, CREAM))
    return "\n".join(s)

def svg(w,h,body,bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{b}{body}</svg>'

def lockup(icon_fn, dark=False):
    ink = CREAM if dark else NAVY
    body = icon_fn(330, 330, 270)
    body += f'<text x="660" y="330" font-family="Be Vietnam Pro" font-weight="900" font-size="150" fill="{ink}">Edu<tspan fill="{ORANGE}">History</tspan></text>'
    body += f'<text x="668" y="455" font-family="Be Vietnam Pro" font-weight="600" font-size="62" letter-spacing="34" fill="{GOLD}">STUDIO</text>'
    return svg(1620, 660, body, NAVY if dark else WHITE)

for name, fn in (("A_trong_dong", icon_A), ("B_sach_phim", icon_B), ("C_cuon_thu", icon_C)):
    open(f"{name}_icon.svg","w").write(svg(1200,1200,fn()))
    open(f"{name}_lockup.svg","w").write(lockup(fn))
    open(f"{name}_lockup_dark.svg","w").write(lockup(fn, True))
print("ok")

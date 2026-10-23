"""The spooky island: the pieces of the three concept drawings this project began from, drawn with the pixel-art
toolkit (scripts/pixelart.py) - a brick vault's arch to frame a tunnel, a broken casement to see a garden through,
a tattered curtain to hang beside it, rose bushes, a robed statue on its pedestal, a round wall lamp, a riveted iron
cabinet, a punt seen from its stern and a bank of storm cloud for a sky at landscape scale; and to lay on a floor or
a wall, broken glass and a painted sigil.
"""
import numpy as np

from biomes import _prop
from pixelart import Canvas, ramp, smooth_noise

VAULT = ramp('#4a4450', dark=0.35, light=1.45, cool=0.12)            # dark grey-violet brick
PLASTER = ramp('#3e4044', dark=0.4, light=1.4, cool=0.1)
WOOD = ramp('#3a2a20', dark=0.45, light=1.6)
GLASS = np.array([0.62, 0.64, 0.66], np.float32)
LEAF = ramp('#2e4a2a', dark=0.35, light=1.45)
ROSE = ramp('#a8202a', dark=0.4, light=1.4, warm=0.1)
STONE = ramp('#8a8680', dark=0.35, light=1.35)
IRON = ramp('#585c64', dark=0.35, light=1.5, cool=0.12)
SOOT = ramp('#2a2624', dark=0.5, light=1.8)
VELVET = ramp('#5e2430', dark=0.35, light=1.6)                     # a curtain's velvet, faded
CLOUD = ramp(['#0e1218', '#151a22', '#1d232e', '#262e3c', '#313b4c', '#3e495c'])  # storm cloud, foot to top
EMBER = ramp(['#6a3010', '#a8501a', '#d87a26', '#f09a38', '#ffb850', '#ffd890'])  # a lamp's glass, warm


def spr_vault_arch():
    """A brick vault's arch, end on, for a tunnel: a card as wide as the tunnel (3) and as tall as its roof (1.6),
    the brickwork filling its upper corners down to a round arch - a ring of voussoirs along its edge, the bricks
    in courses beyond - open inside the arch and below where it springs from the walls. Set one across a tunnel
    every 1.3 or so, turned with `angle` to face along it, and they frame each other into a vault."""
    w, h = 192, 102
    rng = np.random.default_rng(31)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx, spring = w / 2, h * 0.56                                   # the arch springs from the walls here
    a, b = w / 2 - 2, spring - 4                                   # its half-span; its rise, the crown 4 px down
    r = np.hypot((xx - cx) / a, (yy - spring) / b)                # 1 along the arch
    brick = (r >= 1) & (yy < spring)
    ring = brick & (r < 1 + 11 / b)                                # the voussoirs
    th = np.arctan2((yy - spring) / b, (xx - cx) / a)              # their joints run out from the middle
    v = np.full((h, w), 0.5, np.float32)
    course = (yy // 6).astype(int)                                 # bricks in courses beyond the ring
    joint = ((yy % 6) < 1) | (((xx + (course % 2) * 7) % 14) < 1)
    tone = rng.random(400)[(course * 13 + ((xx + (course % 2) * 7) // 14).astype(int)) % 400]
    v = v + 0.16 * (tone - 0.5) + 0.06 * (smooth_noise(w, h, 12, rng, wrap=False) - 0.5)
    v = np.where(joint & ~ring, 0.18, v)
    seg = (th * 30 / np.pi) % 1.0                                  # a voussoir every 6 degrees
    vtone = rng.random(64)[((th + np.pi) * 30 / np.pi).astype(int) % 64]
    v = np.where(ring, 0.56 + 0.14 * (vtone - 0.5) + 0.12 * (1 - (r - 1) * b / 11), v)
    v = np.where(ring & ((seg < 0.08) | (np.abs(r - 1 - 11 / b) < 1.2 / b)), 0.2, v)
    v = np.where(brick & (r < 1 + 1.6 / b), 0.12, v)               # the arch's edge, in its own shadow
    v = v - 0.18 * (1 - yy / spring) * brick                       # darker toward the crown, away from the lamps
    rgba = np.zeros((h, w, 4), np.float32)
    pal = np.asarray(VAULT, np.float32)
    idx = np.clip(np.round(np.clip(v, 0, 1) * (len(pal) - 1)), 0, len(pal) - 1).astype(int)
    rgba[..., :3] = pal[idx]
    rgba[..., 3] = brick.astype(np.float32)
    return rgba, np.zeros((h, w), np.float32)


def spr_broken_casement():
    """A broken casement in a stretch of wall, seen from inside: a card 2 wide and 1 tall - plaster round a window
    of dark wood whose cross of glazing bars is snapped in the middle, the glass gone but for a shard in each
    corner and a sliver at the break, a sill under it. Stand it in the gap of a room's wall, turned with `angle`
    to face into the room, and the night outside shows through."""
    w, h = 192, 96
    rng = np.random.default_rng(17)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    x0, x1, y0, y1 = 34, 158, 6, 80                                # the window's opening
    v = 0.42 + 0.1 * smooth_noise(w, h, 10, rng, wrap=False) + 0.04 * (rng.random((h, w)) - 0.5)
    rgba = np.zeros((h, w, 4), np.float32)
    pal = np.asarray(PLASTER, np.float32)
    rgba[..., :3] = pal[np.clip(np.round(v * 5), 0, 5).astype(int)]
    rgba[..., 3] = 1.0
    opening = (xx >= x0) & (xx < x1) & (yy >= y0) & (yy < y1)
    rgba[opening, 3] = 0.0
    wood = np.asarray(WOOD, np.float32)

    def paint(mask, shade):
        rgba[mask, :3] = wood[shade]
        rgba[mask, 3] = 1.0
    frame = opening & ((xx < x0 + 4) | (xx >= x1 - 4) | (yy < y0 + 4) | (yy >= y1 - 3))
    paint(frame, 2)
    paint(opening & (xx >= x1 - 4) | opening & (yy >= y1 - 3), 1)                 # the frame's shaded sides
    mx = (x0 + x1) // 2
    bar = (xx >= mx - 3) & (xx < mx + 3) & opening
    snap = (yy >= 28 + 3 * np.sin(xx * 1.7)) & (yy < 52 + 2 * np.cos(xx * 2.3))   # snapped, ragged
    paint(bar & ~snap, 2)
    ty = 41
    tbar = (yy >= ty) & (yy < ty + 4) & opening & ((xx < mx - 24 + 4 * np.sin(yy)) | (xx >= mx + 30))
    paint(tbar, 2)
    # what is left of the glass: a shard in each corner of the window, a sliver or two at the break - clear but for
    # the glints across it and along its broken edge
    corners = [(x0 + 4, y0 + 4, 1, 1), (x1 - 4, y0 + 4, -1, 1), (x0 + 4, y1 - 3, 1, -1), (x1 - 4, y1 - 3, -1, -1),
               (mx - 3, ty, -1, -1), (mx + 3, ty + 4, 1, 1)]
    for k, (cx, cy, sx, sy) in enumerate(corners):
        lx, ly = (rng.uniform(26, 36), rng.uniform(16, 24)) if k < 4 else (rng.uniform(7, 11), rng.uniform(5, 8))
        u, v = (xx - cx) * sx / lx, (yy - cy) * sy / ly
        edge = 1 + 0.1 * np.sin(xx * 0.31 + yy * 0.47 + 2 * k)                     # the broken edge, ragged
        tri = (u >= 0) & (v >= 0) & (u + v < edge) & opening & ~frame & ~(bar & ~snap) & ~tbar
        rim = tri & (u + v >= edge - 0.09)
        see = tri & ~rim & (((xx - yy) % 9 == 0) | ((xx - yy) % 9 == 1) & ((xx + 2 * yy) % 5 == 0))
        rgba[see, :3] = GLASS * 0.9
        rgba[see, 3] = 1.0
        rgba[rim, :3] = np.clip(GLASS * 1.25, 0, 1)
        rgba[rim, 3] = 1.0
    sill = (yy >= y1) & (yy < y1 + 5) & (xx >= x0 - 6) & (xx < x1 + 6)
    rgba[sill, :3] = wood[3]
    rgba[(yy >= y1 + 3) & (yy < y1 + 5) & (xx >= x0 - 6) & (xx < x1 + 6), :3] = wood[1]
    return np.clip(rgba, 0, 1), np.zeros((h, w), np.float32)


def dec_glass_shards():
    """Broken glass on a floor: jagged shards of a window, pale and catching the light - a glint at each one's
    sharpest corner - and a few small ones."""
    w, h = 56, 28
    rng = np.random.default_rng(23)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rgba = np.zeros((h, w, 4), np.float32)
    em = np.zeros((h, w), np.float32)
    for _ in range(9):
        cx, cy, s = rng.uniform(6, w - 6), rng.uniform(5, h - 5), rng.uniform(2, 7)
        a = rng.uniform(0, np.pi, 3)
        pts = [(cx + s * np.cos(t) * rng.uniform(0.6, 1.3), cy + s * np.sin(t) * 0.6)
               for t in (a[0], a[0] + 2.2, a[0] + 4.1)]
        (ax, ay), (bx, by), (qx, qy) = pts
        d = (by - qy) * (ax - qx) + (qx - bx) * (ay - qy)
        if abs(d) < 1e-3:
            continue
        l1 = ((by - qy) * (xx - qx) + (qx - bx) * (yy - qy)) / d
        l2 = ((qy - ay) * (xx - qx) + (ax - qx) * (yy - qy)) / d
        inside = (l1 >= 0) & (l2 >= 0) & (l1 + l2 <= 1)
        rgba[inside, :3] = GLASS * (0.8 + 0.5 * l1[inside, None])
        rgba[inside, 3] = 0.78
        glint = inside & (l1 > 0.78)
        rgba[glint, :3] = 0.95
        em[glint] = 0.5
    return np.clip(rgba, 0, 1), em


def dec_sigil():
    """A sigil painted on a wall in red: a circle, a triangle in it standing on its base, a line down through both,
    the paint run in drips below."""
    w, h = 44, 52
    rng = np.random.default_rng(29)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx, cy, R = w / 2, 22, 17
    d = np.hypot(xx - cx, yy - cy)
    paint = np.abs(d - R) < 1.6                                    # the circle
    top, lx, rx, base = cy - R + 1, cx - R * 0.84, cx + R * 0.84, cy + R * 0.5
    for (x0_, y0_), (x1_, y1_) in (((cx, top), (lx, base)), ((cx, top), (rx, base)), ((lx, base), (rx, base))):
        t = np.clip(((xx - x0_) * (x1_ - x0_) + (yy - y0_) * (y1_ - y0_)) / ((x1_ - x0_) ** 2 + (y1_ - y0_) ** 2), 0, 1)
        paint |= np.hypot(xx - (x0_ + t * (x1_ - x0_)), yy - (y0_ + t * (y1_ - y0_))) < 1.3
    paint |= (np.abs(xx - cx) < 1.3) & (yy > cy - R - 2) & (yy < cy + R + 3)          # the line down through
    for _ in range(7):                                             # drips
        x = int(rng.uniform(cx - R, cx + R))
        y = int(np.nonzero(paint[:, x])[0].max()) if paint[:, x].any() else int(cy)
        paint[y:y + int(rng.uniform(3, 12)), x] = True
    rgba = np.zeros((h, w, 4), np.float32)
    shade = 0.8 + 0.3 * smooth_noise(w, h, 6, rng, wrap=False)
    rgba[paint, :3] = np.array([0.74, 0.1, 0.08], np.float32) * shade[paint, None]
    rgba[paint, 3] = 0.9
    return np.clip(rgba, 0, 1), np.zeros((h, w), np.float32)


def spr_rose_bush():
    """A rose bush: a rounded mound of dark leaves, red roses open all over it."""
    w, h = 40, 26
    rng = np.random.default_rng(41)
    cv = Canvas(w, h, wrap=False, ground=-9)
    for _ in range(26):
        x, y = rng.uniform(6, w - 6), rng.uniform(8, h - 3)
        cv.ellipse(x, y, rng.uniform(3, 6), rng.uniform(2.5, 4.5), z=0.5 + (h - y) * 0.03, dome=0.8, rough=0.3,
                   rng=rng, mat=0, tone=float(rng.uniform(-0.08, 0.06)))
    for _ in range(14):
        x, y = rng.uniform(5, w - 5), rng.uniform(6, h - 6)
        if cv.id[int(y), int(x)] == 0:
            continue
        r = rng.uniform(1.2, 2.0)
        cv.ellipse(x, y, r, r * 0.9, z=float(cv.z[int(y), int(x)]) + 0.3, dome=0.6, mat=1,
                   tone=float(rng.uniform(-0.05, 0.08)))
        cv.ellipse(x - 0.3, y - 0.3, r * 0.4, r * 0.35, z=float(cv.z[int(y), int(x)]) + 0.5, dome=0.2, mat=1,
                   tone=-0.25)
    return _prop(cv, [LEAF, ROSE], relief=1.0, cavity=0.45, shadow=0.45)


def spr_tattered_curtain():
    """A tattered curtain, hung beside a window: heavy velvet gone a dusty red, falling in folds from rings on an
    iron rod, its hem rotted ragged, a long tear in it and moth holes here and there. A card (`planes` 1) a
    little wider than a quarter of its height; hang one each side of a window, just in front of the wall."""
    w, h = 30, 110
    rng = np.random.default_rng(37)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rgba = np.zeros((h, w, 4), np.float32)
    pal = np.asarray(VELVET, np.float32)
    phase = rng.uniform(0, 6.3)
    fold = np.sin(xx * 2 * np.pi / 7.5 + phase + 0.02 * yy)                  # the folds, drifting as they fall
    v = 0.45 + 0.32 * fold + 0.06 * smooth_noise(w, h, 8, rng, wrap=False) - 0.12 * (yy / h)
    cloth = yy >= 4
    hem = h - 2 - (rng.uniform(0, 1, w) ** 2) * 18                           # rotted ragged, a few long strands
    cloth &= yy < hem[None, :].repeat(h, 0)
    tear = (np.abs(xx - 19 - 0.06 * (yy - 58)) < 0.9 + 0.5 * np.sin(yy * 0.4)) & (yy > 52) & (yy < 84)
    cloth &= ~tear
    for _ in range(5):                                                       # moth holes
        cx, cy, r = rng.uniform(4, w - 4), rng.uniform(16, h - 22), rng.uniform(0.7, 1.6)
        cloth &= np.hypot(xx - cx, (yy - cy) * 0.8) > r
    rgba[cloth, :3] = pal[np.clip(np.round(v * 5), 0, 5).astype(int)][cloth]
    rgba[cloth, 3] = 1.0
    edge = cloth & ~np.roll(cloth, 1, 0)                                     # the cloth's top edge under the rings
    rod = (yy >= 1) & (yy < 3)
    rgba[rod, :3] = np.asarray(SOOT, np.float32)[2]
    rgba[rod, 3] = 1.0
    for x in range(3, w - 2, 6):                                             # the rings
        ring = (np.abs(xx - x) <= 1) & (yy >= 1) & (yy <= 5)
        rgba[ring, :3] = np.asarray(SOOT, np.float32)[4]
        rgba[ring, 3] = 1.0
    rgba[edge, :3] *= 0.7
    return np.clip(rgba, 0, 1), np.zeros((h, w), np.float32)


def spr_storm_cloud():
    """A bank of storm cloud for a sky at landscape scale: heavy puffs piled along a flat dark underside, their tops
    pale with what light there is. Drawn in its own colours (`fullbright`), as the sky is - set a few far off and
    high, overlapping, to bring a storm in over a skyline."""
    w, h = 160, 48
    rng = np.random.default_rng(43)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    base = h * 0.8                                                 # the underside
    puffs = []
    for _ in range(30):
        cx = rng.uniform(8, w - 8)
        end = min(cx, w - cx) / (w / 2)                            # smaller toward the ends
        rx = rng.uniform(10, 24) * (0.45 + 0.55 * end)
        ry = rx * rng.uniform(0.32, 0.48)
        puffs.append((cx, base - ry * rng.uniform(0.25, 0.8) - 6 * end * rng.uniform(0, 1), rx, ry))
    v = np.zeros((h, w), np.float32)
    inside = np.zeros((h, w), bool)
    for cx, cy, rx, ry in sorted(puffs, key=lambda p: p[1]):      # the high ones first, the low ones in front
        d = ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2
        puff = d < 1
        up = np.clip((cy - yy) / ry, -1, 1)                        # 1 at its top, -1 at its foot
        v[puff] = (0.45 + 0.4 * up - 0.25 * d ** 3)[puff]          # its top catching the light, its rim in shade
        inside |= puff
    inside &= yy < base + 1.5 * np.sin(xx * 0.13) + 1.0 * np.sin(xx * 0.41)
    v -= 0.35 * np.clip((yy - base * 0.7) / (base * 0.3), 0, 1)     # darkening down to the underside
    v += 0.08 * smooth_noise(w, h, 7, rng, wrap=False)
    rgba = np.zeros((h, w, 4), np.float32)
    pal = np.asarray(CLOUD, np.float32)
    rgba[inside, :3] = pal[np.clip(np.round(v * 5), 0, 5).astype(int)][inside]
    rgba[inside, 3] = 1.0
    return rgba, np.zeros((h, w), np.float32)


def spr_robed_statue():
    """A robed statue on its pedestal: a hooded figure in a long robe falling in folds, its hands folded at its
    breast, its face in the hood's shadow - weathered grey stone - on a square plinth."""
    w, h = 30, 88
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(4, 62, 22, 26, z=0.5, top=0.6, bevel=1.4, mat=0, tone=-0.06)                  # the pedestal
    cv.box(2, 58, 26, 5, z=0.7, top=0.4, bevel=1.0, mat=0, tone=0.04)                   # its cornice
    cv.box(3, 84, 24, 4, z=0.7, top=0.4, bevel=1.0, mat=0)                              # its base
    cv.polygon([(9, 20), (21, 20), (25, 58), (5, 58)], z=0.8, top=1.0, bevel=3.0, mat=0)   # the robe
    for x in (9.5, 13, 17, 20.5):                                  # its folds
        cv.stroke([(15 + (x - 15) * 0.5, 28), (x, 57)], 1.2, dome=0.5, mode='carve')
    cv.polygon([(8.5, 23), (10, 12), (15, 5.5), (20, 12), (21.5, 23)], z=1.2, top=1.0, bevel=2.6, mat=0)   # the cowl
    cv.ellipse(15, 16.5, 2.7, 3.8, z=1.4, dome=0.3, mat=0, tone=-0.5)                   # the face, in its shadow
    cv.ellipse(15, 33, 5, 3.4, z=1.6, dome=0.6, mat=0, tone=0.05)                       # the folded hands
    cv.noise(0.15, cells=6, rng=np.random.default_rng(5))
    return _prop(cv, [STONE], relief=1.1, cavity=0.5, shadow=0.45)


def spr_wall_lamp():
    """A round wall lamp, a bulkhead light: a ring of dark iron round a warm glowing glass, a cage across it."""
    w, h = 16, 16
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.ellipse(8, 8, 7, 7, z=0.5, dome=0.6, mat=0)
    cv.ellipse(8, 8, 4.1, 4.1, z=0.9, dome=0.3, mat=1)
    cv.box(7.4, 4.2, 1.2, 7.6, z=1.6, top=0.2, bevel=0.3, mat=0, tone=0.1)          # the cage's bars across the glass
    cv.box(4.2, 7.4, 7.6, 1.2, z=1.6, top=0.2, bevel=0.3, mat=0, tone=0.1)
    em = ((cv.mat == 1) & (cv.id > 0)).astype(np.float32)
    return _prop(cv, [SOOT, EMBER], em=em, relief=0.8)


def spr_punt():
    """A flat-bottomed boat seen from its stern, as you would see one moored ahead of you down a canal: a broad hull
    of tarred planks, its gunwales catching the light, the dark well inside, a thwart across it."""
    w, h = 44, 18
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.polygon([(1, 5), (43, 5), (38, 17), (6, 17)], z=0.5, top=0.8, bevel=2.0, mat=0)          # the hull
    for y in (9, 12.5, 15.5):                                      # its planks
        cv.stroke([(4, y), (40, y)], 0.8, dome=0.3, mode='carve')
    cv.polygon([(4, 4), (40, 4), (38, 8), (6, 8)], z=0.7, top=0.2, bevel=0.6, mat=1)            # the well inside
    cv.box(3, 3, 38, 2, z=1.0, top=0.3, bevel=0.6, mat=0, tone=0.12)                           # the gunwale
    cv.box(8, 5, 28, 1.6, z=0.9, top=0.2, bevel=0.4, mat=0, tone=0.05)                         # a thwart
    return _prop(cv, [WOOD, SOOT], relief=1.0, cavity=0.45, shadow=0.45)


def spr_iron_cabinet():
    """A riveted iron cabinet against a wall: two plate doors one over the other in a dark frame, hinges down one
    side, a rivet at each door's corners, a round black lock plate with its keyhole, rust weeping from the rivets."""
    w, h = 26, 36
    rng = np.random.default_rng(13)
    cv = Canvas(w, h, wrap=False, ground=-9)
    cv.box(0.5, 0.5, 25, 35, z=0.4, top=0.5, bevel=1.0, mat=1, tone=0.25)                 # the frame
    for y0, hh in ((2.5, 13.5), (17.5, 16)):                       # the two doors
        cv.box(3, y0, 20.5, hh, z=1.0, top=0.25, bevel=0.9, mat=0, tone=0.08)
        for x, y in ((5, y0 + 2), (21.5, y0 + 2), (5, y0 + hh - 2), (21.5, y0 + hh - 2)):
            cv.ellipse(x, y, 0.85, 0.85, z=1.5, dome=0.5, mat=0, tone=0.3)              # rivets
        for y in (y0 + 3, y0 + hh - 4):
            cv.box(1.2, y, 2.4, 2.0, z=1.3, top=0.3, bevel=0.4, mat=1, tone=0.1)          # hinges
    cv.ellipse(14, 25.5, 3.4, 3.4, z=1.4, dome=0.3, mat=1, tone=-0.05)                    # the lock plate
    cv.ellipse(14, 25.5, 3.4, 3.4, z=0.15, dome=0.3, mode='add')
    cv.box(13.4, 24.0, 1.3, 2.8, z=0.8, top=0.1, bevel=0.2, mat=1, tone=-0.6)             # its keyhole
    for _ in range(4):                                             # rust weeping from the rivets
        x = rng.choice([5.0, 21.5])
        cv.stroke([(x, 5.5), (x + rng.uniform(-0.5, 0.5), rng.uniform(9, 14))], 0.8, dome=0.1, mode='carve')
    return _prop(cv, [IRON, SOOT], relief=1.0, cavity=0.5, shadow=0.45)


SPRITES = {'vault_arch': spr_vault_arch, 'broken_casement': spr_broken_casement, 'rose_bush': spr_rose_bush,
           'robed_statue': spr_robed_statue, 'tattered_curtain': spr_tattered_curtain, 'wall_lamp': spr_wall_lamp,
           'iron_cabinet': spr_iron_cabinet, 'punt': spr_punt, 'storm_cloud': spr_storm_cloud}
SPRITE_HEIGHT = {'vault_arch': 1.6, 'broken_casement': 1.0, 'rose_bush': 0.42, 'robed_statue': 1.9,
                 'tattered_curtain': 1.45, 'wall_lamp': 0.2, 'iron_cabinet': 0.7, 'punt': 0.2,
                 'storm_cloud': 6.0}
PROP_DEFAULTS = {'vault_arch': {'planes': 1, 'shadow': False}, 'broken_casement': {'planes': 1, 'shadow': False},
                 'tattered_curtain': {'planes': 1, 'shadow': False},
                 'storm_cloud': {'fullbright': True, 'shadow': False},
                 'wall_lamp': {'shadow': False, 'aura': {'color': [1.0, 0.72, 0.38], 'strength': 0.5, 'radius': 0.25}}}
NO_CONTACT_SHADOW = {'vault_arch', 'broken_casement', 'tattered_curtain', 'wall_lamp', 'storm_cloud'}
DECALS = {'glass_shards': dec_glass_shards, 'sigil': dec_sigil}

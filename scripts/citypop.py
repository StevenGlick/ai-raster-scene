"""City pop: the look of the paintings on Japanese city-pop records of the late 70s and the 80s - an endless summer
afternoon, a white house by a turquoise pool under a deep cobalt sky, palms and their hard shadows, nobody about.
Its surfaces are drawn clean and flat, so the `citypop` palette (post.py) prints them as a screen print would: white
stucco, ribbon windows and walls of glass that mirror the sky, a pool's water netted with light, its mosaic tiles,
the deck round it; a terrace's terracotta and a white railing over a cobalt sea; a boulevard's blacktop and lawn; a
roadside diner's stainless front, by day and lit. The props: parasols, fan palms, agaves, yachts, a bistro set, a
diner's sign and its gas pumps (a pool's lounger, ladder and diving board are objects, in objects.py). The `summer`
sky (skies.py) is the cobalt, with banks of cumulus standing on the horizon.
"""
import numpy as np

from texlib import T, _rng, col

WHITE = col('#f4f1ea')
FRAME = col('#fbfaf6')


def _lerp(a, b, t):
    t = np.asarray(t, np.float32)[..., None]
    return a * (1 - t) + b * t


def _bands(t, stops):
    """Colours down a gradient: `stops` is [(t, colour)...] from 0 to 1, `t` an array of positions."""
    out = np.zeros(np.shape(t) + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        m = (t >= t0) & (t <= t1)
        out[m] = _lerp(c0, c1, (np.asarray(t)[m] - t0) / max(t1 - t0, 1e-6))
    return out


def tex_stucco(name):
    """White stucco, clean: the faintest unevenness and a fleck here and there - tint it for a pastel house."""
    rng = _rng(name)
    y, x = np.mgrid[0:T, 0:T]
    tone = np.sin(2 * np.pi * (x / T + rng.random())) * np.sin(2 * np.pi * (2 * y / T + rng.random())) * 0.004
    rgb = np.broadcast_to(WHITE, (T, T, 3)) * (1 + tone)[..., None]
    fleck = rng.random((T, T)) < 0.005
    rgb = np.where(fleck[..., None], rgb * 0.975, rgb)
    return np.clip(rgb, 0, 1).astype(np.float32), None


def _sky_glass(h, w, foot=0.0):
    """A pane mirroring the sky: deep cobalt at its head paling toward its foot, two glints slanting across it, and
    with `foot` that share of it at the bottom dark with the reflected garden."""
    t = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    sky_end = 1.0 - foot
    pane = _bands(np.clip(t / max(sky_end, 1e-6), 0, 1), [(0.0, col('#1f50b0')), (0.45, col('#3f86d6')),
                                                           (1.0, col('#a8d8f2'))])
    if foot > 0:
        garden = t > sky_end
        pane[garden] = _lerp(col('#1d5a5e'), col('#123c46'), (t[garden] - sky_end) / foot)
    y, x = np.mgrid[0:h, 0:w]
    d = (x + y) % w                                      # glints run from the top right down to the left
    glint = ((d >= 10) & (d < 15)) | ((d >= 19) & (d < 21))
    pane[glint] = _lerp(pane[glint], np.ones(3, np.float32), 0.35)
    return pane


def tex_ribbon_window(name):
    """A storey of white stucco with a long low window across it: stack cells of it and the window runs on round the
    house unbroken, a slim white mullion every half unit, the glass mirroring the sky - deep cobalt at its head,
    paling toward the sill. A line of shadow under the sill."""
    rgb = tex_stucco('stucco')[0].copy()
    g0, g1 = 18, 44
    rgb[g0:g1] = _sky_glass(g1 - g0, T)
    rgb[g0 - 2:g0] = FRAME * 0.93                        # the head of the frame, in its own shadow
    rgb[g1:g1 + 2] = FRAME                               # the sill
    rgb[g1 + 2:g1 + 3] = WHITE * 0.82                    # and its shadow on the wall
    for m in (0, 32):
        rgb[g0:g1, m:m + 2] = FRAME * 0.97
    return np.clip(rgb, 0, 1).astype(np.float32), None


def tex_ribbon_window_lit(name):
    """The ribbon window after dark, the rooms behind it lit warm - a pale ceiling, a lamp's pool of light, a red
    curtain half drawn - the white wall round it in the dusk."""
    rgb = tex_stucco('stucco')[0].copy()
    em = np.zeros((T, T), np.float32)
    g0, g1 = 18, 44
    y, x = np.mgrid[g0:g1, 0:T]
    room = _bands((y - g0) / (g1 - g0 - 1.0), [(0.0, col('#ffd48e')), (0.6, col('#ffe8b6')), (1.0, col('#e2a262'))])
    lamp = np.exp(-(((x - 14) / 7.0) ** 2 + ((y - 34) / 6.0) ** 2))
    room = room + lamp[..., None] * (col('#fff6dc') - room) * 0.8
    curtain = (x >= 40) & (x < 54)
    room[curtain] = _lerp(col('#c8563c'), col('#a8402e'), (x[curtain] - 40) / 14.0)
    rgb[g0:g1] = room
    em[g0:g1] = np.where(curtain, 0.45, 0.75)
    rgb[g0 - 2:g0] = FRAME * 0.93
    rgb[g1:g1 + 2] = FRAME
    rgb[g1 + 2:g1 + 3] = WHITE * 0.82
    for m in (0, 32):
        rgb[g0:g1, m:m + 2] = FRAME * 0.97
        em[g0:g1, m:m + 2] = 0.0
    return np.clip(rgb, 0, 1).astype(np.float32), em


def tex_glass_wall(name):
    """A storey of glass from floor to ceiling - sliding doors onto a terrace - between slim white frames: the panes
    mirror the sky, cobalt at the head paling down, the dark line of the garden along their foot, a glint across."""
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = FRAME
    rgb[3:61] = _sky_glass(58, T, foot=0.22)
    rgb[3:5] *= 0.9                                      # the head of the frame shades the glass under it
    for m in (0, 32):
        rgb[:, m:m + 2] = FRAME * 0.97
    rgb[61:] = FRAME * 0.9                               # the threshold
    return np.clip(rgb, 0, 1).astype(np.float32), None


def tex_glass_wall_lit(name):
    """The same wall of glass after dark, lit from inside: a warm room behind the panes - a pale wall, a lamp's pool of
    light, the dark back of a sofa along the foot - glowing between the frames."""
    rng = _rng(name)
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = FRAME * 0.8
    em = np.zeros((T, T), np.float32)
    y, x = np.mgrid[3:61, 0:T]
    room = _bands((y - 3) / 57.0, [(0.0, col('#f2c47e')), (0.55, col('#ffe0a6')), (0.72, col('#e8a868')),
                                   (1.0, col('#b0703c'))])
    lamp = np.exp(-(((x - 46) / 9.0) ** 2 + ((y - 26) / 12.0) ** 2))
    room = room + lamp[..., None] * (col('#fff4d6') - room) * 0.8
    sofa = (y > 44) & (y < 54) & (((x > 4) & (x < 27)) | ((x > 36) & (x < 60)))
    room[sofa] = col('#6a3a2a') * (0.9 + 0.1 * rng.random())
    rgb[3:61] = room
    em[3:61] = np.where(sofa, 0.3, 0.75)
    for m in (0, 32):
        rgb[:, m:m + 2] = FRAME * 0.8
        em[:, m:m + 2] = 0.0
    em[:3] = em[61:] = 0.0
    return np.clip(rgb, 0, 1).astype(np.float32), em


def _caustics(name, cells=10, width=1.25):
    """The net of bright lines sunlight makes on a pool's floor through the ripples: the walls between wobbling
    cells, tiling. Returns the lines (bool) and a slow tone across the water (0-1)."""
    rng = _rng(name)
    y, x = np.mgrid[0:T, 0:T].astype(np.float32)
    wx = x + 2.4 * np.sin(2 * np.pi * (3 * y / T + rng.random())) + 1.2 * np.sin(2 * np.pi * (5 * (x + y) / T))
    wy = y + 2.4 * np.sin(2 * np.pi * (3 * x / T + rng.random())) + 1.2 * np.sin(2 * np.pi * (4 * (x - y) / T))
    pts = rng.random((cells, 2)) * T
    d = []
    for px, py in pts:
        dx = (wx - px + T / 2) % T - T / 2
        dy = (wy - py + T / 2) % T - T / 2
        d.append(np.hypot(dx, dy))
    d = np.sort(np.stack(d), axis=0)
    lines = (d[1] - d[0]) < width
    tone = 0.5 + 0.5 * np.sin(2 * np.pi * (x / T + rng.random())) * np.cos(2 * np.pi * (y / T + rng.random()))
    return lines, tone


def tex_pool_water(name):
    """A swimming pool's water seen from its edge: clear turquoise over a pale floor, netted with the bright wavering
    lines the sun makes through its ripples - drawn crisp, as a painter would. It mirrors a little."""
    lines, tone = _caustics('pool_water')
    rgb = _lerp(col('#22b2cc'), col('#2ac2d8'), tone)
    rgb[lines] = col('#a8f0f2')
    return rgb.astype(np.float32), None


def tex_pool_water_lit(name):
    """The pool after dark with its lights on under the water: the whole of it glowing turquoise, the net of lines
    brighter still."""
    lines, tone = _caustics('pool_water')
    rgb = _lerp(col('#0d9cc0'), col('#18b8d6'), tone)
    rgb[lines] = col('#c8fffb')
    em = np.where(lines, 0.95, 0.6 + 0.15 * tone).astype(np.float32)
    return rgb.astype(np.float32), em


def tex_pool_tile(name):
    """A pool's mosaic: small square tiles in a few blues, white grout between - for the inside of the pool, its
    `side` (the bank seen below the waterline), or a wall."""
    rng = _rng(name)
    blues = [col('#1d6cc0'), col('#2a84d2'), col('#3a9ade'), col('#2476c8')]
    rgb = np.empty((T, T, 3), np.float32)
    s = 8
    for j in range(T // s):
        for i in range(T // s):
            rgb[j * s:(j + 1) * s, i * s:(i + 1) * s] = blues[int(rng.integers(len(blues)))]
    grout = (np.arange(T) % s == 0)
    rgb[grout, :] = col('#dfeef4')
    rgb[:, grout] = col('#dfeef4')
    return rgb, None


def tex_pool_deck(name):
    """The deck round a pool: big pale slabs of travertine laid square, two to a unit, crisp joints between them."""
    rng = _rng(name)
    rgb = np.empty((T, T, 3), np.float32)
    base = col('#e6e0d4')
    rgb[:] = base
    pores = rng.random((T, T)) < 0.01
    rgb[pores] *= 0.97
    joint = (np.arange(T) % 32 == 0)
    rgb[joint, :] = col('#c9c1b2')
    rgb[:, joint] = col('#c9c1b2')
    return np.clip(rgb, 0, 1), None


def tex_terracotta_tile(name):
    """A terrace of terracotta tiles, two to a unit, a darker joint between them."""
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = col('#c86a44')
    grout = (np.arange(T) % 32 < 2)
    rgb[grout, :] = col('#a04c30')
    rgb[:, grout] = col('#a04c30')
    return rgb, None


def tex_summer_sea(name):
    """The sea on a summer afternoon from the shore: deep cobalt in slow swells, the sun glancing off it in short
    bright dashes."""
    rng = _rng(name)
    y, x = np.mgrid[0:T, 0:T].astype(np.float32)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * (2 * y / T + 0.15 * np.sin(2 * np.pi * x / T) + rng.random()))
    rgb = _lerp(col('#1c4aa6'), col('#2a62c2'), (swell > 0.62).astype(np.float32))
    for _ in range(26):                                     # the glints: short level dashes, a few long ones
        gx, gy = int(rng.integers(T)), int(rng.integers(T))
        n = int(rng.integers(2, 6)) + (5 if rng.random() < 0.15 else 0)
        xs = (gx + np.arange(n)) % T
        rgb[gy, xs] = col('#cfe8f8') if rng.random() < 0.7 else col('#ffffff')
    return rgb, None


def tex_white_railing(name):
    """A white railing of round tube, see-through: a top rail at hand height on a wall 0.45 tall (it takes the bottom
    of the texture, as any low wall does), a rail between, a post every half unit, the view between them."""
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = FRAME
    alpha = np.zeros((T, T), np.float32)
    for r0 in (35, 49):                                     # the top rail (0.42 up), the middle one
        alpha[r0:r0 + 3] = 1
        rgb[r0 + 2] = col('#c9cde2')                        # the underside of the tube, in its own shade
    for c0 in (0, 32):
        alpha[35:, c0:c0 + 2] = 1
        rgb[35:, c0 + 1] = col('#dcdce6')
    return rgb, None, alpha


def tex_blacktop(name):
    """A road of fresh blacktop as a poster paints it: smooth slate blue-grey, the odd fleck of stone."""
    rng = _rng(name)
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = col('#4a5068')
    fleck = rng.random((T, T)) < 0.02
    rgb[fleck] = col('#5a6078')
    return rgb, None


def tex_blacktop_line(name):
    """The blacktop with a road's centre line along the middle of it, east to west: a dash and a gap to a unit - lay
    it down the middle row of a road's cells."""
    rgb = tex_blacktop('blacktop')[0].copy()
    rgb[28:36, 4:36] = col('#ffc93a')
    return rgb, None


def tex_lawn_stripes(name):
    """A lawn just mown, in broad stripes of two greens - the way the mower went, up and back - flat as felt."""
    rgb = np.empty((T, T, 3), np.float32)
    rgb[:] = col('#3f9a4c')
    rgb[:, 32:] = col('#56ad56')
    return rgb, None


def _diner(lit):
    """A storey of a stainless-steel roadside diner: a red band along the roof's edge over a fluted strip of steel,
    a long row of windows in chrome frames, a red stripe under them and fluted steel down to the ground. By day the
    windows mirror the sky; lit, the room inside glows warm through them and neon runs pink along the roof's edge and
    turquoise along the stripe."""
    rgb = np.empty((T, T, 3), np.float32)
    em = np.zeros((T, T), np.float32)
    rgb[0:5] = col('#d9302e')
    rgb[5] = FRAME
    rgb[6:12] = np.where((np.arange(6) % 2 == 0)[:, None, None], col('#e6e6ee'), col('#b6bed9'))
    if lit:
        y, x = np.mgrid[12:37, 0:T]
        room = _bands((y - 12) / 24.0, [(0.0, col('#ffd48e')), (0.65, col('#ffe8b6')), (1.0, col('#e8a866'))])
        counter = (y >= 30)
        room[counter] = col('#c8564a')                      # the counter's red front, under the window line
        rgb[12:37] = room
        em[12:37] = np.where(counter, 0.4, 0.6)
        rgb[4], em[4] = col('#ff86c8'), 0.95                # neon along the roof's edge
    else:
        rgb[12:37] = _sky_glass(25, T)
    for m in range(0, T, 16):
        rgb[12:37, m:m + 2] = col('#e6e6ee')
        em[12:37, m:m + 2] = 0.0
    rgb[12] = rgb[36] = col('#e6e6ee')
    em[12] = em[36] = 0.0
    rgb[37:40] = col('#d9302e')
    if lit:
        rgb[38], em[38] = col('#53e6ff'), 0.95              # and turquoise along the stripe
    ribs = (np.arange(40, T) % 4 == 3)
    rgb[40:] = np.where(ribs[:, None, None], col('#9ea6c8'), col('#dcdce6'))
    return rgb, (em if lit else None)


def tex_diner_front(name):
    return _diner(False)


def tex_diner_front_lit(name):
    return _diner(True)


# ------------------------------------------------------------------ props

PARASOL = ('#d9302e', '#15a6c2', '#ffc93a', '#2658c6')


def _parasol(k):
    """A market parasol over a pool's deck: an eight-sided canopy striped white and a colour, a scalloped valance
    round its rim, a white pole down to a weighted foot. Drawn four ways: 0 red, 1 turquoise, 2 yellow, 3 blue."""
    c, white = col(PARASOL[k % len(PARASOL)]), col('#f8f6f0')
    w, h = 48, 46
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    ax, ay, ey, R = 24.0, 3.0, 15.0, 22.5
    seams = np.array([-0.92, -0.38, 0.38, 0.92])                 # where the eight panels meet, seen side on
    t = (yy - ay) / (ey - ay)
    canopy = (t >= 0) & (t <= 1) & (np.abs(xx - ax) <= R * t + 0.5)
    s = np.clip((xx - ax) / np.maximum(R * t, 1e-3), -1, 1)
    paint = np.where((np.searchsorted(seams, s) % 2 == 0)[..., None], c, white)
    shade = np.where(s > 0.38, 0.84, np.where(s < -0.38, 1.0, 0.94))[..., None]    # the sun is up to the left
    rgba[canopy, :3] = (paint * shade)[canopy]
    rgba[canopy, 3] = 1
    se = np.clip((xx - ax) / R, -1, 1)
    hang = 1.0 + 1.8 * np.abs(np.sin(np.pi * (xx - ax + R) / 5.625))         # a scallop to each stretch of rim
    valance = (yy >= ey) & (yy < ey + hang) & (np.abs(xx - ax) <= R)
    vpaint = np.where((np.searchsorted(seams, se) % 2 == 0)[..., None], c, white) * 0.8
    rgba[valance, :3] = vpaint[valance]
    rgba[valance, 3] = 1
    pole = (np.abs(xx - ax) < 1.3) & (yy > ey) & (yy < h - 2)
    rgba[pole, :3] = np.where((xx[pole] > ax)[:, None], col('#c6cad8'), col('#f6f4ee'))
    rgba[pole, 3] = 1
    knob = np.hypot(xx - ax, yy - 2.2) < 1.7
    rgba[knob, :3], rgba[knob, 3] = white * 0.95, 1
    foot = (np.abs(xx - ax) < 5.5) & (yy >= h - 3)
    rgba[foot, :3] = np.where((xx[foot] > ax + 2)[:, None], col('#7a84b2'), col('#b6bed9'))
    rgba[foot, 3] = 1
    return rgba, np.zeros((h, w), np.float32)


def spr_fan_palm():
    """A Mexican fan palm, as they line the boulevards of a coast in the sun: a trunk as slim as a lamp post rising
    very tall, a skirt of dead fronds hanging under a small round head of fans."""
    rng = _rng('fan_palm')
    w, h = 44, 210
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    cx, cy = 22.0, 21.0
    f = np.clip((yy - 30) / (h - 30), 0, 1)
    mid = cx + 3.0 * f * f                                        # it bows a little at the foot
    half = 1.5 + 1.3 * f
    trunk = (yy > 30) & (np.abs(xx - mid) <= half)
    ring = (yy.astype(int) % 5 == 0)
    rgba[trunk, :3] = np.where((xx[trunk] > mid[trunk])[:, None], col('#6e5e50'), col('#a08c74'))
    rgba[trunk & ring, :3] *= 1.12
    rgba[trunk, 3] = 1
    sk = (yy >= 22) & (yy < 60)                                   # the skirt of dead fronds
    swell = np.where(yy < 38, 4.0 + 2.5 * (yy - 22) / 16, 6.5 - 3.5 * (yy - 38) / 22)
    skirt = sk & (np.abs(xx - cx) <= swell)
    streak = (np.floor(xx * 0.9 + rng.random() * 3) % 3 == 0)
    rgba[skirt, :3] = np.where(streak[skirt][:, None], col('#8a6a40'), col('#b48c58'))
    rgba[skirt & (xx > cx + 3), :3] *= 0.82
    rgba[skirt, 3] = 1
    heart = np.hypot((xx - cx) / 1.2, yy - cy - 1) < 4.5            # the dense heart of the crown
    rgba[heart, :3], rgba[heart, 3] = col('#18643e'), 1
    fans = []
    for a in (-120, -150, -60, -30, -175, -5, -90):               # the upper fans, lit - the top one last
        fans.append((a + rng.uniform(-8, 8), rng.uniform(10.0, 12.5), 1))
    for a in (25, 60, 120, 155):                                  # the lower ones, drooping, in shade
        fans.append((a + rng.uniform(-8, 8), rng.uniform(8.0, 10.0), 0))
    fans.sort(key=lambda q: q[2])                                 # shade first, the lit ones over them
    for a, r, lit in fans:
        th = np.radians(a)
        fx, fy = cx + 2.5 * np.cos(th), cy + 2.5 * np.sin(th)
        d = np.hypot(xx - fx, yy - fy)
        ang = np.arctan2(yy - fy, xx - fx)
        off = np.angle(np.exp(1j * (ang - th)))
        split = np.abs(np.sin(off * 7))                           # the fan's segments, split apart toward their tips
        leaf = (d <= r * (0.7 + 0.3 * split)) & (np.abs(off) < 0.95) & ~((d > 0.5 * r) & (split < 0.3))
        tone = col('#5cb35a') if lit else col('#257f46')
        tone2 = col('#3b9a4e') if lit else col('#18643e')
        rgba[leaf, :3] = np.where((off[leaf] > 0)[:, None], tone2, tone)
        rgba[leaf, 3] = 1
    return rgba, np.zeros((h, w), np.float32)


def spr_agave():
    """An agave in a white cubic planter, its thick blue-green leaves fanned up and out to sharp points - by a modern
    house's door, along its terrace."""
    rng = _rng('agave')
    w, h = 30, 30
    rgba = np.zeros((h, w, 4), np.float32)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    box = (yy >= 19) & (xx >= 6) & (xx < 24)
    rgba[box, :3] = np.where((xx[box] >= 19)[:, None], col('#c9cde2'), col('#f6f3ec'))
    rgba[box & (yy < 20.5), :3] = col('#e6e6ee')
    rgba[box, 3] = 1
    bx, by = 15.0, 19.5
    for a in sorted(np.linspace(-168, -12, 9) + rng.uniform(-5, 5, 9), key=lambda q: -abs(q + 90)):
        th = np.radians(a)                                        # the outer leaves first, the upright ones over them
        length = rng.uniform(11.0, 14.0) - 3.0 * abs(np.cos(th))
        along = (xx - bx) * np.cos(th) + (yy - by) * np.sin(th)
        across = -(xx - bx) * np.sin(th) + (yy - by) * np.cos(th)
        taper = np.clip(1 - along / length, 0, 1) ** 0.8
        leaf = (along > 0) & (along < length) & (np.abs(across) < 3.4 * taper) & (yy < 20)
        rgba[leaf, :3] = np.where((across[leaf] > 0)[:, None], col('#3f8a80'), col('#6eb4a4'))
        rgba[leaf, 3] = 1
    return rgba, np.zeros((h, w), np.float32)


def dec_pool_ring():
    """An inflatable ring afloat on a pool, seen from above: its fat tube striped pink and white, a shine on it."""
    n = 32
    rgba = np.zeros((n, n, 4), np.float32)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + 0.5 - n / 2
    r = np.hypot(xx, yy)
    tube = (r > 7.5) & (r < 15.0)
    seg = (np.floor((np.arctan2(yy, xx) + np.pi) / (np.pi / 4)) % 2 == 0)
    rgba[tube, :3] = np.where(seg[tube][:, None], col('#ff8fa0'), col('#f8f6f0'))
    shine = tube & (np.abs(r - 11.5) < 1.2) & (xx < 0) & (yy < 0)
    rgba[shine, :3] = col('#ffffff')
    rgba[tube & (xx + yy > 8), :3] *= 0.85
    rgba[tube, 3] = 1
    return rgba, np.zeros((n, n), np.float32)


YACHT = ('#1a2238', '#d9302e', '#15a6c2')


def _yacht(k):
    """A white sailing yacht side on, under full sail: a long low hull with its sheer picked out in a stripe (0 navy,
    1 red, 2 turquoise), a cabin top with a row of dark windows, the mainsail and the jib white in the sun, the jib a
    shade cooler. Its bow points right; `flip` it to sail the other way."""
    from PIL import Image, ImageDraw
    w, h = 64, 82
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    stripe = tuple(int(c * 255) for c in col(YACHT[k % len(YACHT)]))
    d.polygon([(30, 6), (30, 58), (8, 58)], fill=(255, 255, 255, 255))                  # the mainsail
    d.polygon([(30, 6), (19, 58), (8, 58)], fill=(238, 240, 246, 255))                  # its belly, a shade cooler
    d.polygon([(32, 9), (58, 63), (35, 61)], fill=(226, 230, 240, 255))                 # the jib
    d.line([(31, 3), (31, 64)], fill=(150, 156, 176, 255), width=1)                     # the mast
    d.line([(7, 59), (31, 59)], fill=(150, 156, 176, 255), width=1)                     # the boom
    d.rectangle([17, 61, 41, 66], fill=(246, 243, 236, 255))                            # the cabin top
    for x in range(20, 39, 4):
        d.rectangle([x, 63, x + 2, 64], fill=(26, 34, 56, 255))                         # its windows
    d.polygon([(4, 66), (61, 64), (55, 74), (9, 75), (5, 71)], fill=(255, 255, 255, 255))   # the hull
    d.polygon([(4, 66), (61, 64), (60, 66), (4, 68)], fill=stripe + (255,))            # the sheer stripe
    d.polygon([(9, 73), (56, 72), (55, 74), (9, 75)], fill=(201, 205, 226, 255))        # its shaded underside
    rgba = np.asarray(im, np.float32) / 255
    return rgba, np.zeros((h, w), np.float32)


def spr_bistro_set():
    """A white bistro set on a terrace: a little round table on a pedestal, a chair of white wire either side of it,
    two glasses of something orange on the table."""
    from PIL import Image, ImageDraw
    w, h = 42, 26
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    white, shade, dark = (246, 243, 236, 255), (201, 205, 226, 255), (152, 162, 200, 255)
    for x0, sgn in ((2, 1), (39, -1)):                                                   # the chairs, facing in
        back = x0 if sgn > 0 else x0 - 1
        d.rectangle([back, 3, back + 1, 24], fill=white)                                # the back's upright, a leg
        d.rectangle([back, 3, back + 1, 4], fill=white)
        for y in (6, 9, 12):
            d.line([(back, y), (back + 1, y)], fill=shade)
        seat = (back, 14, back + 9 * sgn, 15) if sgn > 0 else (back + 9 * sgn, 14, back + 1, 15)
        d.rectangle([min(seat[0], seat[2]), 14, max(seat[0], seat[2]), 15], fill=white)
        fx = back + 8 * sgn
        d.line([(fx, 16), (fx, 24)], fill=shade, width=1)                               # the front leg
    d.ellipse([12, 8, 30, 12], fill=white)                                               # the table top
    d.line([(12, 11), (30, 11)], fill=shade)
    d.rectangle([20, 12, 21, 23], fill=shade)                                            # its pedestal
    d.rectangle([16, 23, 25, 25], fill=dark)                                             # and foot
    for x in (16, 24):                                                                   # two glasses
        d.rectangle([x, 5, x + 1, 8], fill=(243, 154, 30, 255))
    rgba = np.asarray(im, np.float32) / 255
    return rgba, np.zeros((h, w), np.float32)


def _diner_sign(lit):
    """A roadside diner's sign on its pole: a white board edged in red, DINER across it in red, and under it an arrow
    of light bulbs pointing in off the road. Lit, the board goes dark and the letters, its edge and the bulbs glow -
    pink neon, turquoise neon, gold bulbs."""
    from PIL import Image, ImageDraw
    from pixelfont import PixelFont
    w, h = 72, 150
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow = Image.new('L', (w, h), 0)
    d, g = ImageDraw.Draw(im), ImageDraw.Draw(glow)
    red, white, teal = (217, 48, 46, 255), (246, 243, 236, 255), (21, 166, 194, 255)
    d.rectangle([33, 58, 38, h - 1], fill=teal)                          # the pole
    d.rectangle([37, 58, 38, h - 1], fill=(11, 138, 168, 255))
    board, edge = ((26, 34, 56, 255), (83, 230, 255, 255)) if lit else (white, red)
    d.rounded_rectangle([1, 6, 70, 46], radius=8, fill=edge)
    d.rounded_rectangle([4, 9, 67, 43], radius=6, fill=board)
    if lit:
        g.rounded_rectangle([1, 6, 70, 46], radius=8, fill=240)
        g.rounded_rectangle([4, 9, 67, 43], radius=6, fill=0)
    mask = PixelFont().render_mask('DINER', scale=2)
    x0 = (w - mask.width) // 2
    ink = (255, 134, 200, 255) if lit else red
    im.paste(Image.new('RGBA', mask.size, ink), (x0, 16), mask)
    if lit:
        glow.paste(250, (x0, 16), mask)
    arrow = [(8, 50), (54, 50), (54, 44), (68, 56), (54, 68), (54, 62), (8, 62)]
    d.polygon(arrow, fill=(26, 34, 56, 255) if lit else red)
    for x in range(12, 54, 6):                                           # the bulbs along it
        for y in (53, 59):
            d.rectangle([x, y, x + 1, y + 1], fill=(255, 207, 112, 255) if lit else (255, 201, 58, 255))
            if lit:
                g.rectangle([x, y, x + 1, y + 1], fill=245)
    rgba = np.asarray(im, np.float32) / 255
    return rgba, np.asarray(glow, np.float32) / 255


PUMPS = ('#d9302e', '#15a6c2')


def _gas_pump(k):
    """An old gas pump on the forecourt: a tall rounded body (0 red, 1 turquoise), a white face with its dial, a
    hose hung on its side and a glass globe on top that glows."""
    from PIL import Image, ImageDraw
    w, h = 22, 42
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    glow = Image.new('L', (w, h), 0)
    d, g = ImageDraw.Draw(im), ImageDraw.Draw(glow)
    body = tuple(int(c * 255) for c in col(PUMPS[k % len(PUMPS)])) + (255,)
    d.rounded_rectangle([3, 9, 18, 38], radius=3, fill=body)
    d.rectangle([14, 11, 18, 37], fill=tuple(int(c * 0.8) for c in body[:3]) + (255,))   # its side in shade
    d.rectangle([6, 13, 15, 22], fill=(246, 243, 236, 255))              # the face
    d.rectangle([8, 15, 13, 17], fill=(26, 34, 56, 255))                 # the dial
    d.line([(19, 14), (21, 22), (20, 32)], fill=(26, 34, 56, 255), width=1)   # the hose
    d.rectangle([2, 38, 19, 41], fill=(122, 132, 178, 255))              # the island's kerb under it
    d.ellipse([5, 0, 16, 9], fill=(255, 246, 220, 255))                  # the globe
    d.rectangle([5, 4, 16, 5], fill=body)
    g.ellipse([5, 0, 16, 9], fill=230)
    rgba = np.asarray(im, np.float32) / 255
    return rgba, np.asarray(glow, np.float32) / 255


# ------------------------------------------------------------------ the tables

TEXTURES = {'stucco': tex_stucco, 'ribbon_window': tex_ribbon_window, 'ribbon_window_lit': tex_ribbon_window_lit,
            'glass_wall': tex_glass_wall, 'glass_wall_lit': tex_glass_wall_lit, 'pool_water': tex_pool_water,
            'pool_water_lit': tex_pool_water_lit, 'pool_tile': tex_pool_tile, 'pool_deck': tex_pool_deck,
            'terracotta_tile': tex_terracotta_tile, 'summer_sea': tex_summer_sea, 'white_railing': tex_white_railing,
            'blacktop': tex_blacktop, 'blacktop_line': tex_blacktop_line, 'lawn_stripes': tex_lawn_stripes,
            'diner_front': tex_diner_front, 'diner_front_lit': tex_diner_front_lit}
# drawn clean, and kept clean: the scene's surface noise barely touches them
TEXTURE_NOISE = {'stucco': 0.15, 'ribbon_window': 0.1, 'ribbon_window_lit': 0.05, 'glass_wall': 0.05,
                 'glass_wall_lit': 0.05, 'pool_water': 0.1, 'pool_water_lit': 0.05, 'pool_tile': 0.2, 'pool_deck': 0.25,
                 'terracotta_tile': 0.3, 'summer_sea': 0.1, 'white_railing': 0.05, 'blacktop': 0.2,
                 'blacktop_line': 0.2, 'lawn_stripes': 0.2, 'diner_front': 0.1, 'diner_front_lit': 0.05}
TEXTURE_REFLECT = {'pool_water': 0.32, 'pool_water_lit': 0.22, 'summer_sea': 0.3}

SPRITES = {'parasol': lambda: _parasol(0), 'fan_palm': spr_fan_palm, 'agave': spr_agave, 'yacht': lambda: _yacht(0),
           'bistro_set': spr_bistro_set, 'diner_sign': lambda: _diner_sign(False),
           'diner_sign_lit': lambda: _diner_sign(True), 'gas_pump': lambda: _gas_pump(0)}
SPRITE_HEIGHT = {'parasol': 0.95, 'fan_palm': 6.5, 'agave': 0.55, 'yacht': 3.6, 'bistro_set': 0.36,
                 'diner_sign': 4.4, 'diner_sign_lit': 4.4, 'gas_pump': 0.72}
# their own shadows (sprite_shadows) are the ones that matter: a contact blob under them prints as a stain
PROP_DEFAULTS = {'parasol': {'shadow': False}, 'bistro_set': {'shadow': False}}
VARIANTS = {'parasol': (4, _parasol), 'yacht': (3, _yacht), 'gas_pump': (2, _gas_pump)}
DECALS = {'pool_ring': dec_pool_ring}

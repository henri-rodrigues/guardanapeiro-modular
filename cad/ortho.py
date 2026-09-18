import json, pickle
from views import *
tex = sticker_texture()
S = scene()
out = {}
VIEWS = {
    'frontal':  ((0, -1, 0), (1, 0, 0)),
    'superior': ((0, 0, 1), (1, 0, 0)),
    'dir':      ((1, 0, 0), (0, 1, 0)),
    'esq':      ((-1, 0, 0), (0, -1, 0)),
}
for k, (d, r) in VIEWS.items():
    im, mp = render_map(S, d, r, s=8, tex=tex)
    im.save(f'orto_{k}.png'); out[k] = {kk: float(v) for kk, v in mp.items()}
# peças isoladas
Sb = scene(plate_on=False, org_on=False)
im, mp = render_map(Sb, (-1, 0, 0), (0, -1, 0), s=10); im.save('orto_base_esq.png'); out['base_esq'] = {kk: float(v) for kk, v in mp.items()}
im, mp = render_map(Sb, (1, 0, 0), (0, 1, 0), s=10); im.save('orto_base_dir.png'); out['base_dir'] = {kk: float(v) for kk, v in mp.items()}
json.dump(out, open('ortho_map.json', 'w'), indent=1)
print(out)

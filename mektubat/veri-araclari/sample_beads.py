"""Elle denetim için hizalama örnekleri (sabit tohum). Âyet atfı ya da beyit içeren gruplar
dışarıda bırakılır: yalnız sıradan cümleler, yani otomatik ölçütlerin göremediği durumlar.
Kullanım: python3 -I sample_beads.py <veri dizini> <dil> <güven 1|2|3> <adet> [tohum]
"""
import json, random, re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import load, units, fa_refs, tr_refs
D, L, C, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
seed = int(sys.argv[5]) if len(sys.argv) > 5 else 20261116
T = load(D); A = json.load(open(D + "/align.json"))
U = {}
pool = []
for k in T["index"]["order"]:
    if L not in A[k]: continue
    for r in A[k][L]:
        a0, na, b0, nb, c, p, lx = r
        if c != C or not na or not nb: continue
        pool.append((k, r))
rnd = random.Random(seed * 10 + C)
rnd.shuffle(pool)
shown = 0
for k, (a0, na, b0, nb, c, p, lx) in pool:
    if k not in U: U[k] = {l: units(T, k, l) for l in ("fa", L)}
    fa = " ".join(U[k]["fa"][a0:a0 + na]).strip(); tg = " ".join(U[k][L][b0:b0 + nb]).strip()
    if fa_refs(fa) or tr_refs(tg) or not re.search(r"[A-Za-zçğıöşü]", tg) and L != "ar": continue
    shown += 1
    print(f"### {shown} | {k} | FA[{a0}+{na}] ↔ {L.upper()}[{b0}+{nb}] | güven {c} p={p} söz={lx}")
    print("FA:", fa[:330]); print(L.upper() + ":", tg[:330]); print()
    if shown >= N: break

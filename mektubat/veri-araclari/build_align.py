"""Üretim hizalaması: uzunluk + öğrenilmiş sözlük + âyet atıfları. Çıktı: data/align.json
Her grup: [fa_başlangıç, fa_adet, hedef_başlangıç, hedef_adet, güven(1-3), uzunluk_p, sözcük_oranı]
Güven: 1 güçlü, 2 orta, 3 zayıf. Eşikler calib() ile elle denetlenmiş örneklerden ayarlanır.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import *

D = sys.argv[1]; OUT = D + "/align.json"
T = load(D); ORDER = T["index"]["order"]
U = {k: {l: units(T, k, l) for l in ("fa", "ar", "ak", "hk")} for k in ORDER}

W_LEX = 25.0  # align_tune.py ile seçildi: Kur'ân ve beyit ölçütlerinin ikisinde de en iyi bölge

def run(dics=None):
    AL = {}
    for k in ORDER:
        AL[k] = {"U": U[k]}
        for l in ("ar", "ak", "hk"):
            if not (U[k]["fa"] and U[k][l]): continue
            sim = Sim(U[k]["fa"], U[k][l], l, dics[l]) if dics else None
            ra = rb = None
            if l == "ak" and dics:
                ra = [fa_refs(s) for s in U[k]["fa"]]; rb = [tr_refs(s) for s in U[k]["ak"]]
            AL[k][l] = align(U[k]["fa"], U[k][l], sim, ra, rb, w_lex=W_LEX, moves=MV_X)
    return AL

def conf(p, lex, ref, na, nb, lang):
    """Eşikler elle denetlenmiş örneklerle ayarlandı (sample_beads.py). Hakikat tercümesinin
    sözlüğü 313 mektuptan öğrenildiği için daha küçüktür; aynı doğruluk daha düşük sözcük oranıyla gelir."""
    if not na or not nb: return 3
    if ref == 1: return 1
    s1, s2 = (0.22, 0.10) if lang == "hk" else (0.34, 0.20)
    if lex >= s1 and p >= 0.05: return 1
    if lex >= s2 or (p >= 0.4 and lex >= s2 / 2): return 2
    return 3

t0 = time.time()
AL = run(); print("uzunluk hizalaması", int(time.time() - t0), "sn", flush=True)
for it in (1, 2):
    dics = {l: learn_dict(T, AL, l) for l in ("ar", "ak", "hk")}
    AL = run(dics); print(f"sözcüklü hizalama #{it}", int(time.time() - t0), "sn", flush=True)
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build"), exist_ok=True)
json.dump({l: {f: sorted(g) for f, g in d.items()} for l, d in dics.items()},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "dict.json"), "w"), ensure_ascii=False)

def absorb(beads, sim):
    """Karşılıksız kalan cümleleri (yalnız hedef ya da yalnız Farsça gruplar) sözcük benzerliği yüksek
    olan komşu gruba katar. Tercümanlar tek bir Farsça cümleyi 7-9 cümleye bölebildiği için bunlar
    çoğunlukla komşu cümlenin devamıdır. Döner: [(a, b, katılan_cümleler_benzersiz_mi)]"""
    B = [[list(a), list(b), False] for a, b, p in beads]
    def score(bd, j=None, i=None):
        if j is not None: return sum(sim(x, j) for x in bd[0])
        return sum(sim(i, y) for y in bd[1])
    changed = True
    while changed:
        changed = False
        for x, bd in enumerate(B):
            a, b = bd[0], bd[1]
            if (a and b) or (not a and not b): continue
            prev = next((y for y in range(x - 1, -1, -1) if B[y][0] and B[y][1]), None)
            nxt = next((y for y in range(x + 1, len(B)) if B[y][0] and B[y][1]), None)
            if prev is None and nxt is None: continue
            # yalnız bitişik gruba katılabilir (araya başka karşılıksız grup girmesin)
            if prev is not None and prev != x - 1: prev = None
            if nxt is not None and nxt != x + 1: nxt = None
            if prev is None and nxt is None: continue
            if b:   # yalnız hedef tarafı
                sp = sum(score(B[prev], j=j) for j in b) if prev is not None else -1
                sn = sum(score(B[nxt], j=j) for j in b) if nxt is not None else -1
                to = prev if (sp >= sn and prev is not None) or nxt is None else nxt
                B[to][1] = sorted(B[to][1] + b); B[to][2] = B[to][2] or max(sp, sn) <= 0
            else:   # yalnız Farsça tarafı
                sp = sum(score(B[prev], i=i) for i in a) if prev is not None else -1
                sn = sum(score(B[nxt], i=i) for i in a) if nxt is not None else -1
                to = prev if (sp >= sn and prev is not None) or nxt is None else nxt
                B[to][0] = sorted(B[to][0] + a); B[to][2] = B[to][2] or max(sp, sn) <= 0
            B[x][0], B[x][1] = [], []
            changed = True
        B = [bd for bd in B if bd[0] or bd[1]]
    return B

exp = {}; dist = {l: [0, 0, 0, 0] for l in ("ar", "ak", "hk")}; absorbed = {l: 0 for l in ("ar", "ak", "hk")}
for k in ORDER:
    e = {"n": {l: (len(U[k][l]) if U[k][l] else 0) for l in ("fa", "ar", "ak", "hk")}}
    for l in ("ar", "ak", "hk"):
        if l not in AL[k]: continue
        sim = Sim(U[k]["fa"], U[k][l], l, dics[l])
        rows = []
        UF, UT = U[k]["fa"], U[k][l]
        cr = (sum(map(len, UT)) or 1) / (sum(map(len, UF)) or 1)
        def lenp(a, b):
            la = sum(len(UF[i]) for i in a); lb = sum(len(UT[j]) for j in b)
            mean = (la + lb / cr) / 2 or 1
            d = (lb / cr - la) / math.sqrt(mean * 6.8)
            return max(2 * (1 - phi(abs(d))), 1e-12)
        merged = absorb(AL[k][l], sim)
        absorbed[l] += len(AL[k][l]) - len(merged)
        AL[k][l] = [(a, b, lenp(a, b) if a and b else 0) for a, b, f in merged]
        for (a, b, p), (_, _, weak) in zip(AL[k][l], merged):
            lex = 0.0; ref = 0
            if a and b:
                tot = sum(max(1, sim.ntok(i)) for i in a)
                lex = min(1.0, sum(sim(i, j) for i in a for j in b) / tot)
                if l == "ak":
                    ra = set().union(*[fa_refs(U[k]["fa"][i]) for i in a]); rb = set().union(*[tr_refs(U[k]["ak"][j]) for j in b])
                    ref = 1 if ra & rb else 0
            c = conf(p, lex, ref, len(a), len(b), l)
            if weak and c == 1: c = 2   # benzerliği olmayan bir cümle katıldıysa en fazla "orta"
            dist[l][c] += 1
            rows.append([a[0] if a else -1, len(a), b[0] if b else -1, len(b), c, round(p, 3), round(lex, 3)])
        e[l] = rows
    exp[k] = e
json.dump(exp, open(OUT, "w"), separators=(",", ":"))
print("yazıldı:", OUT, os.path.getsize(OUT) // 1024, "KB")
print("komşuya katılan karşılıksız grup:", absorbed)
left = {l: sum(1 for k in exp for r in exp[k].get(l, []) if not (r[1] and r[3])) for l in ("ar", "ak", "hk")}
print("hâlâ karşılıksız grup:", left)
for l, d in dist.items():
    s = sum(d[1:]) or 1
    print(f"  {l}: güçlü %{100*d[1]/s:.0f} · orta %{100*d[2]/s:.0f} · zayıf %{100*d[3]/s:.0f}  ({s} grup)")
import align_eval_core as E
G = {k: E.gold(U[k]) for k in ORDER}
for g, l, note in (("ak", "ak", "Kur'ân atıfları (hizalamaya da girdi)"), ("akv", "ak", "beyitler"), ("ar", "ar", "Arapça âyet metinleri")):
    e = n = t = 0
    for k in ORDER:
        if G[k][g] and l in AL[k]:
            x, y = E.score(AL[k][l], G[k][g]); e += x; n += y; t += len(G[k][g])
    print(f"  doğruluk · {note}: tam %{100*e/max(t,1):.1f} · ±1 %{100*n/max(t,1):.1f} ({t} çift)")
print("süre", int(time.time() - t0), "sn")

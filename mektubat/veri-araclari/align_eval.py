"""Hizalama doğruluk testi.

Altın ölçüt (insan eliyle konmuş, hizalamadan bağımsız işaretler):
  FA↔AK: Farsçadaki "[sûre: âyet]" ile Akçiçek'teki "(sûre/âyet)" aynı âyeti gösteriyorsa,
         o Farsça cümle ile o Türkçe cümle birbirinin karşılığıdır.
  FA↔AR: Farsçadaki {âyet} alıntısının ilk 4 kelimesi Arapça tercümede tek bir cümlede geçiyorsa.
Ölçülen: Farsça cümleyi içeren hizalama grubunun hedef tarafında doğru cümle var mı (tam isabet),
ya da bir cümle yakınında mı (±1).
Kullanım: python3 align_eval.py <veri dizini> <yöntem: length|lex|lexref> [çıktı.json]
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import *

D = sys.argv[1]; METHOD = sys.argv[2]; OUT = sys.argv[3] if len(sys.argv) > 3 else None
T = load(D); ORDER = T["index"]["order"]

def gold(k, U):
    G = {"ak": [], "ar": []}
    if U["fa"] and U["ak"]:
        fr = [fa_refs(s) for s in U["fa"]]; tr = [tr_refs(s) for s in U["ak"]]
        # yalnız mektupta tek kez geçen âyetler (belirsizlik olmasın)
        cnt_f = Counter(r for s in fr for r in s); cnt_t = Counter(r for s in tr for r in s)
        for i, s in enumerate(fr):
            for r in s:
                if cnt_f[r] == 1 and cnt_t[r] == 1:
                    j = next(j for j, t in enumerate(tr) if r in t)
                    G["ak"].append((i, j))
    if U["fa"] and U["ar"]:
        arn = [anorm(s) for s in U["ar"]]
        for i, s in enumerate(U["fa"]):
            for q in re.findall(r"\{([^}]{12,})\}", s):
                w = re.findall(r"[ء-ي]+", anorm(q))[:4]
                if len(w) < 4: continue
                pat = re.compile(r"\s+".join(map(re.escape, w)))
                hits = [j for j, t in enumerate(arn) if pat.search(t)]
                if len(hits) == 1: G["ar"].append((i, hits[0]))
    return G

def score(beads, pairs):
    f2b = {}
    for bi, (a, b, p) in enumerate(beads):
        for i in a: f2b[i] = bi
    exact = near = 0
    for i, j in pairs:
        bi = f2b.get(i)
        if bi is None: continue
        b = beads[bi][1]
        if j in b: exact += 1; near += 1
        elif b and min(abs(j - x) for x in b) <= 1: near += 1
    return exact, near

t0 = time.time()
U = {k: {l: units(T, k, l) for l in ("fa", "ar", "ak", "hk")} for k in ORDER}
GOLD = {k: gold(k, U[k]) for k in ORDER}
print("altın eşleşme sayısı: AK", sum(len(g["ak"]) for g in GOLD.values()), "| AR", sum(len(g["ar"]) for g in GOLD.values()), flush=True)

def run(sims=None, use_ref=False):
    AL = {}
    for k in ORDER:
        AL[k] = {"U": U[k]}
        for l in ("ar", "ak", "hk"):
            if not (U[k]["fa"] and U[k][l]): continue
            sim = sims(k, l) if sims else None
            ra = rb = None
            if use_ref and l == "ak":
                ra = [fa_refs(s) for s in U[k]["fa"]]; rb = [tr_refs(s) for s in U[k]["ak"]]
            AL[k][l] = align(U[k]["fa"], U[k][l], sim, ra, rb)
    return AL

def report(AL, name):
    for l in ("ak", "ar"):
        pairs = [(k, p) for k in ORDER for p in GOLD[k][l]]
        e = n = 0
        for k in ORDER:
            if l in AL[k]:
                a, b = score(AL[k][l], GOLD[k][l]); e += a; n += b
        tot = len(pairs)
        print(f"  [{name}] FA↔{l.upper()}: tam isabet {e}/{tot} = %{100*e/max(tot,1):.1f} · ±1 cümle %{100*n/max(tot,1):.1f}", flush=True)

AL = run()
report(AL, "uzunluk")
if METHOD in ("lex", "lexref"):
    for it in (1, 2):
        dics = {l: learn_dict(T, AL, l) for l in ("ar", "ak", "hk")}
        print(f"  sözlük {it}: " + ", ".join(f"{l}={len(d)}" for l, d in dics.items()), flush=True)
        AL = run(lambda k, l: Sim(U[k]["fa"], U[k][l], l, dics[l]), use_ref=(METHOD == "lexref"))
        report(AL, f"uzunluk+sözcük{'+atıf' if METHOD=='lexref' else ''} #{it}")
print(f"süre {time.time()-t0:.0f} sn")
if OUT:
    exp = {}
    for k in ORDER:
        exp[k] = {"n": {l: (len(U[k][l]) if U[k][l] else 0) for l in ("fa", "ar", "ak", "hk")}}
        for l in ("ar", "ak", "hk"):
            if l in AL[k]:
                exp[k][l] = [[a[0] if a else -1, len(a), b[0] if b else -1, len(b), round(p, 3)] for a, b, p in AL[k][l]]
    json.dump(exp, open(OUT, "w"), separators=(",", ":"))
    print("yazıldı:", OUT)

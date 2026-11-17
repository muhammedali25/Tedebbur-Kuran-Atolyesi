"""align_eval.py ve align_tune.py için ortak: altın çiftler ve puanlama."""
import re
from collections import Counter
from align_lib import load, units, fa_refs, tr_refs, anorm

def gold(U):
    G = {"ak": [], "ar": []}
    if U["fa"] and U["ak"]:
        fr = [fa_refs(s) for s in U["fa"]]; tr = [tr_refs(s) for s in U["ak"]]
        cf = Counter(r for s in fr for r in s); ct = Counter(r for s in tr for r in s)
        for i, s in enumerate(fr):
            for r in s:
                if cf[r] == 1 and ct[r] == 1:
                    G["ak"].append((i, next(j for j, t in enumerate(tr) if r in t)))
    # Akçiçek'in aynen aktardığı Farsça beyitler: Türkçe sözcük eşleşmesi bunları görmez (bağımsız ölçüt)
    G["akv"] = []
    if U["fa"] and U["ak"]:
        letters = lambda s: re.sub(r"[^ء-يٱ-ۓ]", "", anorm(s))
        fl = [letters(s) for s in U["fa"]]
        for j, s in enumerate(U["ak"]):
            L = letters(s)
            if len(L) < 16 or re.search(r"[a-zA-ZçğıöşüÇĞİÖŞÜ]{4}", s): continue
            probe = L[2:16]
            hits = [i for i, f in enumerate(fl) if probe in f]
            if len(hits) == 1: G["akv"].append((hits[0], j))
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
    for bi, bd in enumerate(beads):
        for i in bd[0]: f2b[i] = bi
    exact = near = 0
    for i, j in pairs:
        bi = f2b.get(i)
        if bi is None: continue
        b = beads[bi][1]
        if j in b: exact += 1; near += 1
        elif b and min(abs(j - x) for x in b) <= 1: near += 1
    return exact, near

def setup(D):
    T = load(D); ORDER = T["index"]["order"]
    U = {k: {l: units(T, k, l) for l in ("fa", "ar", "ak", "hk")} for k in ORDER}
    return T, U, {k: gold(U[k]) for k in ORDER}, ORDER

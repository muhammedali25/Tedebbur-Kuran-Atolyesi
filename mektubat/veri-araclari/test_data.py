"""Veri testleri. Her test GEÇTİ / UYARI / KALDI yazar ve ayrıntıyı döker.
Kullanım: python3 -I test_data.py /home/user/mektubat/data
"""
import json, os, re, sys, math
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import anorm, tnorm, fa_refs, tr_refs, units, load, SURAS

D = sys.argv[1]
T = load(D); IDX = T["index"]; ORDER = IDX["order"]; MAP = IDX["map"]
P = json.load(open(D + "/people.json")); AT = json.load(open(D + "/atlas.json"))
Q = json.load(open(D + "/quran.json")); V = json.load(open(D + "/verses.json")); W = json.load(open(D + "/widget.json"))
SP = json.load(open(D + "/spectrum.json"))
results = []
def res(name, status, detail=""):
    results.append((status, name)); print(f"[{status}] {name}" + (f"\n        {detail}" if detail else ""))

# 1. bütünlük -----------------------------------------------------------
vols = Counter(k.split("-")[0] for k in ORDER)
res("Farsça mektup sayısı 313/99/124", "GEÇTİ" if (vols["1"], vols["2"], vols["3"]) == (313, 99, 124) else "KALDI", str(dict(vols)))
res("Arapça 534, Akçiçek 534, Hakikat 313", "GEÇTİ" if (len(T["ar"]), len(T["ak"]), len(T["hk"])) == (534, 534, 313) else "KALDI",
    f"{len(T['ar'])}/{len(T['ak'])}/{len(T['hk'])}")
empty = [(l, k) for l in ("fa", "ar", "ak", "hk") for k, L in T[l].items() if sum(len(x) for x in L["p"]) < 80]
res("Boş ya da çok kısa metin yok", "GEÇTİ" if not empty else "UYARI", str(empty[:15]))
junk = []
for l in ("fa", "ar", "ak", "hk"):
    for k, L in T[l].items():
        t = L.get("t", "") + "\n".join(L["p"])
        for pat, why in [(r"&[a-z]+;|&#\d+;", "HTML varlığı"), (r"<[a-zA-Z/][^>]{0,40}>", "HTML etiketi"), ("�", "bozuk karakter"), (r"Gece Modu|Tarayıcınız ses", "site artığı")]:
            if re.search(pat, t): junk.append((l, k, why))
res("Metinlerde HTML/site artığı yok", "GEÇTİ" if not junk else "KALDI", str(junk[:15]))
for l in ("fa", "ar", "ak", "hk"):
    h = Counter(hash("\n".join(L["p"])) for L in T[l].values())
    dup = [k for k, L in T[l].items() if h[hash("\n".join(L["p"]))] > 1]
    res(f"{l}: aynı metin iki mektupta yok", "GEÇTİ" if not dup else "KALDI", str(dup[:10]))
bad_map = [k for k in ORDER if (MAP[k].get("ar") and MAP[k]["ar"].replace("/", "-") not in T["ar"] and False)]
miss = [k for k in ORDER if (k in T["ar"]) != bool(MAP[k].get("ar")) or (k in T["ak"]) != bool(MAP[k].get("ak")) or (k in T["hk"]) != bool(MAP[k].get("hk"))]
res("Dizin eşlemesi metinlerle tutarlı", "GEÇTİ" if not miss else "KALDI", str(miss[:10]))
nomatch = [k for k in ORDER if k not in T["ar"]]
res("Arapçada olmayan mektuplar yalnız 3/115 ve 3/124", "GEÇTİ" if nomatch == ["3-115", "3-124"] else "KALDI", str(nomatch))

# 2. mektup eşleştirmesi: âyet atıflarıyla çapraz kontrol ------------------
def refs_of(l, k):
    L = T[l].get(k)
    if not L: return set()
    t = "\n".join(L["p"])
    return fa_refs(t) if l == "fa" else tr_refs(t)
both = agree = 0; disagree = []
for k in ORDER:
    a, b = refs_of("fa", k), refs_of("ak", k)
    if len(a) >= 2 and len(b) >= 2:
        both += 1
        j = len(a & b) / len(a | b)
        if j >= 0.3: agree += 1
        else: disagree.append((k, round(j, 2), sorted(a)[:3], sorted(b)[:3]))
shift = sum(1 for i, k in enumerate(ORDER[:-1]) if len(refs_of("fa", k)) >= 2 and len(refs_of("ak", ORDER[i + 1])) >= 2 and len(refs_of("fa", k) & refs_of("ak", ORDER[i + 1])) / len(refs_of("fa", k) | refs_of("ak", ORDER[i + 1])) >= 0.3)
res(f"FA↔AK mektup eşlemesi âyetlerle tutarlı ({agree}/{both}; bir kaydırınca {shift})", "GEÇTİ" if agree >= 0.85 * both else "UYARI", "uyuşmayanlar: " + str(disagree[:8]))
fq = 0; fqhit = 0; fqmiss = []
for k in ORDER:
    if k not in T["ar"]: continue
    arn = anorm("\n".join(T["ar"][k]["p"]))
    for q in re.findall(r"\{([^}]{12,})\}", "\n".join(T["fa"][k]["p"])):
        w = re.findall(r"[ء-ي]+", anorm(q))[:4]
        if len(w) < 4: continue
        fq += 1
        if re.search(r"\s+".join(map(re.escape, w)), arn): fqhit += 1
        else: fqmiss.append(k)
res(f"FA'daki âyet alıntıları aynı numaralı Arapça mektupta bulunuyor (%{100*fqhit/max(fq,1):.1f}, {fqhit}/{fq})", "GEÇTİ" if fqhit >= 0.8 * fq else "UYARI", "bulunmayanların geçtiği mektuplar: " + str(Counter(fqmiss).most_common(8)))

# 3. alıcılar ------------------------------------------------------------
def fold(s): return re.sub(r"[^a-z ]", "", tnorm(s).translate(str.maketrans("çğıöşü", "cgiosu")))
STOPN = set("hace mevlana mevlâna molla seyh seyyid mir mirza hazret hz hazreti ogul oglu kardesi seyhi seyhin bin b han".split())
ok = tot = 0; mism = []
pid = {p["id"]: p for p in P["people"]}
for k in ORDER:
    note = (T["ak"].get(k) or {}).get("not") or ""
    if not note or not P["by"].get(k): continue
    nf = fold(note)
    for i in P["by"][k]:
        p = pid[i]
        if p.get("auto"): continue
        toks = [t for t in fold(re.sub(r"\(.*?\)", "", p["tr"])).split() if len(t) >= 4 and t not in STOPN]
        if not toks: continue
        tot += 1
        if any(t[:5] in nf for t in toks): ok += 1
        else: mism.append((k, p["tr"], note[30:110]))
res(f"Alıcı (Farsça başlıktan) Akçiçek notuyla uyuşuyor: {ok}/{tot}", "GEÇTİ" if ok >= 0.9 * tot else "UYARI", "\n        ".join(f"{a} | {b} | {c}" for a, b, c in mism[:40]))
nob = [k for k in ORDER if not P["by"].get(k)]
res("Her mektubun en az bir alıcısı var", "GEÇTİ" if not nob else "UYARI", str(nob))

# 4. Kur'ân atıfları -----------------------------------------------------
AYAH = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
res("Âyet sayısı tablosu doğru (114 sûre, toplam 6236)", "GEÇTİ" if len(AYAH) == 114 and sum(AYAH) == 6236 else "KALDI", f"{len(AYAH)} sûre, {sum(AYAH)} âyet")
inval = [(r[0], SURAS[r[1]-1], r[2]) for r in Q["refs"] if not (1 <= r[2] <= AYAH[r[1]-1] and r[2] <= r[3] <= AYAH[r[1]-1])]
res(f"Bütün âyet numaraları sûrenin âyet sayısı içinde ({len(Q['refs'])} atıf)", "GEÇTİ" if not inval else "KALDI", str(inval[:15]))
noq = [r for r in Q["refs"] if len(r[4]) < 5]
res("Her atfın bir alıntı metni var", "GEÇTİ" if len(noq) < 0.03 * len(Q["refs"]) else "UYARI", f"{len(noq)} atıf alıntısız: " + str([(r[0], r[1], r[2]) for r in noq[:8]]))
# ham metinle say (tr_refs geçersizleri zaten eler; onu kullanmak testi kendini doğrulayan yapar)
raw = [(k, int(m.group(1)), int(m.group(2))) for k in T["ak"] for m in re.finditer(r"\((\d{1,3})\s*/\s*(\d{1,3})\)", "\n".join(T["ak"][k]["p"]))]
trinv = [x for x in raw if not (1 <= x[1] <= 114 and 1 <= x[2] <= AYAH[x[1]-1])]
res(f"Akçiçek'teki (sûre/âyet) atıfları geçerli ({len(raw)-len(trinv)}/{len(raw)}; geçersizler kaynaktaki yazım hatası, hizalamada kullanılmaz)",
    "GEÇTİ" if not trinv else "UYARI", str(trinv[:10]))

# 5. beyitler --------------------------------------------------------------
found = 0; nf = []
for v in V:
    # boşluktan bağımsız: Akçiçek "درافکنده", baskı "در افکنده" yazabiliyor
    letters = re.sub(r"[^ء-يٱ-ۓ]", "", anorm(v["fa"]))
    fa = re.sub(r"[^ء-يٱ-ۓ]", "", anorm(T["fa"][v["k"]]["t"] + "\n" + "\n".join(T["fa"][v["k"]]["p"])))
    probes = [letters[i:i + 12] for i in range(0, max(1, len(letters) - 12), 6)][:4]
    if probes and sum(1 for q in probes if q in fa) >= max(1, len(probes) // 2): found += 1
    else: nf.append((v["k"], v["fa"][:40]))
res(f"Beyitler Farsça asılda aynı mektupta bulunuyor: {found}/{len(V)}", "GEÇTİ" if found >= 0.85 * len(V) else "UYARI", str(nf[:12]))
nomeal = sum(1 for v in V if not v["meal"])
res(f"Beyitlerin meali var ({len(V)-nomeal}/{len(V)})", "GEÇTİ" if nomeal < 0.1 * len(V) else "UYARI")

# 6. atlas kalıpları ---------------------------------------------------------
by = {t["id"]: t for t in AT["terms"]}
CASES = [("fena", "و از فناء خاص", True), ("fena", "بفنا رسيد", True), ("fena", "فنائي", False),
         ("zill", "ظل و اصل", True), ("zill", "ظلمت شب", False), ("zill", "ظلال اسما", True),
         ("nefs", "نفس اماره", True), ("nefs", "نفسي", True), ("nefs", "انفس", False),
         ("kalb", "قلب سليم", True), ("kalb", "منقلب", False), ("zikir", "ذكر خفي", True), ("zikir", "مذكور", False),
         ("kurb", "قرب نوافل", True), ("kurb", "اقرب", False), ("sunnet", "سنت سنيه", True), ("namaz", "عليه الصلاه والسلام", False),
         ("namaz", "اداي نماز", True), ("s_imkan", "دايره امكان", True), ("s_kabe", "حقيقت كعبه", True), ("s_lataayyun", "مرتبه لا تعين", True)]
fails = []
for tid, s, exp in CASES:
    got = bool(re.search(by[tid]["rxfa"], anorm(s)))
    if got != exp: fails.append((tid, s, exp, got))
res(f"Atlas kalıp birim testleri ({len(CASES)-len(fails)}/{len(CASES)})", "GEÇTİ" if not fails else "KALDI", str(fails))
low = []
for t in AT["terms"]:
    f, a = AT["counts"][t["id"]]["fa"], AT["counts"][t["id"]]["ar"]
    if sum(f) < 15: continue
    n = len(f); mf, ma = sum(f)/n, sum(a)/n
    sf = math.sqrt(sum((x-mf)**2 for x in f)); sa = math.sqrt(sum((x-ma)**2 for x in a))
    r = sum((x-mf)*(y-ma) for x, y in zip(f, a))/(sf*sa) if sf and sa else 0
    if r < 0.8: low.append((t["tr"], round(r, 2)))
res("Atlas: Farsça ve Arapça sayımlar mektup bazında uyumlu (r ≥ 0,80)", "GEÇTİ" if not low else "UYARI", "düşük olanlar: " + str(low))

# 7. günün cümlesi, tayf --------------------------------------------------
badw = [w["k"] for w in W if w["k"] not in T["fa"] or not w["fa"] or not w["tr"]]
res(f"Günün cümlesi kayıtları geçerli ({len(W)})", "GEÇTİ" if not badw and len(W) > 300 else "KALDI", str(badw[:5]))
selfhit = []
for t in SP["terms"]:
    rows = SP["data"][t["id"]]["ak"]["rows"]
    head = fold(t["tr"].split()[0])[:4]
    if not any(fold(r["w"])[:4] == head for r in rows[:3]): selfhit.append((t["tr"], [r["w"] for r in rows[:3]]))
res("Tayf: her kavramın ilk 3 Akçiçek karşılığında kendi adı (ya da Türkçesi) var", "GEÇTİ" if len(selfhit) <= 6 else "UYARI", str(selfhit))

print("\nÖZET:", Counter(s for s, _ in results))

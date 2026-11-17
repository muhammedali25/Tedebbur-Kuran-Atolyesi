"""Yeni görünümlerin verisini üretir: Kur'ân atıfları, beyit divanı, seyr daireleri,
tercüme tayfı ve ana ekran bileşeni için günün cümlesi.

Cümle bölme ve hizalama, okuyucudaki JavaScript ile aynı kurallarla yapılır (Gale–Church,
yalnız uzunluklara dayalı; sonuçlar yaklaşıktır).
"""
import json, re, math, sys
from collections import Counter, defaultdict

D = sys.argv[1] if len(sys.argv) > 1 else "/home/user/mektubat/data"
F = json.load(open(D + "/fa.json"))["L"]
AR = json.load(open(D + "/ar.json"))["L"]
AK = json.load(open(D + "/ak.json"))["L"]
HK = json.load(open(D + "/hk.json"))["L"]
IDX = json.load(open(D + "/index.json"))
PEOPLE = json.load(open(D + "/people.json"))
ORDER = IDX["order"]

DROP = re.compile(r"[ً-ٰٟـۖ-ۭؐ-ؚ‌‏‎]")
AMAP = str.maketrans({"ی": "ي", "ى": "ي", "ئ": "ي", "ک": "ك", "ة": "ه", "ۀ": "ه", "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ؤ": "و"})
def anorm(s): return DROP.sub("", s).translate(AMAP)
def tnorm(s): return s.replace("İ", "i").replace("I", "ı").lower().translate(str.maketrans("âîûÂÎÛ", "aiuaiu"))

# ---------------------------------------------------------------- Kur'ân atıfları
SURAS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]
SURA_TR = ["Fâtiha","Bakara","Âl-i İmrân","Nisâ","Mâide","En'âm","A'râf","Enfâl","Tevbe","Yûnus","Hûd","Yûsuf","Ra'd","İbrâhîm","Hicr","Nahl","İsrâ","Kehf","Meryem","Tâhâ","Enbiyâ","Hac","Mü'minûn","Nûr","Furkân","Şuarâ","Neml","Kasas","Ankebût","Rûm","Lokmân","Secde","Ahzâb","Sebe'","Fâtır","Yâsîn","Sâffât","Sâd","Zümer","Mü'min","Fussılet","Şûrâ","Zuhruf","Duhân","Câsiye","Ahkâf","Muhammed","Fetih","Hucurât","Kâf","Zâriyât","Tûr","Necm","Kamer","Rahmân","Vâkıa","Hadîd","Mücâdele","Haşr","Mümtehine","Saf","Cuma","Münâfikûn","Teğâbün","Talâk","Tahrîm","Mülk","Kalem","Hâkka","Meâric","Nûh","Cin","Müzzemmil","Müddessir","Kıyâme","İnsân","Mürselât","Nebe'","Nâziât","Abese","Tekvîr","İnfitâr","Mutaffifîn","İnşikâk","Bürûc","Târık","A'lâ","Gâşiye","Fecr","Beled","Şems","Leyl","Duhâ","İnşirâh","Tîn","Alak","Kadir","Beyyine","Zilzâl","Âdiyât","Kâria","Tekâsür","Asr","Hümeze","Fîl","Kureyş","Mâûn","Kevser","Kâfirûn","Nasr","Tebbet","İhlâs","Felak","Nâs"]
AYAH = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
def valid(s, a): return 1 <= s <= 114 and 1 <= a <= AYAH[s - 1]
def skey(s): return re.sub(r"^ال", "", anorm(s).replace(" ", "").rstrip("،,"))
SK = {skey(s): i + 1 for i, s in enumerate(SURAS)}
SK.update({skey("الإسرا"): 17, skey("آل عمراه"): 3})
refs = []; miss = Counter()
REF = re.compile(r"\[\s*([^\]\[:\d]{1,30}?)\s*(?::|آيات|آية)?\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*\]")
for k in ORDER:
    paras = F[k]["p"]
    for pi, t in enumerate(paras):
        for m in REF.finditer(t):
            s = SK.get(skey(m.group(1)))
            if not s: miss[m.group(1)] += 1; continue
            a1 = int(m.group(2)); a2 = int(m.group(3) or a1)
            if not valid(s, a1): miss[m.group(0)] += 1; continue  # ör. [ص: 148] sayfa göndermesidir, âyet değil
            if not valid(s, a2): a2 = a1
            before = t[:m.start()]
            j = before.rfind("{")
            quote = before[j + 1:].strip().rstrip("}").strip() if j != -1 and m.start() - j < 600 else before[-120:].strip()
            refs.append([k, s, a1, a2, quote[:220]])
json.dump({"suras": SURA_TR, "surasAr": SURAS, "refs": refs}, open(D + "/quran.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("Kur'ân atfı:", len(refs), "| sûre:", len(set(r[1] for r in refs)), "| eşleşmeyen ad:", dict(miss))

# ---------------------------------------------------------------- beyit divanı
verses = []
for k in ORDER:
    L = AK.get(k)
    if not L: continue
    p = L["p"]
    for i, x in enumerate(p):
        if not x.startswith("§vf§"): continue
        ok = p[i + 1][4:] if i + 1 < len(p) and p[i + 1].startswith("§vl§") else ""
        j = i + (2 if ok else 1)
        meal = p[j][4:] if j < len(p) and p[j].startswith("§vm§") else ""
        # Beyit Farsça asılda (Amritsar) bu mektupta geçiyor mu? Boşluktan bağımsız denetim.
        lt = re.sub(r"[^ء-يٱ-ۓ]", "", anorm(x[4:]))
        fa_l = re.sub(r"[^ء-يٱ-ۓ]", "", anorm(F[k]["t"] + "\n" + "\n".join(F[k]["p"])))
        probes = [lt[i:i + 12] for i in range(0, max(1, len(lt) - 12), 6)][:4]
        infa = bool(probes) and sum(1 for q in probes if q in fa_l) >= max(1, len(probes) // 2)
        verses.append({"k": k, "fa": x[4:], "ok": ok, "meal": meal, "asil": infa})
json.dump(verses, open(D + "/verses.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("beyit:", len(verses))

# ---------------------------------------------------------------- seyr daireleri (atlasa eklenir)
L_ = r"[ء-يٱ-ۓ]"
def rx(core):
    return "(?<!" + L_ + ")(?:و|ب)?(?:ال)?(?:" + core + ")(?:ه|ي|ها|هاي|ات|يه|يت)?(?!" + L_ + ")"
STATIONS = [
    ("s_imkan", "Dâire-i imkân", r"دايره (?:ال)?امكان", r"دايره (?:ال)?امكان", "Mümkinlerin, yaratılmışların dairesi"),
    ("s_zilal", "Zılâl-i esmâ", r"دايره ظلال|ظلال (?:ال)?اسما", r"دايره (?:ال)?ظلال|ظلال (?:ال)?اسماء?", "İsim ve sıfatların gölgeleri dairesi"),
    ("s_sugra", "Velâyet-i suğrâ", r"ولايت صغري", r"(?:ال)?ولايه (?:ال)?صغري", "Evliyânın velâyeti"),
    ("s_kubra", "Velâyet-i kübrâ", r"ولايت كبري", r"(?:ال)?ولايه (?:ال)?كبري", "Peygamberlerin velâyeti"),
    ("s_ulya", "Velâyet-i ulyâ", r"ولايت عليا|ولايت ملا اعلي", r"(?:ال)?ولايه (?:ال)?عليا|ولايه (?:ال)?ملا (?:ال)?اعلي", "Melâ-i a'lânın velâyeti"),
    ("s_nubuvvet", "Kemâlât-ı nübüvvet", r"كمالات نبوت", r"كمالات (?:ال)?نبوه", "Peygamberliğin kemâlâtı"),
    ("s_kabe", "Hakîkat-i Kâ'be", r"حقيقت كعبه", r"حقيقه (?:ال)?كعبه", "Kâ'benin hakikati"),
    ("s_kuran", "Hakîkat-i Kur'ân", r"حقيقت قران", r"حقيقه (?:ال)?قران", "Kur'ân'ın hakikati"),
    ("s_mabudiyet", "Ma'bûdiyyet", r"معبوديت", r"معبوديه", "Mabud oluş makamı"),
    ("s_ibrahimi", "Hakîkat-i İbrâhîmî", r"حقيقت ابراهيمي", r"حقيقه (?:ال)?ابراهيميه", "Hz. İbrâhim'in hakikati"),
    ("s_muhammedi", "Hakîkat-i Muhammedî", r"حقيقت محمدي", r"حقيقه (?:ال)?محمديه", "Hz. Muhammed'in hakikati"),
    ("s_ahmedi", "Hakîkat-i Ahmedî", r"حقيقت احمدي", r"حقيقه (?:ال)?احمديه", "Ahmedî hakikat"),
    ("s_lataayyun", "Lâ ta'ayyün", r"لا تعين", r"(?:ال)?لا ?تعين", "Belirlenmemişlik, taayyünsüzlük"),
]
atlas = json.load(open(D + "/atlas.json"))
atlas["terms"] = [t for t in atlas["terms"] if not t["id"].startswith("s_")]
fa_n = {k: anorm(F[k]["t"] + "\n" + "\n".join(F[k]["p"])) for k in ORDER}
ar_n = {k: anorm(AR[k]["t"] + "\n" + "\n".join(AR[k]["p"])) for k in ORDER if k in AR}
for sid, tr, fa, ar, desc in STATIONS:
    rf, ra = re.compile(rx(fa)), re.compile(rx(ar))
    cf = [len(rf.findall(fa_n[k])) for k in ORDER]; ca = [len(ra.findall(ar_n[k])) if k in ar_n else 0 for k in ORDER]
    atlas["terms"].append({"id": sid, "tr": tr, "desc": desc, "fa": fa, "ar": ar, "rxfa": rx(fa), "rxar": rx(ar),
                           "tfa": sum(cf), "tar": sum(ca), "group": "seyr"})
    atlas["counts"][sid] = {"fa": cf, "ar": ca}
    print(f"  {tr:22} FA {sum(cf):3}  AR {sum(ca):3}  mektup {sum(1 for x in cf if x)}")
json.dump(atlas, open(D + "/atlas.json", "w"), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- hizalama: build_align.py çıktısı
import os as _os
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import align_lib as _al
_T = _al.load(D); _AJ = json.load(open(D + "/align.json"))
ALIGN = {}
for k in ORDER:
    U = {l: _al.units(_T, k, l) for l in ("fa", "ar", "ak", "hk")}
    ALIGN[k] = {"U": U}
    for l in ("ar", "ak", "hk"):
        if l in _AJ[k]:
            assert _AJ[k]["n"][l] == len(U[l]) and _AJ[k]["n"]["fa"] == len(U["fa"]), f"cümle sayısı uyuşmuyor: {k}/{l}"
            ALIGN[k][l] = [(list(range(a0, a0 + na)) if na else [], list(range(b0, b0 + nb)) if nb else [], p, c)
                           for a0, na, b0, nb, c, p, lx in _AJ[k][l]]

# ---------------------------------------------------------------- tercüme tayfı
STOP_TR = set("ve ile bir bu şu o da de ki ise için gibi daha çok en ne her hem ya veya ama fakat çünkü olan olarak olur oldu olduğu olduğunu olduğundan olması olmak etmek eder etti edilen yani hiç kendi kendisi onun onu ona ondan bunun buna bundan onlar bunlar biz siz ben sen size bize bana sana mı mi mu mü değil var yok kadar sonra önce böyle şöyle diye dahi bile artık işte yine üzere sıra ancak lakin şey şeyi şeyin bütün tüm".split())
def tr_tokens(s):
    w = [x for x in re.findall(r"[a-zçğıöşü]+", tnorm(s)) if len(x) > 2 and x not in STOP_TR]
    st = [x[:6] if len(x) > 6 else x for x in w]
    return w, st
def ar_tokens(s):
    w = [re.sub(r"^(?:و|ف|ب|ل|ك)?(?:ال)?", "", x) for x in re.findall(r"[ء-يٱ-ۓ]+", anorm(s))]
    w = [x for x in w if len(x) > 2]
    return w, w
spectrum = {"terms": [], "data": {}}
TERMS = [t for t in atlas["terms"] if not t.get("group")]
for t in TERMS:
    rf = re.compile(t["rxfa"])
    entry = {}
    for l in ("ak", "hk", "ar"):
        tok = tr_tokens if l in ("ak", "hk") else ar_tokens
        c_t = 0; c_w = Counter(); c_tw = Counter(); surf = defaultdict(Counter); ex = {}
        for k in ORDER:
            A = ALIGN[k]
            if l not in A: continue
            U = A["U"]
            for a, b, p, cf in A[l]:
                if not a or not b: continue
                fa_txt = " ".join(U["fa"][i] for i in a); tg_txt = " ".join(U[l][j] for j in b)
                pos = bool(rf.search(anorm(fa_txt)))
                words, stems = tok(tg_txt)
                keys = set(stems) | {stems[i] + " " + stems[i + 1] for i in range(len(stems) - 1)}
                for w_, s_ in zip(words, stems): surf[s_][w_] += 1
                for i in range(len(stems) - 1): surf[stems[i] + " " + stems[i + 1]][words[i] + " " + words[i + 1]] += 1
                for kk in keys: c_w[kk] += 1
                if pos:
                    c_t += 1
                    for kk in keys:
                        c_tw[kk] += 1
                        if kk not in ex and cf == 1 and len(tg_txt) < 260 and len(fa_txt) < 320:
                            ex[kk] = [k, fa_txt.strip(), tg_txt.strip()]
        rows = []
        for kk, j in c_tw.items():
            if j < 3: continue
            dice = 2 * j / (c_w[kk] + c_t)
            rows.append((dice, j, kk))
        rows.sort(reverse=True)
        # aynı kökün tek ve ikili biçimi üst üste gelmesin
        out = []; seen = set()
        for dice, j, kk in rows:
            parts = set(kk.split())
            if parts & seen and " " in kk: continue
            if kk in seen: continue
            out.append({"w": surf[kk].most_common(1)[0][0], "n": j, "share": round(j / max(c_t, 1), 3), "dice": round(dice, 3), "ex": ex.get(kk)})
            seen |= parts
            if len(out) >= 8: break
        entry[l] = {"beads": c_t, "rows": out}
    spectrum["terms"].append({"id": t["id"], "tr": t["tr"], "fa": t["fa"]})
    spectrum["data"][t["id"]] = entry
    print("  tayf", t["tr"], "| AK:", ", ".join(r["w"] for r in entry["ak"]["rows"][:4]))
json.dump(spectrum, open(D + "/spectrum.json", "w"), ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- günün cümlesi (ana ekran bileşeni)
pname = {p["id"]: p["tr"] for p in PEOPLE["people"]}
widget = []
for k in ORDER:
    A = ALIGN[k]
    if "ak" not in A: continue
    U = A["U"]; best = None
    arb = A.get("ar") or []
    for a, b, p, cf in A["ak"]:
        if not a or not b or cf != 1: continue
        fa = " ".join(U["fa"][i] for i in a).strip(); tr = " ".join(U["ak"][j] for j in b).strip()
        if not (50 <= len(tr) <= 200 and 30 <= len(fa) <= 240): continue
        score = -abs(len(tr) - 120) / 400
        if not best or score > best[0]:
            ar_ids = sorted({j for aa, bb, pp, cc in arb if set(aa) & set(a) and cc <= 2 for j in bb})
            ar = " ".join(U["ar"][j] for j in ar_ids).strip() if U.get("ar") else ""
            best = (score, fa, tr, ar if len(ar) < 320 else "")
    if best:
        who = ", ".join(re.sub(r"\s*\([^)]*\)$", "", pname[i]) for i in PEOPLE["by"].get(k, []))
        widget.append({"k": k, "fa": best[1], "tr": best[2], "ar": best[3], "who": who})
json.dump(widget, open(D + "/widget.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("günün cümlesi:", len(widget))

"""Cümle bölme ve cümle hizalama.

İki yöntem:
- length: Gale–Church, yalnız cümle uzunlukları (okuyucunun ilk sürümü).
- lex: uzunluk + sözcük benzerliği. Sözcük benzerliği, önce uzunlukla yapılan hizalamadan
  öğrenilen bir Farsça→hedef sözlükten gelir (Hunalign yaklaşımı). Farsça↔Arapça için ortak
  sözcükler (Arapça kökenli kelimeler, âyet ve hadis alıntıları) ayrıca doğrudan eşleşir.
- anchors: Akçiçek'teki "(sûre/âyet)" atıfları ile Farsçadaki "[sûre: âyet]" atıfları
  kesin eşleşme noktası olarak kullanılır.
"""
import json, re, math
from collections import Counter, defaultdict

DROP = re.compile(r"[ً-ٰٟـۖ-ۭؐ-ؚ‌‏‎]")
AMAP = str.maketrans({"ی": "ي", "ى": "ي", "ئ": "ي", "ک": "ك", "ة": "ه", "ۀ": "ه", "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ؤ": "و"})
def anorm(s): return DROP.sub("", s).translate(AMAP)
def tnorm(s): return s.replace("İ", "i").replace("I", "ı").lower().translate(str.maketrans("âîûÂÎÛ", "aiuaiu"))

def load(D):
    G = lambda n: json.load(open(f"{D}/{n}.json"))
    return {"fa": G("fa")["L"], "ar": G("ar")["L"], "ak": G("ak")["L"], "hk": G("hk")["L"], "index": G("index")}

# ------------------------------------------------------------------ cümle bölme (JS ile birebir aynı)
ABBR = re.compile(r"(?:^|[\s(])(?:Hz|s\.a\.v|s\.a|a\.s|r\.a|k\.s|rh\.a|b|bkz|vb|vs|Dr|Mev|Hâc|Şeyh|[A-ZÇĞİÖŞÜ])\.$")
def split(text, lang):
    out = []
    if lang in ("fa", "ar"):
        out = [m.group(0) for m in re.finditer(r"[^.!?؟]+(?:[.!?؟]+[\"»”)\]}]*|$)", text) if m.group(0).strip()]
    else:
        buf = ""
        for m in re.finditer(r"[^.!?…]+(?:[.!?…]+[\"”’»)\]]*|$)", text):
            s = m.group(0)
            if not s: continue
            nxt = text[m.end():].lstrip()[:1]
            buf += s
            rest = text[m.end():].lstrip()
            # "(59/22)" gibi âyet atfı, önündeki meal cümlesine aittir
            if ABBR.search(buf.rstrip()) or (nxt and re.match(r"[a-zçğıöşüâîû0-9]", nxt)) or re.match(r"\(\s*\d{1,3}\s*/\s*\d{1,3}", rest): continue
            if buf.strip(): out.append(buf)
            buf = ""
        if buf.strip(): out.append(buf)
    if lang in ("fa", "ar"):
        out = refine(out, 200 if lang == "ar" else 280)
    merged = []
    for s in out:
        if merged and len(s.strip()) < 6: merged[-1] += s
        else: merged.append(s)
    return merged

def greedy(s, pat, lim):
    """s'yi pat noktalarından böl, parçaları en az lim*0,55 uzunlukta toplayarak birleştir."""
    fine = []; cur = ""
    for p in re.split(pat, s):
        cur += (" " if cur else "") + p
        if len(cur) >= lim * 0.55: fine.append(cur + " "); cur = ""
    if cur:
        if fine and len(cur) < 40: fine[-1] += cur
        else: fine.append(cur)
    return fine

def refine(units_, lim):
    """Farsça ve Arapçada nokta seyrek: uzun cümleleri önce noktalama, sonra "و" bağlacından böl."""
    out = []
    for s in units_:
        if len(s) <= lim: out.append(s); continue
        for q in greedy(s, r"(?<=[،؛:,])\s+", lim):
            if len(q) > 2 * lim: out += greedy(q, r"\s+(?=و\S)", lim)
            else: out.append(q)
    return out

HK_HEAD = re.compile(r"^[\"“”\s]*Bu mekt[uû][bp]")
FA_HINT = re.compile(r"(?<![؀-ۿ])(است|كه|که|را|اين|آن|مى|مي|نمى|شد|بود)(?![؀-ۿ])")
def is_persian(x): return bool(re.search(r"[پچژگ]", x)) or len(FA_HINT.findall(x)) >= 2

def fa_skip(body):
    """Amritsar baskısında Arapça pasajlardan sonra gelen "[ترجمه از مصحح]" paragrafı ve ardındaki
    Farsça tercüme, musahhihin eklemesidir; İmâm-ı Rabbânî'nin metni değildir: hizalamaya girmez."""
    skip = set()
    for i, x in enumerate(body):
        if x.strip().startswith("[ترجمه"):
            skip.add(i)
            if i + 1 < len(body) and is_persian(body[i + 1]): skip.add(i + 1)
    return skip

def fa_has_subtitle(L):
    # Başlık iki satır: "مکتوب اول" + konusu. Konu satırı uzunsa (≥300) gövde ile birleşik yazılmıştır.
    return len(L["t"]) < 40 and len(L["p"]) > 1 and len(L["p"][0]) < 300

def units(T, k, lang):
    L = T[lang].get(k)
    if not L: return None
    body = L["p"]
    if lang == "ak": body = [x for x in body if x != "***"]
    # Hakikat Kitabevi her mektuba "Bu mektûb, … yazılmışdır." girişiyle başlar: tercümanın girişidir, hizalamaya girmez
    if lang == "hk" and body and HK_HEAD.match(body[0]): body = body[1:]
    skip = set()
    if lang == "fa":
        if fa_has_subtitle(L): body = body[1:]
        skip = fa_skip(body)
    flat = []
    for i, x in enumerate(body):
        if i in skip: continue
        flat += split(re.sub(r"^§v[flm]§", "", x), lang)
    return flat

# ------------------------------------------------------------------ sözcükler
STOP_FA = set(anorm(w) for w in "و در به از كه را اين آن با بر است اند بود شد مي مى نيز هم يا اگر تا چه چون كه هر خود او ايشان ما شما من تو آنكه اينكه بلكه ليكن اما زيرا پس باشد باشند شده كرده كند كنند نمايد نموده گشت گشته داشت دارد دارند حق سبحانه تعالي عليه الله في من الي علي عن ما لا ان هو هي الذي التي كل".split())
STOP_TR = set("ve ile bir bu şu o da de ki ise için gibi daha çok en ne her hem ya veya ama fakat çünkü olan olarak olur oldu olduğu olduğunu olması olmak etmek eder etti edilen yani hiç kendi onun onu ona ondan bunun buna bundan onlar bunlar biz siz ben sen size bize bana sana mı mi mu mü değil var yok kadar sonra önce böyle şöyle diye dahi bile artık işte yine üzere ancak lakin şey bütün tüm allah teala yüce".split())
def fa_tokens(s):
    return [w for w in re.findall(r"[ء-يٱ-ۓ]{3,}", anorm(s)) if w not in STOP_FA]
def ar_tokens(s):
    out = []
    for w in re.findall(r"[ء-يٱ-ۓ]{3,}", anorm(s)):
        w = re.sub(r"^(?:و|ف)?(?:بال|لل|ال)", "", w)
        if len(w) >= 3 and w not in STOP_FA: out.append(w)
    return out
def tr_tokens(s):
    return [w[:6] for w in re.findall(r"[a-zçğıöşü]{3,}", tnorm(s)) if w not in STOP_TR]
def strip_al(w): return re.sub(r"^(?:و|ف)?(?:بال|لل|ال)", "", w)
TOK = {"ar": ar_tokens, "ak": tr_tokens, "hk": tr_tokens}

# ------------------------------------------------------------------ âyet atıfları (kesin eşleşme noktaları)
SURAS = ["الفاتحة","البقرة","آل عمران","النساء","المائدة","الأنعام","الأعراف","الأنفال","التوبة","يونس","هود","يوسف","الرعد","إبراهيم","الحجر","النحل","الإسراء","الكهف","مريم","طه","الأنبياء","الحج","المؤمنون","النور","الفرقان","الشعراء","النمل","القصص","العنكبوت","الروم","لقمان","السجدة","الأحزاب","سبأ","فاطر","يس","الصافات","ص","الزمر","غافر","فصلت","الشورى","الزخرف","الدخان","الجاثية","الأحقاف","محمد","الفتح","الحجرات","ق","الذاريات","الطور","النجم","القمر","الرحمن","الواقعة","الحديد","المجادلة","الحشر","الممتحنة","الصف","الجمعة","المنافقون","التغابن","الطلاق","التحريم","الملك","القلم","الحاقة","المعارج","نوح","الجن","المزمل","المدثر","القيامة","الإنسان","المرسلات","النبأ","النازعات","عبس","التكوير","الانفطار","المطففين","الانشقاق","البروج","الطارق","الأعلى","الغاشية","الفجر","البلد","الشمس","الليل","الضحى","الشرح","التين","العلق","القدر","البينة","الزلزلة","العاديات","القارعة","التكاثر","العصر","الهمزة","الفيل","قريش","الماعون","الكوثر","الكافرون","النصر","المسد","الإخلاص","الفلق","الناس"]
AYAH = [7,286,200,176,120,165,206,75,129,109,123,111,43,52,99,128,111,110,98,135,112,78,118,64,77,227,93,88,69,60,34,30,73,54,45,83,182,88,75,85,54,53,89,59,37,35,38,29,18,45,60,49,62,55,78,96,29,22,24,13,14,11,11,18,12,12,30,52,52,44,28,28,20,56,40,31,50,40,46,42,29,19,36,25,22,17,19,26,30,20,15,21,11,8,8,19,5,8,8,11,11,8,3,9,5,4,7,3,6,3,5,4,5,6]
def valid(s, a): return 1 <= s <= 114 and 1 <= a <= AYAH[s - 1]
def skey(s): return re.sub(r"^ال", "", anorm(s).replace(" ", "").rstrip("،,"))
SK = {skey(s): i + 1 for i, s in enumerate(SURAS)}
SK.update({skey("الإسرا"): 17, skey("آل عمراه"): 3})
FA_REF = re.compile(r"\[\s*([^\]\[:\d]{1,30}?)\s*(?::|آيات|آية)?\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*\]")
TR_REF = re.compile(r"\((\d{1,3})\s*/\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?\)")
def fa_refs(s):
    out = set()
    for m in FA_REF.finditer(s):
        su = SK.get(skey(m.group(1)))
        if su and valid(su, int(m.group(2))): out.add((su, int(m.group(2))))
    return out
def tr_refs(s):
    return {(int(m.group(1)), int(m.group(2))) for m in TR_REF.finditer(s) if valid(int(m.group(1)), int(m.group(2)))}

# ------------------------------------------------------------------ hizalama
def phi(x):
    t = 1 / (1 + 0.2316419 * x); d = 0.3989423 * math.exp(-x * x / 2)
    return 1 - d * t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
PRI = {"11": .5, "10": .004, "01": .004, "21": .14, "12": .14, "31": .06, "13": .06, "41": .025, "14": .025, "22": .03, "32": .015, "23": .015}
MV = [(1, 1), (1, 0), (0, 1), (2, 1), (1, 2), (2, 2), (3, 1), (1, 3), (4, 1), (1, 4), (3, 2), (2, 3)]
LPRI = {m: -math.log(PRI[f"{m[0]}{m[1]}"]) for m in MV}

PRI_X = dict(PRI, **{"15": .012, "51": .012, "16": .005, "61": .005, "24": .008, "42": .008})
MV_X = MV + [(1, 5), (5, 1), (1, 6), (6, 1), (2, 4), (4, 2)]
LPRI.update({m: -math.log(PRI_X[f"{m[0]}{m[1]}"]) for m in MV_X})

def align(A, B, sim=None, refsA=None, refsB=None, w_lex=6.0, w_ref=8.0, moves=None):
    MV = moves or globals()["MV"]
    """A: Farsça cümleler, B: hedef cümleler.
    sim(i, j): Farsça i ile hedef j arasındaki sözcük eşleşme sayısı (yoksa yalnız uzunluk).
    refsA/refsB: cümle başına âyet atfı kümeleri (yoksa kullanılmaz)."""
    la = [len(s) for s in A]; lb = [len(s) for s in B]; n, m = len(la), len(lb)
    c = (sum(lb) or 1) / (sum(la) or 1); s2 = 6.8
    pa = [0]; [pa.append(pa[-1] + x) for x in la]
    pb = [0]; [pb.append(pb[-1] + x) for x in lb]
    ta = None
    if sim:
        ta = [max(1, sim.ntok(i)) for i in range(n)]
    def lencost(a, b):
        mean = (a + b / c) / 2 or 1
        d = (b / c - a) / math.sqrt(mean * s2)
        p = max(2 * (1 - phi(abs(d))), 1e-12)
        return -math.log(p), p
    INF = 1e18; W = m + 1
    Dp = [INF] * ((n + 1) * W); BK = [-1] * ((n + 1) * W); Dp[0] = 0
    band = max(30, abs(n - m) + 30)
    for i in range(n + 1):
        jc = round(i * m / (n or 1))
        for j in range(max(0, jc - band), min(m, jc + band) + 1):
            if not i and not j: continue
            best = INF; bk = -1
            for t, (di, dj) in enumerate(MV):
                if i < di or j < dj: continue
                prev = Dp[(i - di) * W + (j - dj)]
                if prev >= INF: continue
                v = prev + lencost(pa[i] - pa[i - di], pb[j] - pb[j - dj])[0] + LPRI[(di, dj)]
                if di and dj:
                    if sim:
                        hit = 0; tot = 0
                        for x in range(i - di, i):
                            tot += ta[x]
                            for y in range(j - dj, j): hit += sim(x, y)
                        v -= w_lex * min(1.0, hit / tot)
                    if refsA is not None:
                        ra = set().union(*[refsA[x] for x in range(i - di, i)])
                        rb = set().union(*[refsB[y] for y in range(j - dj, j)])
                        if ra and rb:
                            v += -w_ref if ra & rb else w_ref
                        elif ra or rb:
                            v += w_ref * 0.25
                if v < best: best, bk = v, t
            Dp[i * W + j] = best; BK[i * W + j] = bk
    beads = []; i, j = n, m
    while i > 0 or j > 0:
        t = BK[i * W + j]
        if t < 0: break
        di, dj = MV[t]
        a = list(range(i - di, i)); b = list(range(j - dj, j))
        p = lencost(pa[i] - pa[i - di], pb[j] - pb[j - dj])[1] if a and b else 0
        beads.append((a, b, p)); i -= di; j -= dj
    return beads[::-1]

class Sim:
    """Farsça cümle i'deki sözcüklerden kaçının hedef cümle j'de bir karşılığı var."""
    def __init__(self, A, B, lang, dic):
        self.fa = [set(fa_tokens(s)) for s in A]
        self.tg = [set(TOK[lang](s)) for s in B]
        # Türkçe metne aynen alınmış Farsça satırlar (beyitler, alıntılar): Farsça asılla doğrudan eşleşir
        self.tgfa = [set(fa_tokens(s)) for s in B] if lang in ("ak", "hk") else None
        self.dic = dic; self.lang = lang; self.cache = {}
    def ntok(self, i): return len(self.fa[i])
    def __call__(self, i, j):
        key = (i, j)
        v = self.cache.get(key)
        if v is None:
            tg = self.tg[j]; v = 0
            tf = self.tgfa[j] if self.tgfa else None
            for f in self.fa[i]:
                if self.lang == "ar" and strip_al(f) in tg: v += 1; continue
                if tf and f in tf: v += 1; continue
                tr = self.dic.get(f)
                if tr and not tr.isdisjoint(tg): v += 1
            self.cache[key] = v
        return v

def learn_dict(T, ALIGN, lang, min_joint=4, min_dice=0.18, top=6):
    """Hizalanmış cümle gruplarından Farsça→hedef sözlük (Dice katsayısı)."""
    cf = Counter(); ct = Counter(); cft = Counter()
    for k, A in ALIGN.items():
        if lang not in A: continue
        UF, UT = A["U"]["fa"], A["U"][lang]
        for a, b, p in A[lang]:
            if not a or not b or p < 0.2: continue
            F = set(w for i in a for w in fa_tokens(UF[i])); G = set(w for j in b for w in TOK[lang](UT[j]))
            for f in F: cf[f] += 1
            for g in G: ct[g] += 1
            for f in F:
                for g in G: cft[(f, g)] += 1
    by = defaultdict(list)
    for (f, g), j in cft.items():
        if j < min_joint: continue
        d = 2 * j / (cf[f] + ct[g])
        if d >= min_dice: by[f].append((d, g))
    return {f: set(g for d, g in sorted(v, reverse=True)[:top]) for f, v in by.items()}

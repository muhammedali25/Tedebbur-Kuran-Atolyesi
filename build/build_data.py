"""Tedebbür veri derleyicisi.

Girdi : kaynak/morph.txt, kaynak/tur-hasanbasricanta.json, kaynak/tur-elmalilihamdiya.json, kaynak/quran-meta-hafs.txt
Çıktı : site/d/{core,ar,meal,morph,rel}.json

Her sayı ya kaynaktan sayılır ya da aşağıda formülü yazılı bir hesaptan çıkar.
Kullanım: python3 build/build_data.py
"""
import collections
import json
import math
import os
import re
import unicodedata

import numpy as np

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAYNAK = os.path.join(KOK, 'kaynak')
CIKTI = os.path.join(KOK, 'site', 'd')

SURE_ADLARI = """Fâtiha|Bakara|Âl-i İmrân|Nisâ|Mâide|En'âm|A'râf|Enfâl|Tevbe|Yûnus|Hûd|Yûsuf|Ra'd|İbrâhîm|Hicr|Nahl|İsrâ|Kehf|Meryem|Tâhâ|Enbiyâ|Hac|Mü'minûn|Nûr|Furkân|Şuarâ|Neml|Kasas|Ankebût|Rûm|Lokmân|Secde|Ahzâb|Sebe'|Fâtır|Yâsîn|Sâffât|Sâd|Zümer|Mü'min|Fussilet|Şûrâ|Zuhruf|Duhân|Câsiye|Ahkâf|Muhammed|Fetih|Hucurât|Kâf|Zâriyât|Tûr|Necm|Kamer|Rahmân|Vâkıa|Hadîd|Mücâdele|Haşr|Mümtehine|Saf|Cuma|Münâfikûn|Teğâbün|Talâk|Tahrîm|Mülk|Kalem|Hâkka|Meâric|Nûh|Cin|Müzzemmil|Müddessir|Kıyâme|İnsân|Mürselât|Nebe'|Nâziât|Abese|Tekvîr|İnfitâr|Mutaffifîn|İnşikâk|Bürûc|Târık|A'lâ|Gâşiye|Fecr|Beled|Şems|Leyl|Duhâ|İnşirâh|Tîn|Alak|Kadir|Beyyine|Zilzâl|Âdiyât|Kâria|Tekâsür|Asr|Hümeze|Fîl|Kureyş|Mâûn|Kevser|Kâfirûn|Nasr|Tebbet|İhlâs|Felak|Nâs""".split('|')
assert len(SURE_ADLARI) == 114

G2_ESIK = 10.83  # ki-kare, 1 serbestlik derecesi, p = 0.001 (çoklu sınama düzeltmesi yok)


def g2(a, r, c, n):
    """2x2 log-olabilirlik. a: ortak, r: satır toplamı, c: sütun toplamı, n: genel toplam."""
    a = np.asarray(a, dtype=np.float64)
    r = np.asarray(r, dtype=np.float64)
    c = np.asarray(c, dtype=np.float64)
    cells = [(a, r, c), (r - a, r, n - c), (c - a, n - r, c), (n - r - c + a, n - r, n - c)]
    tot = np.zeros(np.broadcast(a, r, c).shape)
    for o, rr, cc in cells:
        e = rr * cc / n
        with np.errstate(divide='ignore', invalid='ignore'):
            tot = tot + np.where(o > 0, o * np.log(o / e), 0.0)
    return 2 * tot


# ---------------------------------------------------------------- sure üst verisi
src = open(os.path.join(KAYNAK, 'quran-meta-hafs.txt'), encoding='utf8').read()
blok = src[src.index('SurahList'):]
blok = blok[:blok.index(']\n\t]') + 4] if ']\n\t]' in blok else blok
satirlar = re.findall(r'\[\s*(-?\d+),\s*(\d+),\s*(\d+),\s*(\d+),\s*"([^"]*)",\s*(true|false)\s*\]', blok)
satirlar = [s for s in satirlar if s[0] != '-1'][:114]
assert len(satirlar) == 114, len(satirlar)
AYET_SAYISI = [int(s[1]) for s in satirlar]
NUZUL = [int(s[2]) for s in satirlar]
AD_AR = [s[4] for s in satirlar]
MEKKI = [1 if s[5] == 'true' else 0 for s in satirlar]
assert sum(AYET_SAYISI) == 6236
assert sorted(NUZUL) == list(range(1, 115)), 'nüzul sırası permütasyon değil'
BAS = [0]
for n in AYET_SAYISI:
    BAS.append(BAS[-1] + n)
N_AYET = 6236

# ---------------------------------------------------------------- morfoloji
kokler, kok_id = [], {}
lemmalar, lem_id = [], {}
etiketler, etiket_id = [], {}
ayet_kelime = [[] for _ in range(N_AYET)]   # her ayet: [ [metin, kok, lemma, [etiket, uzunluk]...] ]
onceki = None
for satir in open(os.path.join(KAYNAK, 'morph.txt'), encoding='utf8'):
    satir = satir.rstrip('\n')
    if not satir:
        continue
    yer, bicim, tur, ozl = satir.split('\t')
    s, a, k, _ = (int(x) for x in yer.split(':'))
    gi = BAS[s - 1] + a - 1
    par = [p for p in ozl.split('|') if p]
    kok = next((p[5:] for p in par if p.startswith('ROOT:')), None)
    lem = next((p[4:] for p in par if p.startswith('LEM:')), None)
    ek = 'PREF' in par or 'SUFF' in par
    kalan = [p for p in par if not p.startswith('ROOT:') and not p.startswith('LEM:')]
    et = tur + '|' + '|'.join(kalan)
    if et not in etiket_id:
        etiket_id[et] = len(etiketler)
        etiketler.append(et)
    if (s, a, k) != onceki:
        ayet_kelime[gi].append({'m': '', 'r': -1, 'l': -1, 'p': []})
        onceki = (s, a, k)
    w = ayet_kelime[gi][-1]
    w['m'] += bicim.replace(' ', '\u00a0')   # 37:130 kelimesi kaynakta boşluk içerir; kelime sınırı sayılmasın
    w['p'] += [etiket_id[et], len(bicim)]
    if kok is not None:
        if kok not in kok_id:
            kok_id[kok] = len(kokler)
            kokler.append(kok)
        w['r'] = kok_id[kok]
    if lem is not None and not ek and (w['l'] == -1 or kok is not None):
        anahtar = (lem, kok)
        if anahtar not in lem_id:
            lem_id[anahtar] = len(lemmalar)
            lemmalar.append([lem, kok_id[kok] if kok is not None else -1])
        w['l'] = lem_id[anahtar]

assert all(ayet_kelime), 'kelimesiz ayet var'
N_KELIME = sum(len(a) for a in ayet_kelime)
assert N_KELIME == 77429, N_KELIME
R = len(kokler)
print('kök', R, 'lemma', len(lemmalar), 'etiket', len(etiketler), 'kelime', N_KELIME)

sure_of = np.zeros(N_AYET, dtype=np.int32)
for s in range(114):
    sure_of[BAS[s]:BAS[s + 1]] = s

# kök × ayet sayımı ve varlık matrisi
C = np.zeros((N_AYET, R), dtype=np.float32)
for gi, ks in enumerate(ayet_kelime):
    for w in ks:
        if w['r'] >= 0:
            C[gi, w['r']] += 1
B = (C > 0).astype(np.float32)
kok_n = C.sum(0)                      # kökün toplam kelime sayısı
kok_df = B.sum(0)                     # kökün geçtiği ayet sayısı
lem_n = collections.Counter(w['l'] for ks in ayet_kelime for w in ks if w['l'] >= 0)

# kök × sure
RS = np.zeros((114, R), dtype=np.float64)
for s in range(114):
    RS[s] = C[BAS[s]:BAS[s + 1]].sum(0)
sure_koklu = RS.sum(1)
TOPLAM = RS.sum()

# ---------------------------------------------------------------- sure parmak izi (G²)
parmak = []
for s in range(114):
    a = RS[s]
    g = g2(a, sure_koklu[s], kok_n.astype(np.float64), TOPLAM)
    fazla = a / sure_koklu[s] > (kok_n - a) / (TOPLAM - sure_koklu[s])
    aday = [(float(g[r]), r) for r in range(R) if a[r] > 0 and fazla[r] and g[r] >= G2_ESIK]
    aday.sort(reverse=True)
    parmak.append([[r, int(a[r]), round(v, 1)] for v, r in aday[:14]])

# ---------------------------------------------------------------- sure benzerliği
sure_df = (RS > 0).sum(0)
idf_s = np.log(114 / sure_df)
V = np.log1p(RS) * idf_s
V = V / np.linalg.norm(V, axis=1, keepdims=True)
COS = V @ V.T
komsu = []
for s in range(114):
    sira = np.argsort(-COS[s])
    komsu.append([[int(t), round(float(COS[s, t]), 3)] for t in sira if t != s][:6])

# ---------------------------------------------------------------- kök yoldaşlığı
JO = B.T @ B
df = kok_df.astype(np.float64)
G = g2(JO, df[:, None], df[None, :], N_AYET)
BEK = df[:, None] * df[None, :] / N_AYET
yoldas = []
for r in range(R):
    aday = [(float(G[r, q]), q) for q in range(R)
            if q != r and JO[r, q] >= 3 and JO[r, q] > BEK[r, q] and G[r, q] >= G2_ESIK]
    aday.sort(reverse=True)
    yoldas.append([[q, int(JO[r, q]), round(v, 1)] for v, q in aday[:12]])

# ---------------------------------------------------------------- ayet akrabalığı
idf_a = np.log(N_AYET / np.maximum(kok_df, 1))
W = B * idf_a
norm = np.linalg.norm(W, axis=1, keepdims=True)
norm[norm == 0] = 1
W = W / norm
akraba = []
for i0 in range(0, N_AYET, 800):
    cs = W[i0:i0 + 800] @ W.T
    ort = B[i0:i0 + 800] @ B.T
    for k in range(cs.shape[0]):
        i = i0 + k
        cs[k, i] = -1
        uy = np.where((ort[k] >= 2) & (cs[k] >= 0.30))[0]
        uy = uy[np.argsort(-cs[k, uy])][:6]
        akraba.append([[int(j), int(round(float(cs[k, j]) * 100))] for j in uy])
print('akrabası olan ayet', sum(1 for a in akraba if a))

# ---------------------------------------------------------------- mealler
TR_KUCUK = str.maketrans({'I': 'ı', 'İ': 'i', 'Â': 'a', 'Î': 'i', 'Û': 'u', 'â': 'a', 'î': 'i', 'û': 'u'})
DUZELTMELER = ['Çantay, Fâtiha: kaynak dosyada meal bir ayet kaymıştı ve besmelenin meali yoktu. '
               'Kayıtlar içeriğine göre 2-4, 5 ve 6-7. ayetlere yerleştirildi; 1. ayet (besmele) için Çantay meali gösterilmiyor.',
               'Çantay: kaynak dosyadaki ´ işareti kesme işareti (’) olarak gösteriliyor.']


def sozcukler(t):
    t = re.sub(r'\([^()]*\)', ' ', t)          # mütercimin parantez içi açıklamaları hesaba girmez
    t = t.translate(TR_KUCUK).lower().replace('’', '').replace("'", '')
    return [w for w in re.findall(r'[a-zçğıöşü]+', t) if len(w) >= 2]


def meal_hazirla(dosya, cantay):
    ham = json.load(open(os.path.join(KAYNAK, dosya), encoding='utf8'))['quran']
    assert len(ham) == N_AYET
    metin = [None] * N_AYET
    for x in ham:
        metin[BAS[x['chapter'] - 1] + x['verse'] - 1] = x['text'].replace('´', '’').strip()
    if cantay:
        # DÜZELTME: Fâtiha bir ayet kaymış; içerikten doğrulanarak yerine alınır.
        assert metin[0].startswith('Hamd olsun') and metin[3].startswith('Yalınız sana') and metin[4].startswith('Bizi doğru')
        hamd, iyyake, ihdina = metin[0], metin[3], metin[4]
        metin[0:7] = [None, hamd, hamd, hamd, iyyake, ihdina, ihdina]
    bm, ba, ab = [], [], [-1] * N_AYET
    i = 0
    while i < N_AYET:
        if metin[i] is None:
            i += 1
            continue
        j = i
        while j + 1 < N_AYET and metin[j + 1] == metin[i] and sure_of[j + 1] == sure_of[i]:
            j += 1
        for k in range(i, j + 1):
            ab[k] = len(bm)
        bm.append(metin[i])
        ba.append([i, j])
        i = j + 1
    print(dosya, 'meal birimi', len(bm), 'birleşik grup', sum(1 for a, b in ba if b > a))
    # kök → meal izi
    govde_id, govde_bicim, birim_govde = {}, [], []
    for t in bm:
        gs = set()
        for w in sozcukler(t):
            g = w[:5]
            if g not in govde_id:
                govde_id[g] = len(govde_bicim)
                govde_bicim.append(collections.Counter())
            govde_bicim[govde_id[g]][w] += 1
            gs.add(govde_id[g])
        birim_govde.append(gs)
    U = len(bm)
    T = np.zeros((U, len(govde_bicim)), dtype=np.float32)
    for u, gs in enumerate(birim_govde):
        T[u, list(gs)] = 1
    BU = np.zeros((U, R), dtype=np.float32)
    for u, (a, b) in enumerate(ba):
        BU[u] = B[a:b + 1].max(0)
    t_df = T.sum(0).astype(np.float64)
    r_df = BU.sum(0).astype(np.float64)
    JT = BU.T @ T
    GT = g2(JT, r_df[:, None], t_df[None, :], U)
    BEKT = r_df[:, None] * t_df[None, :] / U
    iz = []
    for r in range(R):
        uy = np.where((JT[r] >= 2) & (JT[r] > BEKT[r]) & (GT[r] >= G2_ESIK))[0]
        uy = uy[np.argsort(-GT[r, uy])][:8]
        iz.append([[govde_bicim[g].most_common(1)[0][0], int(JT[r, g]), int(t_df[g]), round(float(GT[r, g]), 1)]
                   for g in uy])
    print('  izi bulunan kök', sum(1 for k in iz if k), '/', R)
    return {'t': bm, 'r': ba, 'u': ab}, iz


MEAL1, karsilik = meal_hazirla('tur-hasanbasricanta.json', True)
MEAL2, karsilik2 = meal_hazirla('tur-elmalilihamdiya.json', False)
U = len(MEAL1['t'])

# ---------------------------------------------------------------- Mekkî–Medenî kök kayması
mk = np.array(MEKKI, dtype=bool)
aM, aD = RS[mk].sum(0), RS[~mk].sum(0)
tM, tD = float(sure_koklu[mk].sum()), float(sure_koklu[~mk].sum())
gK = g2(aM, tM, kok_n.astype(np.float64), TOPLAM)
kayma = {'tM': int(tM), 'tD': int(tD), 'mekki': [], 'medeni': []}
for r in np.argsort(-gK):
    if gK[r] < G2_ESIK:
        break
    yon = 'mekki' if aM[r] / tM > aD[r] / tD else 'medeni'
    if len(kayma[yon]) < 24:
        kayma[yon].append([int(r), int(aM[r]), int(aD[r]), round(float(gK[r]), 1)])

# ---------------------------------------------------------------- özel isimler
ISIM_TR = {'اللَّه': 'Allah', 'مُوسَى': 'Mûsâ', 'شَيْطان': 'Şeytan', 'جَهَنَّم': 'Cehennem', 'فِرْعَوْن': 'Firavun', 'إِبْراهِيم': 'İbrâhîm', 'قُرْءان': "Kur'an", 'جَنَّة': 'Cennet', 'إِسْرائِيل': 'İsrâil', 'نُوح': 'Nûh', 'مَرْيَم': 'Meryem', 'يُوسُف': 'Yûsuf', 'لُوط': 'Lût', 'ثَمُود': 'Semûd', 'آدَم': 'Âdem', 'عِيسَى': 'Îsâ', 'عاد': 'Âd', 'هارُون': 'Hârûn', 'تَوْراة': 'Tevrat', 'سُلَيْمان': 'Süleymân', 'إِسْحاق': 'İshâk', 'يَعْقُوب': "Ya'kûb", 'داوُد': 'Dâvûd', 'نَصْرانِيّ': 'Nasrânî (Hristiyan)', 'مُسْلِم': 'Müslim', 'إِسْماعِيل': 'İsmâîl', 'إِنجِيل': 'İncil', 'إِبْلِيس': 'İblîs', 'مَسِيح': 'Mesîh', 'شُعَيْب': 'Şuayb', 'عَدْن': 'Adn', 'هُود': 'Hûd', 'مَدْيَن': 'Medyen', 'يَهُود': 'Yahudi', 'صالِح': 'Sâlih', 'زَكَرِيّا': 'Zekeriyyâ', 'إِسْلام': 'İslâm', 'هامان': 'Hâmân', 'اللَّهُمَّ': 'Allahümme', 'يَحْيَى': 'Yahyâ', 'مُحَمَّد': 'Muhammed', 'أَيُّوب': 'Eyyûb', 'يُونُس': 'Yûnus', 'مَدِينَة': 'Medine', 'مِصْر': 'Mısır', 'قارُون': 'Kârûn', 'سَقَر': 'Sekar', 'صابِئ': 'Sâbiî', 'جِبْرِيل': 'Cebrâîl', 'جالُوت': 'Câlût', 'عِمْران': 'İmrân', 'زَبُور': 'Zebûr', 'جاهِلِيَّة': 'Câhiliye', 'إِلْياس': 'İlyâs', 'سامِرِيّ': 'Sâmirî', 'زَقُّوم': 'Zakkum', 'طالُوت': 'Tâlût', 'كَعْبَة': 'Kâbe', 'الْيَسَع': 'Elyesa', 'يَأْجُوج': "Ye'cûc", 'مَأْجُوج': "Me'cûc", 'فِرْدَوْس': 'Firdevs', 'إِدْرِيس': 'İdrîs', 'سَبَإ': "Sebe'", 'لُقْمان': 'Lokmân', 'تُبَّع': "Tübba'", 'مِيكال': 'Mîkâl', 'بابِل': 'Bâbil', 'هارُوت': 'Hârût', 'مارُوت': 'Mârût', 'صَفا': 'Safâ', 'مَرْوَة': 'Merve', 'رَمَضان': 'Ramazan', 'عَرَفات': 'Arafat', 'بَكَّة': 'Bekke', 'بَدْر': 'Bedir', 'آزَر': 'Âzer', 'حُنَيْن': 'Huneyn', 'عُزَيْر': 'Üzeyr', 'جُودِيّ': 'Cûdî', 'مَجُوس': 'Mecûs', 'سَيْناء': 'Sînâ', 'رُوم': 'Rûm', 'يَثْرِب': 'Yesrib', 'زَيْد': 'Zeyd', 'بَعْل': "Ba'l", 'مالِك': 'Mâlik', 'أَحْقاف': 'Ahkâf', 'مَكَّة': 'Mekke', 'اللّات': 'Lât', 'الْعُزَّى': 'Uzzâ', 'مَناة': 'Menât', 'شِعْرَى': "Şi'râ", 'أَحْمَد': 'Ahmed', 'جُمُعَة': 'Cuma', 'لَظَى': 'Lezâ', 'وَدّ': 'Ved', 'سُواع': "Süvâ'", 'يَغُوث': 'Yeğûs', 'يَعُوق': 'Yeûk', 'نَسْر': 'Nesr', 'سَلْسَبِيل': 'Selsebîl', 'إِرَم': 'İrem', 'سِينِين': 'Sînîn', 'قُرَيْش': 'Kureyş'}
ISIM_TR.update({'سِلْم': 'Silm'})
ISIM_TR = {unicodedata.normalize('NFD', k): v for k, v in ISIM_TR.items()}
isim_yer = collections.defaultdict(list)
for gi, ks in enumerate(ayet_kelime):
    for wi, w in enumerate(ks):
        if w['l'] >= 0 and any('PN' in etiketler[t].split('|') for t in w['p'][0::2]):
            isim_yer[w['l']].append((gi, wi))
L_ALLAH_ERKEN = next(i for i, (l_, r_) in enumerate(lemmalar) if unicodedata.normalize('NFD', l_) == unicodedata.normalize('NFD', 'اللَّه'))
isimler = []
for l, yerler in sorted(isim_yer.items(), key=lambda kv: -len(kv[1])):
    ad_ar, kokr = lemmalar[l]
    v = np.zeros(N_AYET, dtype=np.float32)
    ss = collections.Counter()
    for gi, _ in yerler:
        v[gi] = 1
        ss[int(sure_of[gi])] += 1
    dfi = float(v.sum())
    jo = v @ B
    gg = g2(jo, dfi, df, N_AYET)
    aday = [(float(gg[q]), q) for q in range(R)
            if q != kokr and jo[q] >= 2 and jo[q] > dfi * df[q] / N_AYET and gg[q] >= G2_ESIK]
    aday.sort(reverse=True)
    sd = []
    for s_, c_ in sorted(ss.items()):
        sd += [s_, c_]
    duz = []
    if l != L_ALLAH_ERKEN:
        for gi, wi in yerler:
            duz += [gi, wi]
    isimler.append([ad_ar, ISIM_TR.get(unicodedata.normalize('NFD', ad_ar), ''), len(yerler), int(dfi), kokr, sd,
                    [[q, int(jo[q]), round(v_, 1)] for v_, q in aday[:12]], duz])
print('özel isim', len(isimler), 'Türkçesi eksik', [i[0] for i in isimler if not i[1]])

# ---------------------------------------------------------------- tekrarlanan ifadeler
NMIN, NMAX = 4, 40
ngram = {}
for n in range(NMIN, NMAX + 2):
    d = collections.defaultdict(list)
    for gi, ks in enumerate(ayet_kelime):
        m = [w['m'] for w in ks]
        for i in range(len(m) - n + 1):
            d[tuple(m[i:i + n])].append((gi, i))
    ngram[n] = {k: v for k, v in d.items() if len(v) >= 2}
kalip = []
for n in range(NMIN, NMAX + 1):
    ust = ngram[n + 1]
    kapsanan = set()
    for k, v in ust.items():
        for alt in (k[:-1], k[1:]):
            if alt in ngram[n] and len(ngram[n][alt]) == len(v):
                kapsanan.add(alt)
    for k, v in ngram[n].items():
        if k not in kapsanan and (len(v) >= 3 or n >= 6):
            kalip.append((n, len(v), v))
kalip_toplam = len(kalip)
kalip.sort(key=lambda x: -(x[0] * x[1]))
kalip = kalip[:500]
kalip_cikti = []
for n, c, v in kalip:
    duz = []
    for gi, wi in v[:80]:
        duz += [gi, wi]
    kalip_cikti.append([n, c, len({int(sure_of[gi]) for gi, _ in v}), duz])
print('kalıp', kalip_toplam, 'gösterilen', len(kalip_cikti))

# ---------------------------------------------------------------- fiil profili, fâsıla, ritim
HARF = re.compile('[ء-يٱ]')
ESLE = {'ى': 'ا', 'ة': 'ه', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ٱ': 'ا', 'ؤ': 'ء', 'ئ': 'ء'}
SAHIS = re.compile(r'^([123])(MS|FS|MD|FD|MP|FP|S|D|P)$')
gram, fasila, ritim = [], [], []
for s in range(114):
    g = collections.Counter()
    fs = ''
    for gi in range(BAS[s], BAS[s + 1]):
        ks = ayet_kelime[gi]
        for w in ks:
            g['kelime'] += 1
            for ti in w['p'][0::2]:
                par = etiketler[ti].split('|')
                if par[0] != 'V':
                    continue
                g['fiil'] += 1
                for z in ('PERF', 'IMPF', 'IMPV', 'PASS'):
                    if z in par:
                        g[z] += 1
                for p in par:
                    m = SAHIS.match(p)
                    if m:
                        g['s' + m.group(1)] += 1
        harfler = HARF.findall(ks[-1]['m'])
        fs += ESLE.get(harfler[-1], harfler[-1])
    gram.append([g['kelime'], g['fiil'], g['PERF'], g['IMPF'], g['IMPV'], g['PASS'], g['s1'], g['s2'], g['s3']])
    fasila.append(fs)
    ritim.append([len(ayet_kelime[gi]) for gi in range(BAS[s], BAS[s + 1])])

# ================================================================ üçüncü tur
def nfd(x):
    return unicodedata.normalize('NFD', x)


def parcalar(w):
    return [etiketler[t].split('|') for t in w['p'][0::2]]


def govde(w):
    for p_ in parcalar(w):
        if 'PREF' not in p_ and 'SUFF' not in p_:
            return p_
    return []


def var(w, et):
    return any(et in p_ for p_ in parcalar(w))


def lem_ad(w):
    return lemmalar[w['l']][0] if w['l'] >= 0 else ''


def es_kokler(ayetler, dis=(), en_az=2, kac=12):
    """Verilen ayet kümesinde tesadüften sık geçen kökler (ayet düzeyi G²)."""
    v = np.zeros(N_AYET, dtype=np.float32)
    v[list(ayetler)] = 1
    n_ = float(v.sum())
    jo = v @ B
    gg = g2(jo, n_, df, N_AYET)
    aday = [(float(gg[q]), q) for q in range(R)
            if q not in dis and jo[q] >= en_az and jo[q] > n_ * df[q] / N_AYET and gg[q] >= G2_ESIK]
    aday.sort(reverse=True)
    return [[q, int(jo[q]), round(x, 1)] for x, q in aday[:kac]]


def md(ayetler):
    m_ = sum(1 for gi in ayetler if MEKKI[sure_of[gi]])
    return [m_, len(ayetler) - m_]


R_KVL, R_RBB = kok_id['قول'], kok_id['ربب']
L_ALLAH = next(i for i, (l, r) in enumerate(lemmalar) if nfd(l) == nfd('اللَّه'))

# ---- tekil hitap: emir, nehiy, kul
emir, kul_yer = [], []
sonra = {0: np.zeros(R), 1: np.zeros(R)}
for gi, ks in enumerate(ayet_kelime):
    aktarim = False
    for wi, w in enumerate(ks):
        g = govde(w)
        if g and g[0] == 'V' and '2MS' in g:
            tip = None
            if 'IMPV' in g:
                tip = 0
            elif 'IMPF' in g and wi > 0 and var(ks[wi - 1], 'PRO'):
                tip = 1
            if tip is not None:
                kulmu = tip == 0 and w['r'] == R_KVL and 'VF:1' in g
                if kulmu:
                    kul_yer += [gi, wi]
                    for w2 in ks[wi + 1:]:
                        if w2['r'] >= 0:
                            sonra[MEKKI[sure_of[gi]]][w2['r']] += 1
                emir += [gi, wi, w['l'], tip, 1 if aktarim else 0]
        if w['r'] == R_KVL and not (g and 'IMPV' in g and '2MS' in g):
            aktarim = True
kul_sonra = {}
for anahtar, mm in (('mekki', 1), ('medeni', 0)):
    a_ = sonra[mm]
    t_ = a_.sum()
    gg = g2(a_, t_, kok_n.astype(np.float64), TOPLAM)
    aday = [(float(gg[r]), r) for r in range(R) if a_[r] >= 3 and a_[r] / t_ > (kok_n[r] - a_[r]) / (TOPLAM - t_) and gg[r] >= G2_ESIK]
    aday.sort(reverse=True)
    kul_sonra[anahtar] = [[r, int(a_[r]), round(x, 1)] for x, r in aday[:16]]
kul_ayet = sorted(set(kul_yer[0::2]))
print('2MS emir/nehiy', len(emir) // 5, 'kul', len(kul_yer) // 2)

# ---- Rabbüke
rabbuke = []
for gi, ks in enumerate(ayet_kelime):
    for wi, w in enumerate(ks):
        if w['r'] == R_RBB and any('PRON' in p_ and '2MS' in p_ for p_ in parcalar(w)):
            rabbuke += [gi, wi]
rabbuke_ayet = sorted(set(rabbuke[0::2]))

# ---- nidâ
NIDA_TR = {nfd(k): v for k, v in {
    'الَّذِي آمَنَ': 'Ey iman edenler', 'ناس': 'Ey insanlar', 'نَبِيّ': 'Ey Nebi', 'رَسُول': 'Ey Resul', 'قَوْم': 'Ey kavmim',
    'ابْن آدَم': 'Ey Âdemoğulları', 'ابْن إِسْرائِيل': 'Ey İsrâiloğulları', 'أَهْل كِتاب': 'Ey Kitap ehli', 'مُوسَى': 'Ey Mûsâ',
    'مُزَّمِّل': 'Ey örtünen (Müzzemmil)', 'مُدَّثِّر': 'Ey bürünen (Müddessir)', 'الَّذِي كَفَرَ': 'Ey inkâr edenler', 'آدَم': 'Ey Âdem',
    'إِبْراهِيم': 'Ey İbrâhîm', 'نُوح': 'Ey Nûh', 'عِيسَى': 'Ey Îsâ', 'أَب': 'Ey babacığım', 'ابْن': 'Ey oğulcuğum', 'عَبْد': 'Ey kullarım',
    'إِنسان': 'Ey insan', 'لَيْت': 'Keşke (yâ leyte)', 'مَلَأ': 'Ey ileri gelenler', 'مَرْيَم': 'Ey Meryem', 'صالِح': 'Ey Sâlih',
    'شُعَيْب': 'Ey Şuayb', 'هُود': 'Ey Hûd', 'لُوط': 'Ey Lût', 'داوُد': 'Ey Dâvûd', 'زَكَرِيّا': 'Ey Zekeriyyâ', 'يَحْيَى': 'Ey Yahyâ',
    'وَيْل': 'Vay hâlimize (yâ veyl)', 'أُولُو أَلْباب': 'Ey akıl sahipleri', 'مَعْشَر جِنّ': 'Ey cin topluluğu', 'نَفْس': 'Ey nefis',
    'أَرْض': 'Ey yer', 'جَبَل': 'Ey dağlar', 'نار': 'Ey ateş', 'سَماء': 'Ey gök', 'حَسْرَة': 'Yazık (yâ hasreten)', 'أَسَف': 'Yazık (yâ esefâ)',
    'بُشْرَى': 'Müjde', 'ساحِر': 'Ey sihirbaz', 'مالِك': 'Ey Mâlik', 'هامان': 'Ey Hâmân', 'فِرْعَوْن': 'Ey Firavun', 'إِبْلِيس': 'Ey İblîs',
    'صاحِب سِجْن': 'Ey zindan arkadaşlarım', 'أَخ هارُون': 'Ey Hârûn\'un kız kardeşi', 'ذا قَرْن': 'Ey Zülkarneyn', 'أَهْل يَثْرِب': 'Ey Yesrib halkı',
    'نِساء نَبِيّ': 'Ey Peygamber hanımları', 'بُنَىّ': 'Ey oğulcuğum', 'ذُو قَرْن': 'Ey Zülkarneyn', 'اللَّهُمَّ': 'Allahümme', 'عَزِيز': 'Ey Azîz', 'رَبّ': 'Yâ Rabbi', 'الَّذِي آتَى': 'Ey kendilerine Kitap verilenler', 'حَسْرَت': 'Yazık (yâ hasreten)', 'الَّذِي نَزَّلَ': 'Ey kendisine Zikir indirilen', 'أُخْت هارُون': "Ey Hârûn'un kız kardeşi", 'هارُون': 'Ey Hârûn', 'أُمّ': 'Ey anamın oğlu', 'سامِرِيّ': 'Ey Sâmirî', 'مُؤْمِن': 'Ey müminler', 'ثَقَل': 'Ey iki ağırlık (ins ve cin)', 'نَمْل': 'Ey karıncalar'}.items()}
EK_ALAN = {nfd(x) for x in ('ابْن', 'أَهْل', 'صاحِب', 'مَعْشَر', 'أُولُو', 'ذا', 'ذُو', 'أَخ', 'نِساء', 'أُخْت')}
nida_grup = collections.OrderedDict()
for gi, ks in enumerate(ayet_kelime):
    for wi, w in enumerate(ks):
        if not var(w, 'VOC'):
            continue
        l0 = lem_ad(w)
        n_soz = 1
        if nfd(l0) == nfd('أَيّ') and wi + 1 < len(ks):
            l1 = lem_ad(ks[wi + 1])
            n_soz = 2
            if nfd(l1) == nfd('الَّذِي') and wi + 2 < len(ks):
                anahtar = l1 + ' ' + lem_ad(ks[wi + 2])
                n_soz = 3
            else:
                anahtar = l1
        elif nfd(l0) in EK_ALAN and wi + 1 < len(ks) and lem_ad(ks[wi + 1]):
            anahtar = l0 + ' ' + lem_ad(ks[wi + 1])
            n_soz = 2
        else:
            anahtar = l0 or w['m']
        d = nida_grup.setdefault(anahtar, {'yer': [], 'n': n_soz})
        d['yer'] += [gi, wi]
EFENDIMIZ_NIDA = {nfd(x) for x in ('نَبِيّ', 'رَسُول', 'مُزَّمِّل', 'مُدَّثِّر')}
nida = []
for k, d in sorted(nida_grup.items(), key=lambda kv: -len(kv[1]['yer'])):
    ay = d['yer'][0::2]
    nida.append([k, NIDA_TR.get(nfd(k), ''), len(ay), d['n'], md(ay), 1 if nfd(k) in EFENDIMIZ_NIDA else 0, d['yer']])
nida_ef_ayet = sorted({gi for x in nida if x[5] for gi in x[6][0::2]})
print('nidâ', sum(x[2] for x in nida), 'grup', len(nida), 'Türkçesiz ilkler', [x[0] for x in nida if not x[1]][:12])

# ---- Allah ve Resulü
L_RESUL = {i for i, (l, r) in enumerate(lemmalar) if nfd(l) == nfd('رَسُول')}
ar_yer = []
for gi, ks in enumerate(ayet_kelime):
    for wi in range(len(ks) - 1):
        if ks[wi]['l'] == L_ALLAH and ks[wi + 1]['l'] in L_RESUL and var(ks[wi + 1], 'CONJ') and not govde(ks[wi + 1])[-1:] == ['MP'] and 'MP' not in govde(ks[wi + 1]):
            ar_yer += [gi, wi]
ar_ayet = sorted(set(ar_yer[0::2]))
allah_resul = {'yer': ar_yer, 'md': md(ar_ayet), 'es': es_kokler(ar_ayet, dis=(kok_id['أله'], kok_id['رسل']), kac=16)}
print('Allah ve Resulü', len(ar_yer) // 2, 'ayet', len(ar_ayet))

# ---- peygamberler aynası
PEYGAMBER = ['Âdem', 'İdrîs', 'Nûh', 'Hûd', 'Sâlih', 'İbrâhîm', 'Lût', 'İsmâîl', 'İshâk', "Ya'kûb", 'Yûsuf', 'Eyyûb', 'Şuayb', 'Mûsâ', 'Hârûn',
             'Dâvûd', 'Süleymân', 'İlyâs', 'Elyesa', 'Yûnus', 'Zekeriyyâ', 'Yahyâ', 'Îsâ']
hitap_ayet = sorted(set(kul_ayet) | set(rabbuke_ayet) | set(nida_ef_ayet))
vh = np.zeros(N_AYET, dtype=np.float32)
vh[hitap_ayet] = 1
joh = vh @ B
gh = g2(joh, float(len(hitap_ayet)), df, N_AYET)
hitap_one = {q: float(gh[q]) for q in range(R) if joh[q] >= 3 and joh[q] > len(hitap_ayet) * df[q] / N_AYET and gh[q] >= G2_ESIK}
ayna = []
for ad in PEYGAMBER:
    idx = next(i for i, x in enumerate(isimler) if x[1] == ad)
    ay = sorted(set(isim_yer[next(l for l in isim_yer if lemmalar[l][0] == isimler[idx][0])][k][0] for k in range(isimler[idx][2])))
    es = {q: g_ for q, _, g_ in es_kokler(ay, en_az=2, kac=400)}
    ortak = sorted(((min(es[q], hitap_one[q]), q) for q in es if q in hitap_one and q not in (R_KVL, R_RBB)), reverse=True)
    ayna.append([idx, [q for _, q in ortak[:10]]])
print('hitap ayeti', len(hitap_ayet), 'hitapta öne çıkan kök', len(hitap_one))

# ---- ayet sonu çiftleri
ESMA = {nfd(x) for x in "غَفُور رَحِيم عَزِيز حَكِيم سَمِيع عَلِيم بَصِير غَنِيّ حَمِيد تَوّاب رَءُوف واسِع قَوِيّ رَحْمٰن واحِد قَهّار عَلِيّ كَبِير لَطِيف خَبِير حَلِيم عَفُوّ قَدِير شَكُور غَفّار عَظِيم شاكِر كَرِيم مَجِيد وَدُود بَرّ حَفِيظ وَلِيّ مَلِك قُدُّوس حَيّ قَيُّوم أَحَد صَمَد أَوَّل آخِر ظاهِر باطِن فَتّاح وَهّاب رَزّاق مَتِين حَقّ مُبِين قَرِيب مُجِيب شَهِيد رَقِيب حَسِيب وَكِيل مُقْتَدِر خَلّاق".split()}
cift_grup = collections.OrderedDict()
for gi, ks in enumerate(ayet_kelime):
    if len(ks) < 2:
        continue
    a_, b_ = ks[-2], ks[-1]
    if a_['r'] < 0 or b_['r'] < 0 or a_['l'] < 0 or b_['l'] < 0:
        continue
    ga, gb = govde(a_), govde(b_)
    if not ga or not gb or ga[0] != 'N' or gb[0] != 'N' or var(a_, 'PRON') or var(b_, 'PRON') or var(a_, 'DET') != var(b_, 'DET'):
        continue
    cift_grup.setdefault((a_['l'], b_['l']), []).append(gi)
cift = []
for (la, lb), ay in sorted(cift_grup.items(), key=lambda kv: -len(kv[1])):
    if len(ay) < 3:
        continue
    esma = 1 if nfd(lemmalar[la][0]) in ESMA and nfd(lemmalar[lb][0]) in ESMA else 0
    cift.append([la, lb, len(ay), esma, md(ay), es_kokler(ay, dis=(lemmalar[la][1], lemmalar[lb][1]), kac=8), ay])
print('ayet sonu çifti', len(cift), 'esmâ', sum(1 for c_ in cift if c_[3]))

# ---- sorular
soru_grup = collections.OrderedDict()
ham_lem = {}
for satir in open(os.path.join(KAYNAK, 'morph.txt'), encoding='utf8'):
    pp = satir.rstrip('\n').split('\t')
    if len(pp) == 4 and 'INTG' in pp[3].split('|'):
        s_, a_, k_, _ = (int(x) for x in pp[0].split(':'))
        l_ = next((x[4:] for x in pp[3].split('|') if x.startswith('LEM:')), '?')
        soru_grup.setdefault(l_, []).extend([BAS[s_ - 1] + a_ - 1, k_ - 1])
soru = [[k, len(v) // 2, v] for k, v in sorted(soru_grup.items(), key=lambda kv: -len(kv[1]))]
soru_ayet = {gi for _, _, v in soru for gi in v[0::2]}
soru_sure = [sum(1 for gi in range(BAS[s], BAS[s + 1]) if gi in soru_ayet) for s in range(114)]
print('soru edatı', sum(x[1] for x in soru), 'ayet', len(soru_ayet))

# ---- kelimelerin doğum tarihi
nuzul_sira = sorted(range(114), key=lambda s: NUZUL[s])
dogum = [-1] * R
for s in nuzul_sira:
    for r in np.nonzero(RS[s])[0]:
        if dogum[r] < 0:
            dogum[r] = s

# ---- dualar
dua = []
for gi, ks in enumerate(ayet_kelime):
    ses = -1
    for wi, w in enumerate(ks):
        ps = parcalar(w)
        if w['r'] == R_RBB:
            g = govde(w)
            bos1s = any('PRON' in p_ and '1S' in p_ for p_ in ps) and w['p'][1::2][-1] == 0
            rabbena = 'ACC' in g and any('PRON' in p_ and '1P' in p_ for p_ in ps) and not any('PREF' in p_ for p_ in ps)
            if bos1s or rabbena:
                ses = wi
        elif nfd(lem_ad(w)) == nfd('اللَّهُمَّ'):
            ses = wi
        elif ses >= 0:
            g = govde(w)
            if g and g[0] == 'V' and '2MS' in g and ('IMPV' in g or ('IMPF' in g and var(ks[wi - 1], 'PRO'))):
                dua += [gi, ses, wi, w['l'], 1 if 'IMPF' in g else 0]
                ses = -2
    del ses
print('dua (sesleniş + istek)', len(dua) // 5)

# ---- sayım denetçisi
def kok_tablosu(k):
    r = kok_id.get(k)
    if r is None:
        return None
    sat = collections.OrderedDict()
    for ks in ayet_kelime:
        for w in ks:
            if w['r'] != r:
                continue
            g = govde(w)
            if g[0] == 'V':
                zaman = next((z for z in ('PERF', 'IMPF', 'IMPV') if z in g), '')
                sahis = next((x for x in g if re.match(r'^[123]', x)), '')
                anahtar = (w['l'], 'V', zaman + ' ' + sahis)
                sayi = 0
            else:
                cins = 'dişil' if any(x in g for x in ('F', 'FS', 'FD', 'FP')) else 'eril' if any(x in g for x in ('M', 'MS', 'MD', 'MP')) else ''
                anahtar = (w['l'], 'N', cins)
                sayi = 2 if any(x in g for x in ('MP', 'FP', 'P')) else 1 if any(x in g for x in ('MD', 'FD', 'D')) else 0
            d = sat.setdefault(anahtar, [0, 0, 0, 0])
            d[sayi] += 1
            if len(w['p']) // 2 > 1 and any('SUFF' in p_ for p_ in parcalar(w)):
                d[3] += 1
    return [int(kok_n[r]), [[l, t, e] + d for (l, t, e), d in sorted(sat.items(), key=lambda kv: -sum(kv[1][:3]))]]


IDDIA = [['Dünya ve âhiret eşit sayıda geçer', [['Dünya', 'دنو', 115], ['Âhiret', 'أخر', 115]]],
         ['Melek ve şeytan eşit sayıda geçer', [['Melek', 'ملك', 88], ['Şeytan', 'شطن', 88]]],
         ['Hayat ve ölüm eşit sayıda geçer', [['Hayat', 'حيي', 145], ['Ölüm', 'موت', 145]]],
         ['Tekil "gün" 365 kez geçer', [['Gün (yevm)', 'يوم', 365]]],
         ['"Ay" (şehr) 12 kez geçer', [['Ay (şehr)', 'شهر', 12]]],
         ['Erkek ve kadın eşit sayıda geçer', [['Erkek (racül)', 'رجل', 24], ['Kadın (imrae)', 'مرأ', 24]]],
         ['"De" ve "dediler" eşit sayıda geçer', [['Demek (kavl)', 'قول', 332]]]]
sayim = []
for baslik, kalemler in IDDIA:
    ks_ = []
    for ad, k, iddia in kalemler:
        t = kok_tablosu(k)
        if t is None:
            print('  kök yok:', k)
            continue
        ks_.append([ad, kok_id[k], iddia] + t)
    sayim.append([baslik, ks_])

yaz_ek = {'emir': emir, 'kul': kul_yer, 'kulSonra': kul_sonra, 'kulMd': md(kul_ayet),
          'rabbuke': rabbuke, 'rabbukeEs': es_kokler(rabbuke_ayet, dis=(R_RBB,), kac=16), 'rabbukeMd': md(rabbuke_ayet),
          'nida': nida, 'ar': allah_resul, 'ayna': ayna, 'hitapAyet': len(hitap_ayet),
          'cift': cift, 'soru': soru, 'soruSure': soru_sure, 'dogum': dogum, 'dua': dua, 'sayim': sayim}

# ---------------------------------------------------------------- yaz
os.makedirs(CIKTI, exist_ok=True)


def yaz(ad, veri):
    yol = os.path.join(CIKTI, ad)
    with open(yol, 'w', encoding='utf8') as f:
        json.dump(veri, f, ensure_ascii=False, separators=(',', ':'))
    print(ad, os.path.getsize(yol) // 1024, 'KB')


rs_seyrek = []
for r in range(R):
    d = []
    for s in np.nonzero(RS[:, r])[0]:
        d += [int(s), int(RS[s, r])]
    rs_seyrek.append(d)

yaz('core.json', {
    'sayim': {'ayet': N_AYET, 'kelime': N_KELIME, 'kok': R, 'lemma': len(lemmalar),
              'koklu': int(TOPLAM), 'mealBirim': U, 'mealBirim2': len(MEAL2['t']), 'akrabaEsik': 0.30, 'g2Esik': G2_ESIK},
    'sure': [[SURE_ADLARI[s], AD_AR[s], AYET_SAYISI[s], MEKKI[s], NUZUL[s]] for s in range(114)],
    'kok': kokler, 'kokN': [int(x) for x in kok_n], 'kokDf': [int(x) for x in kok_df],
    'lem': lemmalar, 'lemN': [lem_n[i] for i in range(len(lemmalar))],
    'rs': rs_seyrek, 'parmak': parmak, 'komsu': komsu,
    'gram': gram, 'fasila': fasila, 'ritim': ritim,
    'yoldas': yoldas, 'karsilik': karsilik, 'karsilik2': karsilik2, 'duzeltme': DUZELTMELER,
    'kayma': kayma, 'isim': isimler, 'kalip': kalip_cikti, 'kalipToplam': kalip_toplam,
})
yaz('ar.json', [' '.join(w['m'] for w in ks) for ks in ayet_kelime])
yaz('meal.json', MEAL1)
yaz('meal2.json', MEAL2)
yaz('morph.json', {'et': etiketler, 'w': [[[w['r'], w['l']] + w['p'] for w in ks] for ks in ayet_kelime]})
yaz('rel.json', akraba)
yaz('ek.json', yaz_ek)

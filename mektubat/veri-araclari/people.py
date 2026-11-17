import json,re,sys
D=sys.argv[1]; OUT=sys.argv[2]
F=json.load(open(D+'/fa.json'))['L'];A=json.load(open(D+'/ak.json'))['L'];AR=json.load(open(D+'/ar.json'))['L'];I=json.load(open(D+'/index.json'))
DROP=re.compile(r'[ً-ٰٟـ«»]')
def n(s): return re.sub(r'\s+',' ',DROP.sub('',s).replace('ی','ي').replace('ک','ك').replace('ى','ي').replace('ة','ه').replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ج ','ج ')).replace('قليج','قليچ')
# (id, Türkçe ad, Farsça ad, desenler) — sıra önemli: özel kurallar önce
P=[
('numan_abdurrahman',"Mîr Abdurrahmân (Mîr Nu'mân'ın oğlu)","مير عبد الرحمن ولد مير محمد نعمان",[r'عبد الرحمن (ولد|ابن|بن) مير محمد نعمان']),
('numan_abdullah',"Abdullah (Mîr Nu'mân'ın oğlu)","عبد الله ابن مير محمد نعمان",[r'عبد الله (ولد|ابن|بن) مير محمد نعمان']),
('numan_child',"Mîr Nu'mân'ın oğullarından biri","يكي از فرزندان مير محمد نعمان",[r'فرزندان مير محمد نعمان']),
('numan_murad',"Muhammed Murâd Keşmî (Mîr Nu'mân'ın hizmetkârı)","محمد مراد كشمي",[r'محمد مراد كشمي']),
('amin_mother',"Mîr Muhammed Emîn'in annesi","والده مير محمد امين",[r'والده مير محمد امين']),
('husam_jamal',"Hâce Cemâleddin Hüseyin (Hüsâmeddin Ahmed'in oğlu)","خواجه جمال الدين حسين",[r'جمال الدين حسين']),
('masum_kabuli',"Muhammed Ma'sûm Kâbilî","محمد معصوم كابلي",[r'معصوم كابلي']),
('sadiq_kashmiri',"Mevlânâ Muhammed Sâdık Keşmîrî","مولانا محمد صادق كشميري",[r'صادق كشميري']),
('sadiq_kabuli',"Muhammed Sâdık Kâbilî","محمد صادق كابلي",[r'صادق كابلي']),
('sadiq_mumin',"Muhammed Sâdık (Hacı Muhammed Mü'min'in oğlu)","محمد صادق ولد حاجي محمد مؤمن",[r'محمد صادق ولد حاجي محمد مومن',r'محمد صادق ولد حاجي محمد مؤمن']),
('mumin_alikhan',"Muhammed Mü'min (Ali Han'ın oğlu)","محمد مؤمن ولد خواجه عليخان",[r'مؤمن ولد',r'مومن ولد']),
('farid_thanesari',"Şeyh Ferîd Tehânîserî","شيخ فريد تهانيسري",[r'فريد تهانيسري']),
('farid_ranhuni',"Ferîd Rânhûnî","فريد رانهوني",[r'فريد رانهوني']),
('ismail_faridabadi',"İsmâil Ferîdâbâdî","اسماعيل فريد ابادي",[r'اسماعيل فريد']),
('darab',"Mirza Dârâb (Hân-ı Hânân'ın oğlu)","ميرزا داراب",[r'داراب']),
('qilichullah',"Mirza Kılıçullah (Kılıç Han'ın oğlu)","ميرزا قليچ الله",[r'قليچ ?الله']),
('tahir_lahori',"Molla Tâhir Lâhorî","ملا طاهر لاهوري",[r'طاهر لاهوري']),
('nur_anbali',"Nur Muhammed Ambâlevî","نور محمد انبالي",[r'نور محمد انبالي']),
('nur_tihari',"Şeyh Nur Muhammed Tihârî","شيخ نور محمد تهاري",[r'نور محمد (ال)?تهاري',r'نور محمد التهاري']),
('pirzade_ubeydullah',"Hâce Ubeydullah (şeyhinin oğlu)","خواجه عبيد الله",[r'عبيد الله']),
('pirzade_abdullah',"Hâce Muhammed Abdullah (şeyhinin oğlu)","خواجه محمد عبد الله",[r'پير ?زاد\S* (?:اعني )?(?:حضرت ايشان )?خواجه (?:محمد )?عبد الله',r'محمد عبد الله']),
('baki',"Hâce Muhammed Bâkîbillah (şeyhi)","خواجه محمد باقي بالله",[r'^PIR$',r'پير بزرگوار',r'باقي بالله']),
('masum',"Hâce Muhammed Ma'sûm (oğlu)","خواجه محمد معصوم",[r'محمد ?معصوم',r'مخدوم محمد معصوم']),
('said',"Hâce Muhammed Sa'îd (oğlu)","خواجه محمد سعيد",[r'محمد ?سعيد']),
('sadiq_son',"Hâce Muhammed Sâdık (oğlu)","خواجه محمد صادق",[r'(مخدوم ?زاد|ميان)\S*.*?محمد صادق',r'ميان (شيخ |خواجه )?محمد صادق']),
('numan',"Mîr Muhammed Nu'mân Bedahşî","مير محمد نعمان",[r'نعمان']),
('hashim',"Hâce Muhammed Hâşim Keşmî","خواجه محمد هاشم كشمي",[r'هاشم']),
('husam',"Mirza Hüsâmeddin Ahmed","ميرزا حسام الدين احمد",[r'حسام الدين']),
('farid',"Şeyh Ferîd Buhârî","شيخ فريد بخاري",[r'فريد']),
('khankhanan',"Abdürrahîm Hân-ı Hânân","عبد الرحيم خان خانان",[r'خان ?خانان']),
('qilichkhan',"Kılıç Han","قليچ خان",[r'قليچ']),
('jabbari',"Cebbârî Han","جباري خان",[r'جباري ?خان']),
('sadrjahan',"Sadr-ı Cihân","صدر جهان",[r'صدر جهان']),
('khanjahan',"Hân-ı Cihân","خان جهان",[r'خان جهان']),
('khwajajahan',"Hâce Cihân","خواجه جهان",[r'خواجه جهان',r'^جهان$']),
('khanazam',"Hân-ı A'zam","خان اعظم",[r'خان اعظم']),
('sikandar',"İskender Han Lûdî","سكندر خان لودي",[r'سكندر خان']),
('khizr_lodi',"Hızır Han Lûdî","خضر خان لودي",[r'خضر خان']),
('khizr_afghan',"Hızır Afgan","خضر افغان",[r'خضر افغان']),
('fathullah',"Mirza Fethullah Hakîm","ميرزا فتح الله حكيم",[r'فتح ال(له|هد) (ال)?حكيم']),
('badiuddin',"Şeyh Bedîüddin Sehârenpûrî","شيخ بديع الدين سهارنپوري",[r'بديع الدين']),
('badiuzzaman',"Bedîüzzamân","بديع الزمان",[r'بديع الزمان']),
('ahmad_barki',"Mevlânâ Ahmed Berkî","مولانا احمد بركي",[r'احمد (ال)?بركي']),
('yusuf_barki',"Mevlânâ Yûsuf Berkî","مولانا يوسف بركي",[r'يوسف بركي']),
('hasan_barki',"Mevlânâ Hasan Berkî","مولانا حسن بركي",[r'حسن بركي']),
('muhibbullah',"Mîr Muhibbullah Mânikpûrî","مير محب الله مانكپوري",[r'محب الله']),
('tahir',"Mevlânâ Muhammed Tâhir Bedahşî","مولانا محمد طاهر بدخشي",[r'طاهر (ال)?بدخشي',r'محمدطاهر بدخشي']),
('siddiq_badakhshi',"Mevlânâ Muhammed Sıddîk Bedahşî","مولانا محمد صديق بدخشي",[r'صديق بدخشي']),
('siddiq',"Muhammed Sıddîk","محمد صديق",[r'محمد (ال)?صديق']),
('ashraf',"Hâce Muhammed Eşref Kâbilî","خواجه محمد اشرف كابلي",[r'محمد اشرف']),
('hasan_kashmiri',"Molla Hasan Keşmîrî","ملا حسن كشميري",[r'حسن كشميري']),
('hasan_dehlavi',"Mevlânâ Hasan Dehlevî","مولانا حسن دهلوي",[r'حسن (ال)?دهل']),
('chitri',"Muhammed Çitrî","محمد چتري",[r'محمد چتري']),
('mahdi_chitri',"Mehdî Çitrî","مهدي چتري",[r'مهدي چتري']),
('muzammil',"Şeyh Miyân Müzzemmil","شيخ ميان مزمل",[r'مزمل']),
('yar_qadim',"Yâr Muhammed Kadîm Bedahşî","يار محمد قديم بدخشي",[r'يار محمد (ال)?قديم']),
('yar_jadid',"Yâr Muhammed Cedîd Bedahşî Tâlekânî (1. defteri derleyen)","يار محمد الجديد البدخشي الطالقاني",[r'يار محمد (ال)?جديد']),
('abdulghafur',"Molla Abdülgafûr Semerkandî","ملا عبد الغفور سمرقندي",[r'عبد الغفور',r'عبد الفغور']),
('sharafuddin',"Hâce Şerefeddin Hüseyin Bedahşî","خواجه شرف الدين حسين",[r'شرف الدين حسين']),
('abdulwahid',"Mevlânâ Abdülvâhid Lâhorî","مولانا عبد الواحد لاهوري",[r'عبد الواحد']),
('abdulhay',"Mevlânâ Abdülhay (2. defteri derleyen)","عبد الحي",[r'عبد الحي']),
('abdulqadir_anbali',"Mevlânâ Abdülkâdir Ambâlevî","مولانا عبد القادر انبالي",[r'عبد القادر انبالي']),
('nizam',"Şeyh Nizâm Tehânîserî","شيخ نظام تهانيسري",[r'نظام تهانيسري']),
('amak',"Hâce Amık","خواجه عمك",[r'عمك']),
('pahlavan',"Pehlivan Mahmûd","پهلوان محمود",[r'پهلوان محمود']),
('hafiz_mahmud',"Hâfız Mahmûd Lâhorî","حافظ محمود لاهوري",[r'حافظ محمود']),
('sayyid_mahmud',"Seyyid Mahmûd","سيد محمود",[r'سيد محمود']),
('muhammad_lahori',"Mevlânâ Hacı Muhammed Lâhorî","مولانا حاجي محمد لاهوري",[r'محمد (ال)?لاهوري']),
('qasim',"Hâce Muhammed Kâsım","خواجه محمد قاسم",[r'محمد قاسم']),
('hamid_bengali',"Mevlânâ Hamîd Bengâlî","مولانا حميد بنگالي",[r'حميد بنگالي']),
('salih_kulabi',"Mevlânâ Muhammed Sâlih Kûlâbî","مولانا محمد صالح كولابي",[r'صالح (بدخشي )?كولابي']),
('mansur_arab',"Mansûr Arab","منصور عرب",[r'منصور عرب']),
('mansur',"Mîr Mansûr","مير منصور",[r'منصور']),
('shakibi',"Şekîbî İsfahânî","شكيبي اصفهاني",[r'شكيبي']),
('badruddin',"Mevlânâ Bedreddin (Serhendî)","مولانا بدر الدين",[r'بدر الدين']),
('amanullah',"Mevlânâ Emânullah","مولانا امان الله",[r'امان الله']),
('farkati',"Mevlânâ Hacı Muhammed Ferketî","مولانا حاجي محمد فركتي",[r'فركتي']),
('taqi',"Hâce Muhammed Takî","خواجه محمد تقي",[r'محمد تقي']),
('sultan_sirhindi',"Mevlânâ Sultan Serhendî","مولانا سلطان سرهندي",[r'سلطان (ال)?سرهندي']),
('khalkhali',"Mîr Şemseddin Ali Halhâlî","مير شمس الدين علي خلخالي",[r'شمس الدين علي',r'خلخالي']),
('mirza_shams',"Mirza Şemseddin","ميرزا شمس الدين",[r'ميرزا شمس الدين']),
('molla_shams',"Molla Şems(eddin)","ملا شمس",[r'ملا شمس']),
('ibrahim_qubadiyani',"İbrâhim Kubâdiyânî","ابراهيم قبادياني",[r'ابراهيم قبادياني']),
('maqsud',"Maksûd Ali Tebrîzî","مقصود علي تبريزي",[r'مقصود']),
('yusuf_kashmiri',"Hacı Muhammed Yûsuf Keşmîrî","حاجي محمد يوسف كشميري",[r'يوسف (ال)?كشميري',r'حاجي يوسف']),
('abdulwahhab',"Abdülvehhâb Buhârî","عبد الوهاب بخاري",[r'عبد الوهاب']),
('mumin_balkhi',"Mîr Mü'min Belhî","مير مؤمن بلخي",[r'مؤمن بلخي',r'مومن بلخي']),
('sufi_qurban',"Sûfî Kurbân","صوفي قربان",[r'صوفي قربان']),
('salih_nishapuri',"Mîr Sâlih Nîşâbûrî","مير صالح نيشابوري",[r'صالح نيشابوري',r'ميرصالح']),
('abdurrahman_mufti',"Abdurrahmân Müftî Kâbilî","عبد الرحمن مفتي كابلي",[r'عبد الرحمن مفتي']),
('baha_sirhindi',"Hâfız Bahâeddin Serhendî","حافظ بهاء الدين سرهندي",[r'بهاء الدين سرهندي']),
('muhammad_amin_kabuli',"Muhammed Emîn Kâbilî","محمد امين كابلي",[r'محمد امين']),
('mawdud',"Miyân Muhammed Mevdûd (kardeşi)","ميان محمد مودود",[r'مودود']),
('ghulam',"Miyân Gulâm Muhammed (kardeşi)","ميان غلام محمد",[r'غلام محمد']),
('salih_turk',"Sâlih Türk","صالح ترك",[r'صالح ترك']),
('sultan',"Zamanın sultanı (Cihângîr)","سلطان وقت",[r'سلطان وقت']),
('abdulhaq',"Şeyh Abdülhak Dehlevî","شيخ عبد الحق دهلوي",[r'عبد الحق (ال)?دهلوي']),
('saliha',"Salih bir hanım","يكي از صالحات",[r'صالحات',r'صالحه از اهل ارادت']),
]
P.append(('barki_ashab',"Mevlânâ Ahmed Berkî'nin yârenleri","ياران مولانا احمد بركي",[r'^$NEVER']))
P.append(('samana',"Sâmâne'nin seyyidleri, kadıları ve halkı","سادات و قضاة و اهالى بلده سامانه",[r'^$NEVER']))
P.append(('nevahi_seyh',"Çevredeki şeyhlerden biri","يكى از مشايخ نواحى",[r'^$NEVER']))
# 1/30: Farsça başlıkta alıcı yok; Arapça tercümenin başlığı Şeyh Nizâm Tehânîserî'yi verir
OVR={'1-234':['sadiq_son'],'2-61':['barki_ashab'],'2-15':['samana'],'2-53':['nevahi_seyh'],'1-30':['nizam']}
RX=[(i,tr,fa,[re.compile(p) for p in ps]) for i,tr,fa,ps in P]
def fa_phrase(k):
    t=n(F[k]['t']+' '+(F[k]['p'][0] if F[k]['p'] else ''))[:300]
    if 'پير بزرگوار' in t: return 'PIR'
    return t
def ar_phrase(k):
    a=AR.get(k); 
    if not a: return ''
    t=n(a['t'])
    m=re.search(r'(?:الي|إلى|إلي)\s+(.{2,120}?)\s+(?:في|فى)\s',t)
    if re.search(r'الي شيخه',t): return 'PIR'
    return m.group(1) if m else ''
def match(text):
    found=[]; t=text
    for i,tr,fa,rxs in RX:
        for r in rxs:
            m=r.search(t)
            if m:
                found.append(i); t=t[:m.start()]+' # '+t[m.end():]; break
    return found
ORD=set('اول دوم سوم چهارم پنجم ششم هفتم هشتم نهم دهم يازدهم دوازدهم سيزدهم چهاردهم پانزدهم شانزدهم هفدهم هيجدهم هجدهم نوزدهم بيستم بيست سي سى ام سي‌ام چهلم چهل پنجاهم پنجاه پنچاه شصتم شصت هفتادم هفتاد هشتادم هشتاد نودم نود صدم صد دويستم دويست سيصدم سيصد و يكم يكم دويم سيوم صدو صدوبيست ديوم'.split())
def recipient_span(t):
    if t=='PIR': return t
    w=t.split()
    i=0
    while i<len(w) and (w[i] in ('مكتوب','مكتوبات') or w[i].rstrip(':') in ORD or w[i]==':'): i+=1
    t=' '.join(w[i:]).lstrip(': ')
    m=re.search(r'(?:^|\s)(?:نيز\s+)?(?:به|بـ|ب(?=\S)|ارسل\s+الي|الي|هذا المكتوب ارسل الي)\s*(.{2,200}?)(?:\s+(?:صدور|ورود|درود|نوشته|ارسال|املاء|في|فى)\b|\s+در(?:\s|بيان)|$)',t)
    return m.group(1).strip(' ،:') if m else ''
def tr_note(k):
    t=((A.get(k) or {}).get('not') or '')
    m=re.search(r'bu mektubu,?\s*(.+?)\s*(?:yazmıştır|göndermiştir|yazılmıştır)',t,re.I)
    return m.group(1).strip() if m else ''
people={i:{'id':i,'tr':tr,'fa':fa,'L':[]} for i,tr,fa,_ in RX}
by={}; src={}; unk=[]
prev=None
for k in I['order']:
    fp=fa_phrase(k); span=recipient_span(fp)
    ids=match(span) if span else []
    if k in OVR: ids=OVR[k]
    s='fa'
    if not ids:
        ap=ar_phrase(k); ids=match(ap) if ap else []
        s='ar'
    if not ids and span:
        # sözlükte olmayan alıcı: Farsça ifadeyi kişi olarak al
        nm=re.sub(r'\s+',' ',span).strip(' ،')
        if 3<len(nm)<70 and not re.search(r'(^|\s)(بيان|تحقيق|سبب|كمالات)(\s|$)',nm):
            import hashlib; pid='x'+hashlib.md5(nm.encode()).hexdigest()[:8]
            trn=re.sub(r"[`'’]?(y?[ae]|n[ae])$","",tr_note(k)).strip(' .`,;')
            people.setdefault(pid,{'id':pid,'tr':trn or nm,'fa':nm,'L':[],'auto':True}); ids=[pid]; s='fa'
    if not ids:
        unk.append(k); s=None
    for i in ids: people[i]['L'].append(k)
    by[k]=ids; src[k]=s
people={i:p for i,p in people.items() if p['L']}
json.dump({'people':list(people.values()),'by':by,'src':src},open(OUT,'w'),ensure_ascii=False,separators=(',',':'))
print('persons',len(people),'unknown',len(unk),unk)
top=sorted(people.values(),key=lambda p:-len(p['L']))
for p in top[:45]: print(len(p['L']),p['id'],p['tr'])
print('auto persons:',sum(1 for p in people.values() if p.get('auto')))
for p in people.values():
    if p.get('auto'): print('  A',p['L'],'|',p['fa'],'|',p['tr'])

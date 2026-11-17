import json,re,sys
D=sys.argv[1]
F=json.load(open(D+'/fa.json'))['L'];AR=json.load(open(D+'/ar.json'))['L'];I=json.load(open(D+'/index.json'))
DROP=re.compile(r'[ً-ٰٟـۖ-ۭؐ-ؚ‌‏‎]')
MAP=str.maketrans({'ی':'ي','ى':'ي','ئ':'ي','ک':'ك','ة':'ه','ۀ':'ه','أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ؤ':'و'})
def norm(s): return DROP.sub('',s).translate(MAP)
L=r'[ء-يٱ-ۓ]'
PRE=r'(?:و|ف|ب|ل|ك)?(?:ال|لل)?'
def rx(core,suf=r'(?:ه|ي|ها|هاي|ات|يه|يت|ش|هم|نا|كم)?'):
    return '(?<!'+L+')'+PRE+'(?:'+core+')'+suf+'(?!'+L+')'
# id, Türkçe, Farsça çekirdek, Arapça çekirdek, kısa açıklama
T=[
('fena','Fenâ','فناء?','فناء?','Kulun kendi varlığından geçmesi'),
('beka','Bekâ','بقاء?','بقاء?','Fenâdan sonra Hak ile kalış'),
('cezbe','Cezbe','جذبه|جذبات','جذبه|جذبات','İlâhî çekiliş'),
('suluk','Sülûk','سلوك','سلوك','Yolda adım adım ilerleyiş'),
('uruc','Urûc','عروج|عروجات','عروج|عروجات','Yükseliş'),
('nuzul','Nüzûl','نزول','نزول','Halka dönüş, iniş'),
('zill','Zıll (gölge)','ظل|ظلال|ظليت|ظليه','ظل|ظلال|ظليه','Asıl ile gölgesi ayrımı'),
('vucudi','Vahdet-i vücûd','وحدت (?:ال)?وجود|توحيد وجودي','وحده الوجود|التوحيد الوجودي','Varlık birliği'),
('suhudi','Tevhîd-i şühûdî','توحيد شهودي|وحدت شهود','التوحيد الشهودي|وحده الشهود','Görüş birliği'),
('velayet','Velâyet','ولايت|ولايات','ولايه|ولايات','Velîlik'),
('nubuvvet','Nübüvvet','نبوت','نبوه','Peygamberlik ve kemâlâtı'),
('sunnet','Sünnet','سنت|سنن','السنه|سنن','Sünnete uymak'),
('bidat','Bid\'at','بدعت|بدعات|بدع','بدعه|بدع','Dine sonradan katılan'),
('seriat','Şeriat','شريعت|شرايع|شرع','شريعه|شرايع|شرع','Dinin hükümleri'),
('tarikat','Tarîkat','طريقت|طريقه','طريقه','Yol, tasavvuf yolu'),
('hakikat','Hakîkat','حقيقت|حقايق','حقيقه|حقايق','Özün özü'),
('zikir','Zikir','ذكر|اذكار','ذكر|اذكار','Anma (Arapçada "anılan" anlamıyla karışabilir)'),
('rabita','Râbıta','رابطه','رابطه','Mürşide gönül bağı'),
('tecelli','Tecellî','تجلي|تجليات','تجلي|تجليات','Görünüş, zuhûr'),
('kurb','Kurb','قرب','قرب','Yakınlık'),
('marifet','Ma\'rifet','معرفت|معارف','معرفه|معارف','Bilen bilgi'),
('letaif','Letâif','لطيفه|لطايف|لطائف','لطيفه|لطايف|لطائف','İnsandaki ince idrak merkezleri'),
('kalb','Kalb','قلب|قلوب','قلب|قلوب','Gönül'),
('nefs','Nefs','نفس','نفس','Nefis (Arapçada "kendisi" anlamıyla karışabilir)'),
('kesf','Keşf','كشف|كشوف','كشف|كشوف','Perdenin açılması'),
('yakin','Yakîn','يقين','يقين','İlme\'l-, ayne\'l-, hakka\'l-yakîn'),
('mahabbet','Muhabbet','محبت|محبوبيت|محبيت','محبه|محبوبيه|محبيه','Sevgi'),
('istikamet','İstikamet','استقامت','استقامه','Doğruluk üzere oluş'),
('abdiyet','Abdiyet','عبديت|عبوديت','عبديه|عبوديه','Kulluk makamı'),
('hayret','Hayret','حيرت','حيره','Şaşkınlık hâli'),
('namaz','Namaz','نماز|صلاه(?!\\s*و\\s*(?:ال)?(?:سلام|تحيه|تحيات|تسليم|تسليمات|بركات))','صلاه(?!\\s*و\\s*(?:ال)?(?:سلام|تحيه|تحيات|تسليم|تسليمات|بركات))','Namaz (salavat kalıbı «es-salâtü ve\'s-selâm» sayılmaz)'),
('kuran','Kur\'ân','قران|كلام مجيد|كلام الله','القران|كلام الله','Kur\'ân'),
]
out={'terms':[],'counts':{}}
fa_n={k:norm(F[k]['t']+'\n'+'\n'.join(F[k]['p'])) for k in I['order']}
ar_n={k:norm(AR[k]['t']+'\n'+'\n'.join(AR[k]['p'])) for k in I['order'] if k in AR}
for tid,tr,fa,ar,desc in T:
    rf=re.compile(rx(fa)); ra=re.compile(rx(ar))
    cf={k:len(rf.findall(v)) for k,v in fa_n.items()}; ca={k:len(ra.findall(v)) for k,v in ar_n.items()}
    out['terms'].append({'id':tid,'tr':tr,'desc':desc,'fa':fa,'ar':ar,'rxfa':rx(fa),'rxar':rx(ar),'tfa':sum(cf.values()),'tar':sum(ca.values())})
    out['counts'][tid]={'fa':[cf[k] for k in I['order']],'ar':[ca.get(k,0) for k in I['order']]}
    print(f"{tr:18} FA {sum(cf.values()):5}  AR {sum(ca.values()):5}  letters FA {sum(1 for v in cf.values() if v)}")
json.dump(out,open(D+'/atlas.json','w'),ensure_ascii=False,separators=(',',':'))

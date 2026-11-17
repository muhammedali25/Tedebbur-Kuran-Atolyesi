import json,re,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from trparse import parse_ak,parse_hk
S=sys.argv[1]; OUT=sys.argv[2]
ar=json.load(open(S+'/data/ar_letters.json')); fa=json.load(open(S+'/data/fa_letters.json'))
def pgs(pages):
    ps=[(a,b) for a,b in pages if b]
    if not ps: return ''
    (p1,a),(p2,b)=ps[0],ps[-1]
    return f"c.{p1} s.{a}" + (f"–{b}" if b!=a else '') if p1==p2 else f"c.{p1} s.{a} – c.{p2} s.{b}"
def shamela(l):
    lines=[x.strip() for x in l['text'].split('\r')]
    lines=[x for x in lines if x]
    t=lines[0]; p=lines[1:]
    p=[re.sub(r'\s*[^.]*به تاريخ [^.]*هجرى شمسى به پايان رسيد[^.]*\.?','',x).strip() for x in p]
    p=[x for x in p if x]
    n=[[pg,re.sub(r'\r+','\n',txt).strip()] for pg,txt in l['notes']]
    return {'t':t,'p':p,'n':n,'pg':pgs(l['pages'])}
# Arapça (vol,no) -> Farsça (vol,no)
def ar2fa(v,n):
    if v<3: return (v,n)
    if n<=38: return (3,n)
    if n==39: return (3,40)
    if n==40: return (3,39)
    if n<=114: return (3,n)
    return (3,n+1)
# Akçiçek sıra no -> Arapça (vol,no)
def tr2ar(g):
    if g<=313: return (1,g)
    if g<=412: return (2,g-313)
    return (3,g-412)
key=lambda v,n:f"{v}-{n}"
FA={key(l['vol'],l['no']):shamela(l) for l in fa}
AR={}; idx={key(l['vol'],l['no']):{'fa':key(l['vol'],l['no'])} for l in fa}
for l in ar:
    k=key(*ar2fa(l['vol'],l['no'])); AR[k]=shamela(l); idx[k]['ar']=f"{l['vol']}/{l['no']}"
AK={};HK={};missing=[]
for g in range(1,535):
    f=f"{S}/raw/ak/{g:03d}.htm"
    k=key(*ar2fa(*tr2ar(g)))
    if os.path.exists(f):
        a=parse_ak(f); AK[k]={'t':a['t'],'m':a['m'],'not':a['not'],'p':a['p']}; idx[k]['ak']=g
    else: missing.append(('ak',g))
    h=f"{S}/raw/hk/{g:03d}.htm"
    if os.path.exists(h):
        x=parse_hk(h)
        if x['p']: HK[k]={'t':x['t'],'p':x['p']}; idx[k]['hk']=g
os.makedirs(OUT,exist_ok=True)
def dump(name,obj): 
    json.dump(obj,open(f"{OUT}/{name}.json",'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print(name,len(obj.get('L',obj)),os.path.getsize(f"{OUT}/{name}.json")//1024,'KB')
dump('index',{'order':[key(l['vol'],l['no']) for l in fa],'map':idx})
dump('fa',{'L':FA}); dump('ar',{'L':AR}); dump('ak',{'L':AK}); dump('hk',{'L':HK})
print('missing',len(missing),missing[:5])

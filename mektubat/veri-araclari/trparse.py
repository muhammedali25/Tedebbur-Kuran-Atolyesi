import re,html,json,sys,os
from html.parser import HTMLParser
VERSE={'farsca-metin':'vf','arapca-metin':'vf','latin-okunus':'vl','turkce-meal':'vm'}
class P(HTMLParser):
    """<p>, <br> ve şiir bloklarını koruyarak paragraf listesi çıkarır."""
    def __init__(s):
        super().__init__(); s.paras=[]; s.buf=None; s.skip=0; s.cls=[]; s.vdepth=0; s.vkind=None; s.depth=0
    def flush(s,extra=''):
        if s.buf is None: return
        x=re.sub(r'\s+',' ',''.join(s.buf).replace('\u2028','\x00')).replace(' \x00','\x00').replace('\x00 ','\x00').replace('\x00','\n').strip()
        if x: s.paras.append((x,(' '.join(s.cls)+' '+extra).strip()))
        s.buf=None; s.cls=[]
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in('script','style','audio','form','button'): s.skip+=1
        if t=='div':
            s.depth+=1
            k=VERSE.get((a.get('class') or '').strip())
            if k: s.flush(); s.buf=[]; s.vkind=k; s.vdepth=s.depth
            elif s.vkind is None: s.flush()
        if t=='p' and s.vkind is None: s.flush(); s.buf=[]
        if t=='span' and s.buf is not None and a.get('class'): s.cls.append(a['class'])
        if t=='br' and s.buf is not None: s.buf.append('\u2028')
    def handle_endtag(s,t):
        if t in('script','style','audio','form','button'): s.skip-=1
        if t=='div':
            if s.vkind and s.depth==s.vdepth: s.flush('verse-'+s.vkind); s.vkind=None
            s.depth-=1
        if t=='p' and s.vkind is None: s.flush()
    def handle_data(s,d):
        if s.buf is not None and not s.skip: s.buf.append(d)
    def close(s):
        super().close(); s.flush()
def vfmt(x,c):
    m=re.search(r'verse-(v[flm])',c)
    return ('\u00a7'+m.group(1)+'\u00a7'+x) if m else x
def body(s,start_pat,end_pat):
    i=s.find(start_pat); i=0 if i<0 else i
    j=s.find(end_pat,i); j=len(s) if j<0 else j
    return s[i:j]
def parse_ak(path):
    s=open(path,encoding='utf-8',errors='replace').read()
    title=re.search(r'class="baslik-yesil">(.*?)</span>',s,re.S)
    b=body(s,'class="metin"','Hakîkat Kitâbevi Tercümesi')
    b=b[:b.rfind('<a ')] if b.rfind('<a ')>len(b)-600 else b
    p=P(); p.feed(b); p.close()
    mevzu=[];note=None;rest=[]
    for x,c in p.paras:
        if 'Gece Modu' in x: continue
        if x.startswith('MEVZUU'): continue
        if not rest and 'mavi' in c and not note: mevzu.append(x); continue
        if not rest and x.startswith('NOT:'): note=x; continue
        if not rest and note=='NOT:' : note='NOT: '+x; continue
        rest.append(vfmt(x,c))
    return {'t':html.unescape(title.group(1)).strip() if title else '','m':mevzu,'not':note,'p':rest}
def parse_hk(path):
    s=open(path,encoding='utf-8',errors='replace').read()
    b=body(s,'<body','class="tercume-link"')
    p=P(); p.feed(b); p.close()
    paras=[vfmt(x,c) for x,c in p.paras if x and 'Tarayıcınız' not in x]
    t=paras[0] if paras else ''
    return {'t':t,'p':paras[1:]}
if __name__=='__main__':
    R=sys.argv[1]
    for n in sys.argv[2:]:
        a=parse_ak(f'{R}/ak/{n}.htm'); print('== AK',n,a['t'],'| mevzu',len(a['m']),'| not:',a['not'],'| paras',len(a['p'])); print('   first:',a['p'][0][:120]); print('   last:',a['p'][-1][:120])
        if os.path.exists(f'{R}/hk/{n}.htm'):
            h=parse_hk(f'{R}/hk/{n}.htm'); print('== HK',n,h['t'][:60],'| paras',len(h['p'])); print('   first:',h['p'][0][:120] if h['p'] else None); print('   last:',h['p'][-1][:120] if h['p'] else None)

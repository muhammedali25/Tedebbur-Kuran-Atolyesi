import json,re,sys
NOTE_SEP=re.compile(r'\r_{5,}\r?|\n_{5,}\n?')
def is_letter(t):
    return bool(re.match(r'^\s*(\(\d+\)\s*المكتوب|مكتوب|مکتوب|مكتوب\s*صد)',t))
def load(path,volheads):
    d=json.load(open(path))
    pages=sorted(d['pages'],key=lambda p:int(p['id']))
    # build stream
    stream=[];pos={}
    for p in pages:
        body,_,notes=(p['nass'] or '').partition('\r__________')
        if notes=='' : 
            m=NOTE_SEP.search(p['nass'] or '')
            if m: body,notes=p['nass'][:m.start()],p['nass'][m.end():]
            else: body,notes=p['nass'] or '',''
        pos[int(p['id'])]=sum(len(x[0]) for x in stream)
        stream.append((body+'\r', int(p['id']), p.get('part'), p.get('page'), notes.strip('_\r ')))
    full=''.join(x[0] for x in stream)
    starts=[pos[x[1]] for x in stream]
    DROP=re.compile(r'[\u064B-\u065F\u0670\u0640\u06D6-\u06ED\u0610-\u061A\u200c\u200f\u200e]')
    MAP=str.maketrans({'ی':'ي','ى':'ي','ک':'ك','ة':'ه','أ':'ا','إ':'ا','آ':'ا','ٱ':'ا','ۀ':'ه','ؤ':'و','ئ':'ي'})
    def nchar(c):
        if DROP.match(c) or c in ' \r\n\t()«»[]:.,،؛-_' : return ''
        return c.translate(MAP)
    nfull=[];nmap=[]
    for i,c in enumerate(full):
        r=nchar(c)
        if r: nfull.append(r); nmap.append(i)
    nfull=''.join(nfull)
    import bisect as _b
    def locate(t):
        pid=int(t['id'])
        if pid not in pos: pid=min(pos,key=lambda k:abs(k-pid))
        base=pos[pid]
        nb=_b.bisect_left(nmap,base)
        nt=''.join(nchar(c) for c in t['tit'])
        for L in (40,25,14):
            probe=nt[:L]
            if len(probe)<6: continue
            j=nfull.find(probe,nb,nb+40000)
            if j!=-1:
                i=nmap[j]
                while i>0 and full[i-1] in '(«[': i-=1
                return i
        return base
    toc=d['toc']
    ents=[]
    for t in toc:
        ents.append(dict(t,at=locate(t),letter=is_letter(t['tit'])))
    ents.sort(key=lambda e:(e['at']))
    # volume assignment
    letters=[];vol=0;cnt={}
    import bisect
    for k,e in enumerate(ents):
        if int(e['id']) in volheads and not e['letter']:
            vol=volheads.index(int(e['id']))+1 if int(e['id']) in volheads else vol
        if not e['letter'] or vol==0: continue
        # end = next entry with lvl<=lvl or non-letter appendix heading
        end=len(full)
        for e2 in ents[k+1:]:
            if e2['at']<=e['at']: continue
            if int(e2['lvl'])<=int(e['lvl']) or re.search(r'عريضة|عرضه ?داشت|عرضداشت|فهرس|المجلد|جلد|دفتر',e2['tit']):
                end=e2['at'];break
        cnt[vol]=cnt.get(vol,0)+1
        text=full[e['at']:end]
        # page notes & page markers
        i0=bisect.bisect_right(starts,e['at'])-1; i1=bisect.bisect_right(starts,max(e['at'],end-1))-1
        pg=[(stream[i][2],stream[i][3]) for i in range(i0,i1+1)]
        notes=[ (stream[i][3],stream[i][4]) for i in range(i0,i1+1) if stream[i][4]]
        letters.append({'vol':vol,'no':cnt[vol],'title':e['tit'].strip(),'text':text,'pages':pg,'notes':notes})
    return letters
if __name__=='__main__':
    L=load(sys.argv[1],[int(x) for x in sys.argv[2].split(',')])
    json.dump(L,open(sys.argv[3],'w'),ensure_ascii=False)
    from collections import Counter
    print(sys.argv[3],Counter(l['vol'] for l in L), 'empty:',sum(1 for l in L if len(l['text'])<200))

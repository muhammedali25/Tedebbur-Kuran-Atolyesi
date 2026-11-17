import csv,json,subprocess,sys,io,glob
csv.field_size_limit(10**9)
def tab(f,t):
    out=subprocess.run(['mdb-export','-q','"','-X','"',f,t],capture_output=True).stdout.decode('utf-8','replace')
    return list(csv.DictReader(io.StringIO(out)))
src,dst=sys.argv[1],sys.argv[2]
f=glob.glob(src+'/*.bok')[0]
tabs=subprocess.run(['mdb-tables','-1',f],capture_output=True,text=True).stdout.split()
b=[t for t in tabs if t.startswith('b') and t[1:].isdigit()][0]; ti='t'+b[1:]
d={'main':tab(f,'Main'),'pages':tab(f,b),'toc':tab(f,ti)}
json.dump(d,open(dst,'w',encoding='utf-8'),ensure_ascii=False)
print(dst,len(d['pages']),'pages',len(d['toc']),'toc')

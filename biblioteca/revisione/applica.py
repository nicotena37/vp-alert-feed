import json,re,collections
d=json.load(open('ambiti_articoli.json'))
R=[]
for i in range(4): R+=json.load(open('revisione/report%d.json'%i))
VAL={'tutti','banca','assicurazione','sim','sgr','intermediari','bancoposta','sedi','fondi_pensione','ccp_csd'}
def norm_int(x):
    pr=list(x['proposto'])
    if 'intermediari' in pr:
        t=x['motivo'].lower()
        if not re.search(r'106|intermediari finanziari',t): pr.remove('intermediari')
    return [p for p in pr if p in VAL]
st=collections.Counter();skip=[];amb=[]
for x in R:
    if x['campo']=='ambito':
        if x['certezza']=='alta': st['ambito_alta_da_applicare']+=1
        amb.append(x); continue
    if x['certezza']=='bassa': st['per_bassa_non_applicata']+=1; skip.append(x); continue
    ps=d[x['norma']]['parti']; tg=[]
    m=re.match(r'^(.*?)\s*\[#(\d+)\]\s*$',x['articolo'])
    if m: 
        k=int(m.group(2)); tg=[k] if 0<=k<len(ps) and ps[k]['e']==m.group(1) else []
    else:
        tg=[n for n,p in enumerate(ps) if p['e']==x['articolo']]
        if not tg:
            r=re.match(r'^(?:Art\.\s*)?(\d+)-(\d+)$',x['articolo'])
            if r:
                lo,hi=int(r.group(1)),int(r.group(2))
                for n,p in enumerate(ps):
                    q=re.match(r'^Art\.\s*(\d+)\b',p['e'])
                    if q and lo<=int(q.group(1))<=hi: tg.append(n)
    if not tg: st['non_trovata']+=1; skip.append(x); continue
    new=norm_int(x)
    for n in tg:
        p=ps[n]
        if p.get('per')!=new:
            p.setdefault('per_prima',p.get('per',[])); p['per']=new; p['per_stato']='rivisto_'+x['certezza']
            st['applicata']+=1
json.dump(d,open('ambiti_articoli.json','w'),ensure_ascii=False)
json.dump([x for x in skip],open('revisione/non_applicate.json','w'),ensure_ascii=False,indent=0)
json.dump([x for x in amb],open('revisione/ambito_da_valutare.json','w'),ensure_ascii=False,indent=0)
print(dict(st))

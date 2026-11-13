import json,sys
sys.path.insert(0,'.')
from gruppi import G
a=json.load(open('../adem_ramweuq26q.ORIG.json'))
# adempimenti NON riferiti alle banche (autorità, Stati membri, ESA, fornitori TIC, CSD/CCP)
EX={i for i,x in enumerate(a) if x['sogg']=='altro'}-{335}
EX|={196,202}|set(range(422,430))
for i in sorted(EX): a[i]['_escl']=True
json.dump(sorted(EX),open('esclusi.json','w'))
K=["sanz","rep","oper","econ","compl","freq","nov"]
RINOMINA={"Fornitori critici: designazione, raccomandazioni e cooperazione":("Fornitori critici: seguire le raccomandazioni e sospendere i contratti","Le banche tengono conto delle raccomandazioni dell'autorità di sorveglianza nella gestione dei rischi da terzi, utilizzano fornitori critici di paesi terzi solo se hanno una filiale nell'Unione e sospendono o risolvono i contratti se imposto dall'autorità.")}
out=[]
for tit,desc,idx in G:
    idx=[i for i in idx if i not in EX]
    if not idx: continue
    if tit in RINOMINA: tit,desc=RINOMINA[tit]
    m=[a[i] for i in idx]; p=m[0]
    f={}
    for k in K:
        v=[x['f'][k] for x in m]; f[k]=max(1,min(4,round(.5*max(v)+.5*sum(v)/len(v))))
    f['ctrl']=2; f['att']=max(2,round(sum(x['f']['att'] for x in m)/len(m)))
    sanz=next((x['sanz_txt'] for x in m if x.get('sanz_txt')),'')
    ter=[]
    for x in m:
        t=(x.get('termine') or '').strip()
        if t and t not in ter: ter.append(t)
    termine=ter[0] if len(ter)==1 else ('Vari: vedi le fonti' if ter else '')
    comp=' '.join('• '+x['titolo'].rstrip('.')+'.' for x in m) if len(m)>1 else ''
    out.append({"norma":p['norma'],"art":p['art'],"comma":p['comma'],"titolo":tit,
      "desc":desc+((' Comprende: '+comp) if comp else ''),
      "dest":p['dest'],"termine":termine,
      "natura":'obbligatorio' if any(x['natura']=='obbligatorio' for x in m) else p['natura'],
      "sogg":'banca',"cit":p['cit'],"citOk":bool(p.get('citOk')),
      "f":f,"sanz_txt":sanz,"S":0,"C":0,"lv":"prescrizioni","pres":[],"stato":None,"val":False,
      "fonti":[{k:x[k] for k in('norma','art','comma','cit')} for x in m]})
for n,x in enumerate(out,1): x['_id']='a%03d'%n
json.dump(out,open('/home/claude/ra_build/data/adem_ramwf8f1hm.json','w'),ensure_ascii=False)
pun=[x for i,x in enumerate(a) if i not in EX]
for x in pun: x.pop('_escl',None)
json.dump(pun,open('/home/claude/ra_el/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(pun,open('/home/claude/ra_build/data/adem_ramweuq26q.json','w'),ensure_ascii=False)
print(len(EX),'esclusi;',len(pun),'puntuali;',len(out),'prescrizioni;',sum(len(x['fonti']) for x in out))
ids=['a%03d'%(i+1) for i in sorted(EX)]; json.dump(ids,open('esclusi_ids.json','w')); print(ids)

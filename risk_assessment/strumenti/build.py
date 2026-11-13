import json,sys
sys.path.insert(0,'.')
from gruppi import G
a=json.load(open('../adem_ramweuq26q.ORIG.json'))
# adempimenti NON riferiti alle banche (autorità, Stati membri, ESA, fornitori TIC, CSD/CCP)
EX={i for i,x in enumerate(a) if x['sogg']=='altro'}-{335}
EX|={196,202}|set(range(422,430))
for i in sorted(EX): a[i]['_escl']=True
json.dump(sorted(EX),open('esclusi.json','w'))
M1="Governance e gestione dei rischi TIC";M2="Sicurezza dei sistemi, dei dati e degli accessi";M3="Continuità operativa e ripristino";M4="Incidenti TIC: gestione, classificazione e segnalazione";M5="Test di resilienza operativa digitale e TLPT";M6="Rischi da fornitori terzi di servizi TIC e registro degli accordi";M7="Ambito di applicazione per tipo di entità"
def macro_di(t):
    for k,m in [("Imparare",M1),("TLPT",M5),("tester",M5),("Applicare DORA",M7),("sedi di negoziazione",M7),("Quadro semplificato: continuità",M3),("Quadro semplificato: governance",M1),("Quadro semplificato: identificazione",M1),
        ("registro",M6),("fornitori",M6),("Subappalto",M6),("uscita",M6),("Fornitori critici",M6),
        ("incident",M4),("segnalazion",M4),("Segnalare",M4),("clienti",M4),("minacce",M4),("costi e perdite",M4),("crisi",M4),
        ("TLPT",M5),("test di penetrazione",M5),("tester",M5),("red team",M5),("Programma di test",M5),
        ("continuità",M3),("Backup",M3),
        ("Governance",M1),("quadro dei rischi",M1),("quadro di gestione",M1),("Politiche di sicurezza TIC",M1),("Valutare e trattare",M1),("inventariare",M1),("Imparare",M1)]:
        if k in t: return m
    return M2

import re
def short(n):
    m=re.match(r'UE-3(\d{4})([RL])(\d+)$',n)
    if m: return ('Reg. (UE) ' if m.group(2)=='R' else 'Dir. (UE) ')+m.group(1)+'/'+str(int(m.group(3)))
    if n.startswith('IT-decreto'): return 'd.lgs. 23/2025'
    if n=='IVASS-7772be2880': return 'Lettera IVASS 14/02/2025 (segnalazioni incidenti)'
    if n=='IVASS-22f87cfee4': return 'Lettera IVASS 07/03/2025 (registro delle informazioni)'
    if n.startswith('EBA'): return 'Orientamenti congiunti ESA sulla stima dei costi e delle perdite'
    return n
def fontitxt(m):
    d={}
    for x in m:
        art=x['art']; lab=art if (art=='Premessa' or art.startswith('Allegato')) else 'art. '+art
        d.setdefault(x['norma'],{}).setdefault(lab,[])
        if x['comma'] and x['comma'] not in d[x['norma']][lab]: d[x['norma']][lab].append(x['comma'])
    out=[]
    for n,arts in d.items():
        out.append(short(n)+' ('+', '.join(a+(' c. '+', '.join(c) if c else '') for a,c in arts.items())+')')
    return '; '.join(out)
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
    comp=''
    out.append({"norma":p['norma'],"art":p['art'],"comma":p['comma'],"titolo":tit,
      "desc":desc+'\n\nObblighi compresi:\n'+'\n'.join('- '+x['titolo'].rstrip('.') for x in m)+'\n\nFonti normative: '+fontitxt(m)+'.',
      "dest":p['dest'],"termine":termine,
      "natura":'obbligatorio' if any(x['natura']=='obbligatorio' for x in m) else p['natura'],
      "sogg":'banca',"cit":p['cit'],"citOk":bool(p.get('citOk')),
      "f":f,"sanz_txt":sanz,"S":0,"C":0,"lv":"prescrizioni","pres":[],"stato":None,"val":False,
      "macro":macro_di(tit),"fonti":[{**{k:x[k] for k in('norma','art','comma','cit')},'pid':x['_id'],'titolo':x['titolo']} for x in m]})
for n,x in enumerate(out,1): x['_id']='a%03d'%n
json.dump(out,open('/home/claude/ra_build/data/adem_ramwf8f1hm.json','w'),ensure_ascii=False)
pun=[x for i,x in enumerate(a) if i not in EX]
for x in pun: x.pop('_escl',None)
json.dump(pun,open('/home/claude/ra_el/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(pun,open('/home/claude/ra_build/data/adem_ramweuq26q.json','w'),ensure_ascii=False)
MAP={}
for x in out:
    for f in x['fonti']: MAP[f['pid']]=x['macro']
for x in pun: x['macro']=MAP[x['_id']]; x['sogg']='banca'
json.dump(pun,open('/home/claude/ra_el/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(pun,open('/home/claude/ra_build/data/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(MAP,open('/home/claude/ra_build/data/macro.json','w'),ensure_ascii=False)
json.dump(out,open('/home/claude/ra_build/data/adem_ramwf8f1hm.json','w'),ensure_ascii=False)
from collections import Counter
print(Counter(x['macro'] for x in out))
print(len(EX),'esclusi;',len(pun),'puntuali;',len(out),'prescrizioni;',sum(len(x['fonti']) for x in out))
ids=['a%03d'%(i+1) for i in sorted(EX)]; json.dump(ids,open('esclusi_ids.json','w')); print(ids)

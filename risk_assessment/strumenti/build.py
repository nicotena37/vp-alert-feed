import json,sys
sys.path.insert(0,'.')
from gruppi import G
a=json.load(open('../adem_ramweuq26q.ORIG.json'))
# adempimenti NON riferiti alle banche (autorità, Stati membri, ESA, fornitori TIC, CSD/CCP)
EX={i for i,x in enumerate(a) if x['sogg']=='altro'}
EX|={196,202}|set(range(422,430))
# entità non bancarie: intermediari finanziari, Bancoposta, sedi di negoziazione, assicurazioni, fondi pensione, lettere IVASS
EX|={17,18,20,21,22,23,24}|set(range(27,42))
for i in sorted(EX): a[i]['_escl']=True
# perimetri: le entità non bancarie restano nei dati (campo per), non vengono più scartate
SPEC={17:['intermediari'],18:['intermediari'],20:['bancoposta'],21:['sedi'],22:['sedi'],23:['assicurazione'],24:['fondi_pensione'],335:['ccp_csd'],147:['ccp_csd']}
for i in range(27,42): SPEC[i]=['assicurazione']
import re
PERIM_LISTA=[('banca',0),('assicurazione',0),('sim',0),('sgr',0),('intermediari',0),('bancoposta',0),('sedi',0),('fondi_pensione',0),('ccp_csd',0)]
PROV=re.compile(r'fornitor|prestator|outsourc',re.I); KEEP={294,306,321}
for i in KEEP: a[i]['dest']='banca'
EX|={i for i,x in enumerate(a) if PROV.search(x['dest']) and not re.search(r'banca|enti creditizi|entit',x['dest']) and i not in KEEP}
MAI=EX-set(SPEC)   # autorità, Stati membri, ESA, fornitori TIC: mai negli adempimenti
import re
BANCA_RE=re.compile(r'ent[ie] creditizi|\bTUB\b|G-SII|O-SII',re.I)
DAVERIF=[]
def per_di(i,x):
    if x.get('per'): return x['per']
    if i in SPEC: return SPEC[i]
    if re.match(r'(UE-3|IT-decreto|EBA)',x['norma']):
        if BANCA_RE.search((x.get('cit') or '')+' '+x['titolo']+' '+x['dest']): DAVERIF.append('a%03d'%(i+1)); return ['banca']
        return ['tutti']
    return ['banca']  # norme non DORA: per default solo banche finché non indicato
# ambito soggettivo letto nel testo (indagine sul testo degli articoli):
#  - quadro semplificato (art. 16 DORA + RTS 2024/1774 art. 28-41, a371-a403): NON per le banche, solo imprese di investimento piccole e non interconnesse (SIM) e piccoli enti pensionistici
#  - TLPT (art. 26 DORA + RTS 2025/1190): enti creditizi G-SII/O-SII, istituti di pagamento/IMEL grandi, CSD, CCP, sedi di negoziazione maggiori, grandi assicurazioni; SIM e SGR non sono nell'elenco
#  - a159: solo enti creditizi significativi; a460: enti creditizi significativi, gestori di sedi di negoziazione e CCP; a478: G-SII/O-SII, CCP, CSD, sedi di negoziazione
PEROV={i:['sim','fondi_pensione'] for i in range(370,403)}
for i,x in enumerate(a):
    if x['norma']=='UE-32025R1190' or (x['norma']=='UE-32022R2554' and x['art']=='26'): PEROV[i]=['banca','assicurazione','sedi','ccp_csd']
PEROV[158]=['banca']; PEROV[459]=['banca','sedi','ccp_csd']; PEROV[477]=['banca','sedi','ccp_csd']
PER={i:(PEROV[i] if i in PEROV else per_di(i,x)) for i,x in enumerate(a)}
json.dump(sorted(MAI),open('esclusi.json','w'))
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
def vis(i,p): return 'tutti' in PER[i] or p in PER[i]
def adatta(t,p):
    if p=='banca': return t
    for x,y in [('La banca',"L'entità"),('la banca',"l'entità"),('della banca',"dell'entità"),('alla banca',"all'entità"),('dalla banca',"dall'entità"),('Le banche','Le entità'),('le banche','le entità')]: t=t.replace(x,y)
    return t
def componi(tit,desc,idx,p):
    m=[a[i] for i in idx]; q=m[0]
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
    spec=set(z for i in idx for z in PER[i])-{'tutti'}
    d=desc+'\n\nObblighi compresi:\n'+'\n'.join('- '+x['titolo'].rstrip('.') for x in m)+'\n\nFonti normative: '+fontitxt(m)+'.'
    return {"norma":q['norma'],"art":q['art'],"comma":q['comma'],"titolo":adatta(tit,p),"desc":adatta(d,p),
      "dest":q['dest'],"termine":termine,"natura":'obbligatorio' if any(x['natura']=='obbligatorio' for x in m) else q['natura'],
      "sogg":p,"cit":q['cit'],"citOk":bool(q.get('citOk')),"f":f,"sanz_txt":sanz,"S":0,"C":0,"lv":"prescrizioni","pres":[],"stato":None,"val":False,
      "per":sorted(spec) if spec else ['tutti'],"macro":macro_di(tit),
      "fonti":[{**{k:x[k] for k in('norma','art','comma','cit')},'pid':x['_id'],'titolo':x['titolo']} for x in m]}
def costruisci(p):
    out=[];usati=set()
    for tit,desc,idx in G:
        idx=[i for i in idx if i not in MAI and vis(i,p)]
        if not idx: continue
        if tit in RINOMINA: tit,desc=RINOMINA[tit]
        usati|=set(idx); out.append(componi(tit,desc,idx,p))
    # adempimenti rimasti del perimetro, non coperti dai gruppi a mano: un gruppo per norma (se almeno 2)
    resto=collections.defaultdict(list)
    for i in range(len(a)):
        if i not in MAI and i not in usati and vis(i,p): resto[a[i]['norma']].append(i)
    for nm,ix in resto.items():
        if len(ix)>=2 and len(ix)<=15:
            out.append(componi("Adempimenti specifici: "+short(nm),"Gli adempimenti previsti da "+short(nm)+" per questo perimetro.",ix,p))
    for n,x in enumerate(out,1): x['_id']='a%03d'%n
    return out
import collections
out=costruisci('banca')
GRP={'banca':out}
for p,_ in PERIM_LISTA:
    if p!='banca':
        g=costruisci(p)
        if g: GRP[p]=g
for p,g in GRP.items(): json.dump(g,open('/home/claude/ra_build/data/prescrizioni_%s.json'%p,'w'),ensure_ascii=False)
json.dump(out,open('/home/claude/ra_build/data/adem_ramwf8f1hm.json','w'),ensure_ascii=False)
pun=[x for i,x in enumerate(a) if i not in MAI]
for i,x in enumerate(a): x['per']=PER[i]
for x in pun: x.pop('_escl',None)
json.dump(pun,open('/home/claude/ra_el/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(pun,open('/home/claude/ra_build/data/adem_ramweuq26q.json','w'),ensure_ascii=False)
MAP={}
for x in out:
    for f in x['fonti']: MAP[f['pid']]=x['macro']
for x in pun: x['macro']=MAP.get(x['_id'],M7); x['sogg']='banca'
json.dump(pun,open('/home/claude/ra_el/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(pun,open('/home/claude/ra_build/data/adem_ramweuq26q.json','w'),ensure_ascii=False)
json.dump(MAP,open('/home/claude/ra_build/data/macro.json','w'),ensure_ascii=False)
json.dump(out,open('/home/claude/ra_build/data/adem_ramwf8f1hm.json','w'),ensure_ascii=False)
from collections import Counter
print(Counter(x['macro'] for x in out))
print(len(EX),'esclusi;',len(pun),'puntuali;',len(out),'prescrizioni;',sum(len(x['fonti']) for x in out))
json.dump({'a%03d'%(i+1):PER[i] for i in range(len(a)) if i not in MAI},open('/home/claude/ra_build/data/per.json','w'))
print('DA VERIFICARE (testo con termini bancari, messi su banca):',DAVERIF)
print(Counter(tuple(v) for i,v in PER.items() if i not in MAI))
ids=['a%03d'%(i+1) for i in sorted(MAI)]; json.dump(ids,open('esclusi_ids.json','w')); print(ids)

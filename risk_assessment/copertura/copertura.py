"""Copertura per perimetro: cosa c'e', cosa manca, quanto, adempimenti associati.
Uso: python3 copertura.py [--scrivi-per]   (con --scrivi-per aggiunge il campo per a biblioteca/ambiti_articoli.json, dopo backup)
Il perimetro delle norme e' una STIMA automatica (colonna 'stima'), da verificare man mano."""
import json,glob,re,collections,sys,shutil,os,datetime
B='/home/claude/vp-alert-feed/biblioteca/'; R='/home/claude/vp-alert-feed/risk_assessment/'
L=lambda f:json.load(open(f))
PERIM=[("banca","Banche"),("assicurazione","Imprese di assicurazione"),("sim","SIM"),("sgr","SGR"),("intermediari","Intermediari finanziari (art. 106 TUB)"),("bancoposta","Bancoposta"),("sedi","Sedi di negoziazione"),("fondi_pensione","Fondi pensione"),("ccp_csd","CCP e depositari centrali")]
PN=dict(PERIM)
at=L(B+'ambiti_atti.json'); aa=L(B+'ambiti_articoli.json')
T={};TXT={}
for f in glob.glob(B+'indice_*.json')+glob.glob(B+'corpus_*.json'):
    d=L(f)
    it=d.items() if isinstance(d,dict) else [(v.get('id'),v) for v in d]
    for k,v in it:
        if not (k and isinstance(v,dict)): continue
        if v.get('titolo'): T.setdefault(k,v['titolo'])
        if v.get('n_articoli'): TXT[k]=v['n_articoli']
FAL={}
for f in ['falliti_riprova.json','falliti_autorita.json','falliti_blocco3.json']:
    for k,v in L(B+f).items(): FAL[k]=str(v)
SENZA=set(L(B+'senza_adempimenti.json'))
# tematica -> perimetri (stima)
TB=["Vigilanza prudenziale (Basilea)","Vigilanza prudenziale","Segnalazioni di Vigilanza","Credito","Incassi e pagamenti","Trasparenza e tutela del consumatore","Gestione reclami","Usura","Banche e intermediari","Imprese e intermediari","Sviluppo commerciale","Sviluppo commerciale e Rete vendita"]
TM=["Mercati finanziari","Emittenti","Benchmark finanziari"]
def per_atto(k,v):
    p=set()
    pr=[a for a in v['ambiti'] if a['ruolo']=='principale'] or v['ambiti']
    for a in pr:
        t=a['tematica']
        if t in TB: p.add('banca')
        elif t=='Distribuzione assicurativa': p.add('assicurazione')
        elif t=='Gestione collettiva': p.add('sgr')
        elif t in TM: p|={'banca','sim','sgr'}
        else: p.add('tutti')
    ti=(T.get(k) or '').lower()
    if k.startswith(('IVASS','EIOPA')): p.discard('tutti'); p.add('assicurazione')
    if k.startswith('COVIP'): p={'fondi_pensione'}
    if re.search(r'assicura|riassicura|solvency|ivass',ti): p.discard('tutti'); p.add('assicurazione')
    if re.search(r'\boicr\b|\bsgr\b|gestori di fondi|\bfia\b|ucits|aifm|gestione collettiva',ti): p.discard('tutti'); p.add('sgr')
    if re.search(r'imprese di investimento|\bsim\b|mifid|servizi di investimento',ti): p.discard('tutti'); p|={'sim'}
    if not p: p={'tutti'}
    if 'tutti' in p and len(p)>1: p.discard('tutti')
    return sorted(p)
# override per atti DORA gia lavorati
OV={'UE-32022R2554':['tutti'],'UE-32024R1772':['tutti'],'UE-32024R1773':['tutti'],'UE-32024R1774':['tutti'],'UE-32025R1190':['tutti'],'UE-32025R0301':['tutti'],'UE-32025R0302':['tutti'],'UE-32025R0295':['tutti'],'UE-32025R0532':['tutti'],'UE-32024R2956':['tutti'],'UE-32022L2556':['tutti'],'IT-decreto.legislativo-2025-03-10-23':['tutti'],'EBA-8edbe0bc94':['tutti'],'IVASS-7772be2880':['assicurazione'],'IVASS-22f87cfee4':['assicurazione']}
PA={k:OV.get(k) or per_atto(k,v) for k,v in at.items()}
# adempimenti per norma e per perimetro
O=L('/home/claude/ra_el/adem_ramweuq26q.ORIG.json'); MAI=set(L('/home/claude/ra_el/presc/esclusi.json'))
PERA=L('/home/claude/ra_build/data/per.json')
adn=collections.Counter();adm=collections.Counter();adp=collections.defaultdict(collections.Counter)
for i,x in enumerate(O):
    if i in MAI: adm[x['norma']]+=1; continue
    adn[x['norma']]+=1
    for p in PERA['a%03d'%(i+1)]: adp[x['norma']][p]+=1
# ---- attribuzione perimetro a livello articolo (solo con --scrivi-per)
if '--scrivi-per' in sys.argv:
    bak=B+'ambiti_articoli.bak_prima_perimetro.json'
    if not os.path.exists(bak): shutil.copy(B+'ambiti_articoli.json',bak)
    for k,e in aa.items():
        pn=PA.get(k) or ['tutti']
        e['per']=pn; e['per_stato']='stima'
        for pt in e['parti']:
            pt['per']=[] if pt.get('na') else pn
    json.dump(aa,open(B+'ambiti_articoli.json','w'),ensure_ascii=False)
    print('per scritto su',len(aa),'norme')
# ---- tabella norme (solo atti non abrogati con almeno un ambito principale)
righe=[]
for k,v in at.items():
    if v.get('abrogato'): continue
    pr=[a for a in v['ambiti'] if a['ruolo']=='principale']
    if not pr: continue
    c=collections.Counter(); 
    st='in elenco'
    if k in FAL: st='testo non scaricabile'
    elif k in TXT: st='testo scaricato'
    else: st='senza testo'
    if k in aa: st='articoli attribuiti (pronta per RA)'
    ad=adn.get(k,0)
    righe.append(dict(id=k,titolo=T.get(k) or '',fonte=k.split('-')[0],stato=st,per=PA[k],tem=sorted({a['tematica'] for a in pr}),amb=sorted({a['tematica']+' > '+a['ambito'] for a in pr}),n_ad=ad,n_ad_mai=adm.get(k,0),senza=k in SENZA,fal=FAL.get(k,'')))
json.dump(righe,open('/tmp/righe_cop.json','w'),ensure_ascii=False)
print(len(righe),collections.Counter(r['stato'] for r in righe))
print(collections.Counter(p for r in righe for p in r['per']))

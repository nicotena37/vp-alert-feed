import json,collections,datetime,sys
sys.argv=['x']; exec(open('copertura.py').read().split('# ---- tabella norme')[0])
from openpyxl import Workbook
from openpyxl.styles import Font,PatternFill,Alignment,Border,Side
from openpyxl.utils import get_column_letter
righe=json.load(open('/tmp/righe_cop.json'))
DAY=datetime.date.today().isoformat()
wb=Workbook()
H=PatternFill('solid',fgColor='1F4E5F');HF=Font(bold=True,color='FFFFFF',name='Arial',size=10);BF=Font(name='Arial',size=10)
def sheet(name,head,rows,widths,first=False,filt=True,wrap=()):
    ws=wb.active if first else wb.create_sheet(); ws.title=name
    ws.append(head)
    for c in ws[1]: c.fill=H;c.font=HF;c.alignment=Alignment(wrap_text=True,vertical='center')
    for r in rows: ws.append(r)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font=BF
            if c.column in wrap: c.alignment=Alignment(wrap_text=True,vertical='top')
    for i,w in enumerate(widths,1): ws.column_dimensions[get_column_letter(i)].width=w
    ws.freeze_panes='A2'
    if filt and rows: ws.auto_filter.ref=ws.dimensions
    ws.row_dimensions[1].height=32
    return ws
# ---------- Leggimi
leg=[["Copertura normativa per perimetro — Compliance dyAInamic",""],["Aggiornato al",DAY],["",""],
["Che cos'è","Cruscotto fuori dal sito che mostra, per ogni perimetro (banche, assicurazioni, SIM, SGR…), quante norme ci sono, a che punto è il lavoro, cosa manca e quanti adempimenti sono già stati creati."],
["Avanzamento di una norma","1) In elenco (classificata per tematica/ambito)  →  2) Testo scaricato  →  3) Articoli attribuiti (ambiti, processi, perimetro: pronta per il risk assessment)  →  4) Adempimenti creati."],
["Cosa manca (3 tipi)","A) Testo non disponibile: norma classificata ma testo non scaricato o non scaricabile.  B) Da lavorare: testo presente ma articoli non ancora attribuiti, quindi nessun adempimento.  C) Buchi noti: censimenti non fatti (vedi foglio 'Buchi noti')."],
["Perimetro: è una stima","Per le 69 norme con articoli attribuiti il perimetro è stato scritto nel campo 'per' come STIMA (da verificare). Per le altre è dedotto da tematica, fonte e titolo. Le norme valide per tutte le entità finanziarie sono 'trasversali'."],
["Trasversali","Una norma trasversale vale per ogni perimetro: nei fogli compare come 'Trasversale' in ciascuno."],
["Conteggio norme","Sono contate le norme non abrogate con almeno un ambito principale. Una norma con più ambiti compare in ciascuno (nel foglio 'Per ambito'), ma una sola volta nei totali del foglio 'Riepilogo'."],
["Adempimenti","Per ora esistono solo per l'ambito DORA e solo per le banche (459 puntuali dopo l'esclusione di autorità e fornitori, che non sono mai adempimenti)."],
["Fogli","Riepilogo · Per ambito · Adempimenti per norma · Norme (elenco completo, filtrabile) · Da fare (testo mancante) · Buchi noti"]]
ws=sheet('Leggimi',['',''],leg,[28,120],first=True,filt=False,wrap=(2,)); ws.delete_rows(1); ws['A1'].font=Font(bold=True,size=14,name='Arial')
for r in ws.iter_rows(min_row=2):
    r[0].font=Font(bold=True,name='Arial',size=10)
# ---------- Riepilogo
def vis(r,p): return p in r['per'] or 'tutti' in r['per']
ris=[]
for k,n in PERIM:
    sp=[r for r in righe if k in r['per']]; tr=[r for r in righe if 'tutti' in r['per']]
    al=sp+tr
    c=lambda L,f:sum(1 for r in L if f(r))
    txt=lambda r:r['stato'] in('testo scaricato','articoli attribuiti (pronta per RA)')
    att=lambda r:r['stato'].startswith('articoli')
    adp_sp=sum(1 for v in PERA.values() if v==[k]); adp_tr=sum(1 for v in PERA.values() if 'tutti' in v)
    ris.append([n,len(sp),len(tr),len(al),c(al,txt),c(al,att),c(al,lambda r:r['stato']=='testo scaricato'),c(al,lambda r:not txt(r)),sum(1 for kk in adn if k in PA.get(kk,[]) or 'tutti' in PA.get(kk,[])),adp_sp,adp_tr,adp_sp+adp_tr])
ris=[[*r] for r in ris]
hd=['Perimetro','Norme riferite a questo perimetro (alcune condivise con altri)','Norme trasversali','Norme totali visibili','Con testo scaricato','Con articoli attribuiti (pronte per RA)','Da lavorare (testo ok, articoli da attribuire)','Testo mancante o non scaricabile','Norme con adempimenti creati','Adempimenti propri del perimetro','Adempimenti trasversali','Adempimenti totali nella RA']
ws=sheet('Riepilogo',hd,ris,[34,16,14,14,14,18,20,18,16,16,14,14],wrap=())
for c in ws[1]: c.alignment=Alignment(wrap_text=True,vertical='center')
ws.row_dimensions[1].height=62
n=ws.max_row+2
ws.cell(n,1,'Totale norme classificate (senza doppi conteggi)').font=Font(bold=True,name='Arial',size=10); ws.cell(n,2,len(righe)).font=BF
ws.cell(n+1,1,'di cui con testo scaricato').font=BF; ws.cell(n+1,2,sum(1 for r in righe if r['stato'] in('testo scaricato','articoli attribuiti (pronta per RA)'))).font=BF
ws.cell(n+2,1,'di cui con articoli attribuiti').font=BF; ws.cell(n+2,2,sum(1 for r in righe if r['stato'].startswith('articoli'))).font=BF
ws.cell(n+3,1,'Adempimenti esclusi per sempre (autorità, Stati membri, ESA, fornitori TIC)').font=BF; ws.cell(n+3,2,len(MAI)).font=BF
ws.cell(n+4,1,'Nota: per SIM e SGR non ci sono ancora adempimenti propri, solo i trasversali').font=Font(italic=True,name='Arial',size=10)
# ---------- Per ambito
rows=[]
agg=collections.defaultdict(lambda:collections.Counter())
for r in righe:
    for t in r['tem']:
        for p in r['per']:
            tipo='Trasversale' if p=='tutti' else 'Specifico'
            for pp in ([k for k,_ in PERIM] if p=='tutti' else [p]):
                a=agg[(pp,tipo,t)]; a['n']+=1
                a['txt']+= r['stato'] in('testo scaricato','articoli attribuiti (pronta per RA)')
                a['att']+= r['stato'].startswith('articoli'); a['mis']+= r['stato'] in('senza testo','testo non scaricabile')
                a['ad']+=r['n_ad']
order={k:i for i,(k,_) in enumerate(PERIM)}
for (pp,tipo,t),a in sorted(agg.items(),key=lambda x:(order[x[0][0]],x[0][1]!='Specifico',-x[1]['n'])):
    rows.append([PN[pp],tipo,t,a['n'],a['txt'],a['att'],a['n']-a['att']-a['mis'],a['mis'],a['ad']])
sheet('Per ambito',['Perimetro','Tipo','Tematica (ambito principale)','Norme','Con testo','Articoli attribuiti','Da lavorare','Testo mancante','Adempimenti creati'],rows,[34,14,40,10,10,14,12,14,14])
# ---------- Adempimenti per norma
rows=[]
for k in sorted(adn.keys()|adm.keys(),key=lambda x:-adn.get(x,0)):
    pr=PA.get(k,['?'])
    rows.append([k,(T.get(k) or '')[:140],', '.join(PN.get(p,'Trasversale') for p in pr),adn.get(k,0),adm.get(k,0),sum(adp[k].get(p,0) for p in ['assicurazione','intermediari','bancoposta','sedi','fondi_pensione','ccp_csd'])])
sheet('Adempimenti per norma',['Norma','Titolo','Perimetro (stima)','Adempimenti nella RA','Esclusi (autorità/fornitori)','Di cui solo altri perimetri'],rows,[36,70,30,14,16,16],wrap=(2,))
# ---------- Norme
rows=[[r['id'],r['titolo'][:160],r['fonte'],', '.join(PN.get(p,'Trasversale') for p in r['per']),r['stato'],'; '.join(r['tem']),r['n_ad'],'sì' if r['senza'] else ''] for r in righe]
sheet('Norme',['ID','Titolo','Fonte','Perimetro (stima)','Stato','Tematiche principali','Adempimenti','Senza adempimenti per banche'],rows,[28,70,10,28,30,40,12,16])
# ---------- Da fare
rows=[[r['id'],r['titolo'][:160],', '.join(PN.get(p,'Trasversale') for p in r['per']),r['stato'],r['fal'][:60],'; '.join(r['tem'])] for r in righe if r['stato'] in('senza testo','testo non scaricabile')]
sheet('Da fare (testo mancante)',['ID','Titolo','Perimetro (stima)','Stato','Motivo','Tematiche'],rows,[28,70,28,22,30,40])
# ---------- Buchi noti
rows=[["Atti italiani da censire","circa 600","Censimento non fatto","Tutti"],
["Atti senza testo consolidato","8","Serve il testo vigente","Banche e altri"],
["Testi EIOPA da recuperare","17","Scaricamento bloccato (429)","Assicurazioni"],
["Sanzioni IVASS per le imprese di assicurazione","—","Non estratte","Assicurazioni"],
["Norme specifiche SIM/SGR (TUF, regolamenti Consob/Banca d'Italia)","—","Nessun adempimento estratto: servono nuove estrazioni","SIM, SGR"],
["Testi Banca d'Italia","—","Leggibili solo dal browser del PC (robots.txt)","Banche"],
["Elenco norme attese per ambito","—","Da costruire, partendo da DORA","Tutti"],
["Adempimenti oltre DORA","—","Finora creati solo per DORA","Tutti"]]
sheet('Buchi noti',['Buco','Quanti','Cosa manca','Perimetro'],rows,[62,12,60,22])
wb.save('copertura_perimetri.xlsx'); print('ok')

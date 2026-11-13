import re
FOOT=re.compile(r'^\s*(\d{1,2})\s+(?![\.\)\-–])\S')
PAGE=re.compile(r'(\bPag\.?\s*\d|^\s*\d+\s+Pag\.?\s*$|^\s*\d+\s*/\s*\d+\s*$|^\s*Pag\.?\s*$|^\s*\d{3,}/\d{2}\s*$|^\s*Page\s+\d)',re.I)
def pulisci(t):
    """Toglie note a piè di pagina e 'Note all'art.'; ritorna (testo, [parti_rimosse])"""
    rem=[]
    m=re.search(r"\n\s*Note (all'art\.|alle premesse|al titolo|all'allegato)",t)
    if m: rem.append(t[m.start():]); t=t[:m.start()]
    righe=t.split('\n'); out=[]; i=0; last=0; nums=set()
    while i<len(righe):
        r=righe[i]; m=FOOT.match(r)
        if m and int(m.group(1)) in (last+1,1) and i>0:
            j=i; blocco=[]
            while j<len(righe):
                if blocco and PAGE.search(righe[j]): break
                if len(blocco)>=60: break
                blocco.append(righe[j]); j+=1
            nums.add(int(m.group(1)))
            # più note consecutive nel blocco
            for b in blocco:
                mm=FOOT.match(b)
                if mm: last=int(mm.group(1)); nums.add(last)
            rem.append('\n'.join(blocco)); i=j; continue
        out.append(r); i+=1
    out=[r for r in out if not PAGE.search(r)]
    s='\n'.join(out)
    for n in sorted(nums,reverse=True):
        s=re.sub(r'(?<=[A-Za-zàèéìòùÀ-ÿ\.;:,\)”»])%d(?=[\s\.;:,\)]|$)'%n,'',s)
        s=re.sub(r'\b((?:19|20)\d\d)%d\b'%n,r'\1',s)
    return s,rem

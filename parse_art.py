import re
def pulisci(t): return re.sub(r"\s+"," ",re.sub(r"\(\(|\)\)","",t)).strip()
def commi(testo):
    righe=testo.split("\n")[2:] if testo.startswith("Art") else testo.split("\n")
    out={}; cur=None
    for l in righe:
        l2=re.sub(r"^\(\(","",l.strip())
        m=re.match(r"^(\d+(?:-(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|decies))?)\.\s",l2)
        if m: cur=m.group(1); out[cur]=[l2]; continue
        if cur: out[cur].append(l2)
        else: out.setdefault("0",[]).append(l2)
    return {k:"\n".join(v) for k,v in out.items()}
def lettere(ctesto):
    out={}; cur=None
    for l in ctesto.split("\n"):
        l2=re.sub(r"^\(\(","",l.strip())
        m=re.match(r"^([a-z](?:-(?:bis|ter|quater))?)\)\s",l2)
        if m: cur=m.group(1); out[cur]=[l2]; continue
        if cur: out[cur].append(l2)
    return {k:"\n".join(v) for k,v in out.items()}
def estratto(A, art, c=None, l=None):
    t=A.get(art)
    if not t: return ""
    if c is None: return pulisci(" ".join(t.split("\n")[2:]))
    cc=commi(t).get(c,"")
    if l is None: return pulisci(cc)
    return pulisci(lettere(cc).get(l,""))

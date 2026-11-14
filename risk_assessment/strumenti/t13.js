const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1200,height:1000}});const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.route(/fonts\.|cdnjs/,r=>r.abort());await p.goto('http://localhost:8765/index.html');await p.waitForTimeout(1200);
await p.evaluate(()=>localStorage.setItem('kv:ra/rg',JSON.stringify({id:'rg',titolo:'t',per:'banca',prob:'voti',metodo:'m3',stato:'in_corso',amb:['IT e Digital||Resilienza operativa digitale (DORA)'],norme:{},livello:'prescrizioni',richiesta:{stato:'pronta',file:'data/adem_ramwf8f1hm.json',importato:false,per:'banca'},extra:{},step:6,nAdem:0,nVal:0,nNr:0})));
await p.reload();await p.waitForTimeout(1000);await p.evaluate(()=>apriRA('rg'));await p.waitForTimeout(5000);
const T=await p.evaluate(()=>{
 const oggi=new Date().toISOString().slice(0,10),fa=m=>{const d=new Date();d.setMonth(d.getMonth()-m);return d.toISOString().slice(0,10)};
 const o={};
 o.mai=fattoreTest({tests:[]});
 o.indip_ok=fattoreTest({tests:[{data:oggi,tipo:2,cop:0,esito:0}]});          // 1
 o.auto_ok=fattoreTest({tests:[{data:oggi,tipo:0,cop:0,esito:0}]});          // 0.8
 o.vecchio=fattoreTest({tests:[{data:fa(30),tipo:2,cop:0,esito:0}]});        // 0.6+.4*.4=.76
 o.critico_aperto=fattoreTest({tests:[{data:oggi,tipo:2,cop:0,esito:3,aperti:true}]}); // .2
 o.signif_aperto=fattoreTest({tests:[{data:oggi,tipo:2,cop:0,esito:0},{data:oggi,tipo:1,cop:0,esito:2,aperti:true}]}); // cap .5
 const ad={_id:'x',fonti:[{pid:'1'},{pid:'2'},{pid:'3'},{pid:'4'}],voti:{1:4,2:4,3:4,4:1}};
 o.pv=Pvoti(ad).calc;  // (4+1.75)/2=2.875
 o.pv_over=Pvoti({...ad,vtot:3}).eff; // 2
 o.pv_none=Pvoti({_id:'y'});
 R.prob='voti';o.P_voti=IP(ad).P;R.prob='fattori';o.P_fatt=IP(ad).P;R.prob='voti';
 return o});
console.log(JSON.stringify(T));
// UI: popup di un adempimento raggruppato
await p.evaluate(()=>{vai(6)});await p.waitForTimeout(300);
const id=await p.evaluate(()=>{const a=A.find(x=>x.fonti&&x.fonti.length>=3);W=null;apriAd(a._id);return a._id});await p.waitForTimeout(400);
console.log('voti select',await p.evaluate(()=>document.querySelectorAll('#bAd [data-vo]').length),'vt',await p.evaluate(()=>document.querySelectorAll('#bAd [data-vt]').length));
await p.selectOption('#bAd [data-vo]:nth-of-type(1)','4').catch(()=>{});
await p.evaluate(()=>{const s=document.querySelectorAll('#bAd [data-vo]');s[0].value='4';s[0].dispatchEvent(new Event('change',{bubbles:true}));s[1].value='1';s[1].dispatchEvent(new Event('change',{bubbles:true}))});
console.log('P dopo voti',await p.evaluate(()=>IP(W).P.toFixed(3)),await p.evaluate(()=>document.querySelector('#bAd .box small:last-of-type, #bAd .box .small:last-child')?.textContent.slice(0,90)));
// presidio + test
await p.evaluate(()=>{W.pres.push({nome:'Procedura operativa scritta',nat:'Procedura',peso:.75,tipo:'Preventivo',adeg:0,tests:[]});corpoAd()});
await p.evaluate(()=>{document.querySelector('#bAd [data-tadd]').click()});await p.waitForTimeout(200);
console.log('test righe',await p.evaluate(()=>document.querySelectorAll('#bAd [data-tdel]').length),'E',await p.evaluate(()=>eff(W).toFixed(3)));
await p.screenshot({path:'t13.png'});
// metodologie
await p.evaluate(()=>{$('#dAd').close&&$('#dAd').close();vai(5)});await p.waitForTimeout(300);
console.log('radio met',await p.evaluate(()=>[...document.querySelectorAll('#metodi input[name=mt]')].length),'select',await p.evaluate(()=>[...document.querySelectorAll('#metodi select')].map(s=>s.name)));
await p.selectOption('select[name=mq]','m1');console.log('metodo m1?',await p.evaluate(()=>R.metodo));
await p.check('input[name=mt][value=e]');console.log('metodo euro?',await p.evaluate(()=>R.metodo),await p.evaluate(()=>[...document.querySelectorAll('#metodi select')].map(s=>s.name)));
await p.check('input[name=mt][value=q]');console.log('metodo q ripristina?',await p.evaluate(()=>R.metodo));
await p.screenshot({path:'t13b.png'});
console.log('errori',errs);await b.close()})()

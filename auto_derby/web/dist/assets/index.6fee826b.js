import{d as C,t as b,u as l,o as d,c as h,a,w as z,v as ue,r as P,b as x,e as ne,f as K,g as M,m as re,F as B,h as I,i as T,j as le,k as ce,R as ie,l as w,n as D,p as de,q as A,s as pe,x as fe,y as N,z as ae,A as X,B as J,C as Q,D as me,T as oe,E as G,G as he,H as ge,I as ve}from"./vendor.b0bc8c03.js";const _e=function(){const t=document.createElement("link").relList;if(t&&t.supports&&t.supports("modulepreload"))return;for(const n of document.querySelectorAll('link[rel="modulepreload"]'))r(n);new MutationObserver(n=>{for(const o of n)if(o.type==="childList")for(const m of o.addedNodes)m.tagName==="LINK"&&m.rel==="modulepreload"&&r(m)}).observe(document,{childList:!0,subtree:!0});function s(n){const o={};return n.integrity&&(o.integrity=n.integrity),n.referrerpolicy&&(o.referrerPolicy=n.referrerpolicy),n.crossorigin==="use-credentials"?o.credentials="include":n.crossorigin==="anonymous"?o.credentials="omit":o.credentials="same-origin",o}function r(n){if(n.ep)return;n.ep=!0;const o=s(n);fetch(n.href,o)}};_e();const ye=["\u30B9\u30D4\u30FC\u30C9","\u30B9\u30BF\u30DF\u30CA","\u30D1\u30EF\u30FC","\u6839\u6027","\u8CE2\u3055","\u30E1\u30E2\u5E33","\u6226\u8853\u66F8","\u79D8\u4F1D\u66F8","\u30C8\u30EC\u30FC\u30CB\u30F3\u30B0","\u30E1\u30AC\u30DB\u30F3","\u30BF\u30FC\u30F3","\u30A6\u30A7\u30A4\u30C8","\u8E44\u9244","\u30D0\u30A4\u30BF\u30EB","\u30C9\u30EA\u30F3\u30AF","\u30B1\u30FC\u30AD","\u7D46\u30B2\u30FC\u30B8","\u3084\u308B\u6C17","\u4F53\u529B","\u306B\u306A\u308B","\u89E3\u6D88","\u30EC\u30FC\u30B9","\u30FB","\u306E","\u30FC","\u30E5","\u30C3"];function xe(...e){}var j=(e=>(e.SINGLE_MODE_ITEM_SELECT="SINGLE_MODE_ITEM_SELECT",e.LOG="LOG",e))(j||{});function be(){const e=document.getElementById("data");if(!e)throw new Error("'#data' element not found");return JSON.parse(e.innerHTML)}const L=be(),we=C({props:{pageData:{type:Object,required:!0}},setup(e){return(t,s)=>b(l(L))}}),Ce={class:"text-left"},Ee={class:"border-b border-gray-200"},$e={class:"font-bold"},ke={class:"text-sm"},De=a("span",{class:"bg-gray-200 rounded-lg px-1 mr-2"},"\u52B9\u679C",-1),Oe={class:"font-bold"},Y=C({props:{value:{type:Object,required:!0},idHidden:{type:Boolean}},setup(e){return(t,s)=>(d(),h("div",Ce,[a("p",Ee,[a("span",$e,b(e.value.name),1),z(a("span",{class:"text-sm float-right"},b(e.value.id),513),[[ue,!e.idHidden]])]),a("p",ke,[De,a("span",Oe,b(e.value.description),1)])]))}}),Fe={class:"max-w-lg m-auto space-y-2"},Ae={class:"bg-gray-200 sticky top-0 space-y-2"},Be={class:"text-center bg-white p-1 rounded"},Ie=a("p",null,"select matching item for this image:",-1),Le=["src"],Re=["action"],Me=a("span",{class:"bg-gray-200 mx-2 rounded-full px-4"},"id",-1),Te=a("button",{type:"submit",class:"bg-theme-green text-white rounded p-2 font-bold"}," \u78BA\u8A8D ",-1),Ne={class:"space-y-1"},qe={class:"w-full flex items-center"},Se={class:"inline align-top fill-current h-8",viewBox:"0 0 24 24"},ze=["d"],Ge={class:"flex gap-1 flex-wrap"},je={class:"space-y-2"},Pe=C({props:{pageData:{type:Object,required:!0}},setup(e){var p;const t=e,s=P({id:(p=t.pageData.defaultValue)!=null?p:0,q:""});function r(u){return[u.name,u.description]}function n(u,c){const f=r(u);return c.split(" ").every(v=>f.some(_=>_.includes(v)))}const o=x(()=>t.pageData.options.filter(u=>n(u,s.q)).map(u=>{const c=u.id===s.id;return{key:u.id,value:u,attrs:{class:["border border-2 cursor-pointer",c?"border-theme-green":"border-gray-200"],onClick:()=>{s.id=u.id}}}})),m=x(()=>ye.map(u=>{const c=o.value.filter(f=>n(f.value,u)).length;return{key:u,value:u,matchCount:c,attrs:{class:[(()=>c===0?"bg-gray-400 text-white":c===1?"bg-theme-green text-white":"bg-white text-theme-text")()],onClick:()=>{o.value.length!==c&&(s.q=c?`${s.q} ${u}`.trim():u)}}}})),i=x(()=>{var u;return(u=t.pageData.options.find(c=>c.id===s.id))!=null?u:{id:s.id,name:"unknown",description:"unknown"}});return ne(()=>{o.value.length===1&&(s.id=o.value[0].value.id)}),(u,c)=>(d(),h("div",Fe,[a("div",Ae,[a("div",Be,[Ie,a("img",{src:l(L).imageURL,class:"sticky m-auto"},null,8,Le),a("form",{action:l(L).submitURL,method:"POST",class:"flex items-center justify-center gap-2 mx-2"},[a("label",null,[Me,z(a("input",{"onUpdate:modelValue":c[0]||(c[0]=f=>l(s).id=f),type:"number",name:"id",class:"spin-button-none w-16 text-center"},null,512),[[K,l(s).id,void 0,{number:!0}]])]),M(Y,{value:l(i),class:"inline-block border border-gray-200 flex-auto rounded px-2","id-hidden":""},null,8,["value"]),Te],8,Re)]),a("div",Ne,[a("label",qe,[(d(),h("svg",Se,[a("path",{d:l(re)},null,8,ze)])),z(a("input",{"onUpdate:modelValue":c[1]||(c[1]=f=>l(s).q=f),class:"flex-auto",type:"search",placeholder:"search"},null,512),[[K,l(s).q]])]),a("ol",Ge,[(d(!0),h(B,null,I(l(m),({key:f,value:v,attrs:_})=>(d(),h("li",T({key:f,class:"cursor-pointer inline-block rounded px-1"},_),b(v),17))),128))])])]),a("ul",je,[(d(!0),h(B,null,I(l(o),({key:f,attrs:v,value:_})=>(d(),h("li",T({key:f,class:"bg-white rounded p-2"},v),[M(Y,{value:_},null,8,["value"])],16))),128))])]))}});function H(){const e=[],t=r=>{e.push(r)},s=()=>{var r;for(;e.length>0;)(r=e.pop())==null||r()};return le()&&ce(s),{addCleanup:t,cleanup:s}}var q=(e=>(e.TEXT="TEXT",e.IMAGE="IMAGE",e))(q||{}),F=(e=>(e.DEBUG="DEBUG",e.INFO="INFO",e.WARN="WARN",e.ERROR="ERROR",e))(F||{});async function He({stream:e,encoding:t="utf-8",onLine:s}){const r=e.getReader();let n="";const o=new TextDecoder(t);async function m(){const{value:i,done:p}=await r.read();if(p){n&&await s(n);return}const u=o.decode(i);let c=0;for(let f=0;f<u.length;f+=1)u[f]===`
`&&(await s(n+u.slice(c,f)),c=f+1,n="");n+=u.slice(c),await m()}await m()}function Ue(e,t){return(...s)=>{e.value+=1;let r=!1;try{const n=t(...s);return n instanceof Promise&&(r=!0,n.finally(()=>{e.value-=1})),n}finally{r||(e.value-=1)}}}function Ve(){return typeof ResizeObserver=="undefined"?ie:ResizeObserver}function We(e,t){const s=Ve(),r=new s(n=>{n.forEach(o=>{t(o)})});return r.observe(e),()=>r.disconnect()}function Z(e){const{addCleanup:t,cleanup:s}=H(),r=w(0),n=w(0);return D(e,o=>{if(s(),!o)return;n.value=o.clientWidth,r.value=o.clientHeight;const m=We(o,de(i=>{n.value=i.contentRect.width,r.value=i.contentRect.height},100));t(m)},{immediate:!0}),{width:n,height:r}}const Ke={class:"flex flex-wrap items-start bg-checkerboard p-px relative gap-2"},Xe=["src"],Je=["src"],Qe={class:"text-white bg-black bg-opacity-50 px-1"},Ye={key:0,class:"space-x-1"},Ze=C({props:{value:{type:Object,required:!0}},setup(e){const t=e,s=x(()=>{var v;return(v=t.value.layers)!=null?v:[]}),r=w(),n=w(),o=w(0),m=x(()=>({name:"main",url:t.value.url})),i=x(()=>{const v=o.value-1,_=s.value;return v in _?_[v]:m.value}),p=x(()=>[m.value,...s.value].map(({name:v},_)=>({key:_,label:v,inputAttrs:{type:"radio",checked:o.value===_,onChange:E=>{E.target.checked&&(o.value=_)}}}))),{width:u}=Z(r),{width:c}=Z(n),f=x(()=>u.value*3<c.value-20);return(v,_)=>(d(),h("div",{ref_key:"el",ref:n},[a("figure",Ke,[a("img",{ref_key:"img",ref:r,src:l(i).url},null,8,Xe),l(f)?(d(!0),h(B,{key:0},I(l(s),({name:E,url:$},g)=>(d(),h("figure",{key:g},[a("img",{src:$},null,8,Je),a("figcaption",Qe,b(E),1)]))),128)):A("",!0)]),l(f)?A("",!0):(d(),h("div",Ye,[(d(!0),h(B,null,I(l(p),({label:E,inputAttrs:$,key:g})=>(d(),h("label",{key:g},[a("input",pe(fe($)),null,16),a("span",null,b(E),1)]))),128))])),a("figcaption",null,b(e.value.caption),1)],512))}}),et=C({props:{value:{type:Object,required:!0}},setup(e){return(t,s)=>(d(),h("div",null,b(e.value.msg),1))}}),tt=C({props:{value:{type:Object,required:!0}},setup(e){return(t,s)=>(d(),h("div",null,"unsupported item: "+b(e.value),1))}}),st={class:"p-1 bg-white rounded border border-gray-300"},nt={class:"space-x-1"},rt={class:"text-sm float-right text-gray-400"},at=a("span",{class:"dot mx-1"},null,-1),ot=a("hr",{class:"border-gray-300 my-1"},null,-1),ut=new Map([[q.IMAGE,{component:Ze}],[q.TEXT,{component:et}]]),lt={component:tt},ct=C({props:{value:{type:Object,required:!0},lineno:{type:Number,required:!0}},setup(e){const t=e,s=new Intl.DateTimeFormat(void 0,{dateStyle:"short",timeStyle:"medium",hour12:!1}),r=new Intl.DateTimeFormat(void 0,{fractionalSecondDigits:3}),n=x(()=>{const i=new Date(t.value.ts);return`${s.format(i)}.${r.format(i)}`}),o=x(()=>{var i;return(i=ut.get(t.value.t))!=null?i:lt}),m=x(()=>{switch(t.value.lv){case F.DEBUG:return{class:"text-gray-400 bg-gray-800"};case F.INFO:return{class:"bg-gray-300"};case F.WARN:return{class:"bg-orange-500 text-orange-800"};case F.ERROR:return{class:"bg-red-500 text-red-800"};default:return xe(t.value.lv),{}}});return(i,p)=>(d(),h("li",st,[a("div",nt,[a("span",T({class:"w-24 inline-block text-center"},l(m)),b(e.value.lv),17),a("span",null,b(e.value.source),1),a("span",rt,[a("span",null,b(l(n)),1),at,a("span",null,b(e.lineno),1)])]),ot,(d(),N(ae(l(o).component),{value:e.value},null,8,["value"]))]))}});function ee(e,t,{deep:s}={}){const r=w(t(e));return D(e,n=>{r.value=w(t(n)).value},{deep:s}),r}function it(e,...t){const{addCleanup:s,cleanup:r}=H();D(e,n=>{r(),n&&(n.addEventListener(...t),s(()=>{n.removeEventListener(...t)}))},{immediate:!0})}function dt(e,{onScrollToBottom:t,onScrollToTop:s,margin:r=()=>0,marginBottom:n=r,marginTop:o=r}){it(e,"scroll",m=>{const i=m.target;i.scrollTop+i.clientHeight>=i.scrollHeight-n(i)?t==null||t(i):i.scrollTop<o(i)&&(s==null||s(i))})}function pt(e,t){const s=w(e.value);return D([e,t],([r,n])=>{n||(s.value=w(r).value)}),s}function ft(e,t,s=r=>r){return x({get(){return t(e.value)},set(r){e.value=s(r)}})}function mt(e,t,s){return s<=t?t:Math.min(Math.max(e,t),s)}const ht={key:1},gt={key:2,class:"flex flex-center h-full"},vt=a("div",{class:"text-center"},[a("h1",{class:"text-2xl"},"Log Viewer"),a("p",null,"waiting for record")],-1),_t=[vt],yt=C({props:{records:{type:Array,required:!0},size:{type:Number,default:100},paused:{type:Boolean}},setup(e){const t=e,s=X(t,"paused"),r=X(t,"records"),n=x(()=>{if(!t.paused)return{enterFromClass:"opacity-0 transform translate-x-8",enterActiveClass:"transition-all ease-in-out duration-500 relative",enterToClass:"opacity-100",leaveFromClass:"h-full max-h-fit",leaveToClass:"h-0",leaveActiveClass:"transition-all ease-in-out duration-500 overflow-hidden"}}),o=w(),m=x(()=>{var g;return(g=o.value)==null?void 0:g.$el}),i=pt(ee(()=>t.records,()=>t.records.length,{deep:!0}),s),p=ft(w(0),g=>g,g=>mt(g,0,i.value-1)),u=x(()=>p.value>0),c=x(()=>p.value<i.value-t.size),f=g=>{var y;return(y=m.value)==null?void 0:y.querySelector(`li[data-index="${g}"]`)},v=g=>{if(g===0)return;const y=p.value;p.value+=g;const k=p.value;k-y<0&&Q(()=>{const O=f(y),V=f(k),W=m.value;V&&O&&W&&(W.scrollTop-=V.offsetTop-O.offsetTop)})},_=J(()=>{!u.value||v(-Math.round(t.size/2))},100),E=J(()=>{!c.value||v(Math.round(t.size/2))},100);dt(m,{onScrollToTop:_,onScrollToBottom:E,margin:g=>Math.min(200,g.offsetHeight*.3)});const $=ee([i,p],()=>t.records.slice(p.value,p.value+t.size).map((g,y)=>({value:g,key:p.value+y,index:p.value+y})));return ne(()=>{t.paused||(p.value=Math.max(0,t.records.length-t.size))}),D([()=>t.paused,m,$],([g,y])=>{g||!y||Q(()=>{y.scroll({top:y.scrollHeight,behavior:"smooth"})})},{deep:!0}),(g,y)=>(d(),N(oe,T({ref_key:"el",ref:o,class:"max-h-screen overflow-y-auto overflow-x-hidden space-y-1",tag:"ol"},l(n)),{default:me(()=>[l(u)?(d(),h("button",{key:0,type:"button",class:"w-full text-blue-500 underline",onClick:y[0]||(y[0]=k=>l(_)())}," load previous records ")):A("",!0),(d(!0),h(B,null,I(l($),({value:k,key:U,index:O})=>(d(),N(ct,{key:U,value:k,lineno:O+1,"data-index":O},null,8,["value","lineno","data-index"]))),128)),l(c)?(d(),h("span",ht,[a("button",{type:"button",class:"w-full text-blue-500 underline",onClick:y[1]||(y[1]=k=>l(E)())}," load next records ")])):A("",!0),l(r).length===0?(d(),h("div",gt,_t)):A("",!0)]),_:1},16))}}),R=P({messages:[]}),xt=C({name:"MessageList",data(){return R},render(){return G(oe,{class:"fixed top-0 right-4 flex flex-col-reverse items-end",appear:!0,tag:"ol",moveClass:"transition ease-in-out duration-200",enterActiveClass:"transition ease-in-out duration-300",enterFromClass:"opacity-0 transform translate-x-full",leaveActiveClass:"transition ease-in-out duration-1000",leaveToClass:"opacity-0"},()=>this.messages.map(e=>{const t=e.render();return t.key=e.key,t}))}});let te=0;function se(e){const t=te;return te+=1,R.messages.splice(0,0,{key:t,render:e}),()=>{const s=R.messages.findIndex(r=>r.key===t);s<0||R.messages.splice(s,1)}}class bt{info(t,s=3e3+200*t.length){const r=se(()=>G("li",{class:"p-3 rounded-sm w-64 mx-2 my-1 bg-gray-900 text-white break-all"},t));setTimeout(r,s)}error(t,s=3e3+200*t.length){const r=se(()=>G("li",{class:"p-3 rounded-sm w-64 mx-2 my-1 bg-red-700 text-white break-all"},t));setTimeout(r,s)}}const S={message:new bt};async function wt(e){const t=new Image;return t.src=e,t.alt=e,await t.decode(),t}const Ct={class:"container max-w-2xl m-auto h-screen overflow-hidden flex flex-col gap-1"},Et={class:"flex-none flex gap-1"},$t={class:"flex flex-auto items-center"},kt={class:"inline align-top fill-current h-8",viewBox:"0 0 24 24"},Dt=["d"],Ot=a("input",{class:"flex-auto rounded border-gray-300",type:"search",placeholder:"TODO: search"},null,-1),Ft=["disabled"],At={class:"inline align-top fill-current h-8",viewBox:"0 0 24 24"},Bt=["d"],It=C({props:{pageData:{type:Object,required:!0}},setup(e){const t=e,s=P([]),r=async p=>{p.t===q.IMAGE&&await wt(p.url),s.push(p)},n=w(!1),o=w(0),{addCleanup:m,cleanup:i}=H();return D(()=>t.pageData.streamURL,Ue(o,async p=>{i();const u=new AbortController;m(()=>u.abort());try{const{body:c}=await fetch(p,{signal:u.signal});if(!c)return;await He({stream:c,onLine:async f=>{try{await r(Object.freeze(JSON.parse(f)))}catch(v){const _=s.length+1;S.message.error(`line parsing failed: ${_}: ${v}`)}}})}catch(c){S.message.error(`stream read failed: ${c}`)}S.message.info("stream closed")}),{immediate:!0}),(p,u)=>(d(),h("div",Ct,[a("div",Et,[a("label",$t,[(d(),h("svg",kt,[a("path",{d:l(re)},null,8,Dt)])),Ot]),a("button",{type:"button",class:"bg-white rounded border-gray-300 h-10 px-4 disabled:text-gray-200 disabled:cursor-not-allowed",disabled:o.value===0,onClick:u[0]||(u[0]=c=>n.value=!n.value)},[(d(),h("svg",At,[a("path",{d:n.value?l(he):l(ge)},null,8,Bt)]))],8,Ft)]),M(yt,{class:"flex-auto",records:l(s),paused:n.value},null,8,["records","paused"])]))}}),Lt={class:"bg-gray-200 text-theme-text min-h-screen"},Rt=C({setup(e){var r;const s=(r=new Map([[j.SINGLE_MODE_ITEM_SELECT,{component:Pe}],[j.LOG,{component:It}]]).get(L.type))!=null?r:{component:we};return(n,o)=>(d(),h("div",Lt,[(d(),N(ae(l(s).component),{"page-data":l(L)},null,8,["page-data"])),M(l(xt),{class:"messages z-20"})]))}});ve(Rt).mount("#app");

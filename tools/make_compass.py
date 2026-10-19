# -*- coding: utf-8 -*-
"""make_compass.py · 生成语义罗盘 compass.html（应用 A 首件交付）

从 r32_charge_table.json (字典 v2.0, 3498 字) 生成自包含单文件 HTML:
  - 内嵌紧凑字典 (字 x 10 维 + pos/norm/freq/frame_consistency)
  - 低置信角标: 跨框架一致性 < 0.25 的字在归因表标 ⚠ (R32 P2 判例)
  - 内嵌 golden 自检用例 (与 jevcore lexicon.solve 同口径, 加载时自检)
  - 双文本对比模式 / 10 维双向条形图 / 分域置信标注 / 逐字归因
零 API / 零后端 / 零外部依赖。字典更新后重新运行本脚本即可再生成。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # 项目根

from jevcore.jevcore.lexicon import Lexicon, PHYS7  # noqa: E402

DIMS_ZH = {
    "p_valence": "效价 好坏",
    "p_scale": "尺度 大小",
    "p_rate": "速率 快慢",
    "p_time": "时新 新旧",
    "p_strength": "强度 强弱",
    "p_temp": "温度 冷热",
    "p_direction": "聚散 收放",
    "p_luminance": "明暗 清浊",
    "p_transitivity": "施受 做功",
    "p_weight": "轻重 厚薄",
}


def main():
    lex = Lexicon()
    dims = lex.dims

    # 紧凑字典: char -> {v: [10], p: pos, n: norm, f: freq, fc: 帧一致性}
    # fc 直接取表内三位小数, 与 R32 判据 (<0.25) 两侧完全一致
    cd = {}
    for c, ch in lex.chars.items():
        cd[c] = {"v": [ch["vec"][p] for p in dims], "p": ch["pos"],
                 "n": ch["norm"], "f": ch["freq"],
                 "fc": ch.get("frame_consistency")}
    unstable_n = sum(1 for e in cd.values()
                     if (e["fc"] is not None and e["fc"] < 0.25))
    # golden 用例
    golden = []
    for s in ["价格大幅上涨，市场情绪高涨。",
              "老同学，晚上有空一起吃个饭吗？",
              "【公安局】您涉嫌洗钱案件，请立即配合调查，否则将冻结全部账户。"]:
        sol = lex.solve(s)
        golden.append({"in": s,
                       "all10": [sol["all10"][p] for p in dims],
                       "cov": sol["coverage"],
                       "attr": [[a["char"], a["weight"]] for a in
                                sol["attribution"]]})

    data = {"dims": dims, "dims_zh": DIMS_ZH, "phys7": PHYS7,
            "dict": cd, "golden": golden,
            "meta": {"version": lex.version, "n": len(lex.chars),
                     "md5": lex.probes_md5,
                     "snapshot": lex.meta["meta"]["snapshot"],
                     "unstable_n": unstable_n}}

    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False,
                                                   separators=(",", ":")))
    out = os.path.join(HERE, "compass.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"compass.html written: {os.path.getsize(out)//1024} KB, "
          f"{len(cd)} chars, {len(golden)} golden cases")


TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>语义罗盘 · 汉语动力学字典 v1.1</title>
<style>
:root{--bg:#fafaf8;--card:#fff;--ink:#222;--muted:#777;--line:#e4e2da;
--blue:#185FA5;--blue-l:#E6F1FB;--amber:#854F0B;--amber-l:#FAEEDA;
--pos:#c0392b;--neg:#0e8a4f}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.7 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
.wrap{max-width:980px;margin:0 auto;padding:28px 20px 60px}
h1{font-size:19px;font-weight:600;margin:0 0 4px}
.sub{color:var(--muted);font-size:12.5px;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;
padding:16px 18px;margin-bottom:16px}
textarea{width:100%;min-height:74px;padding:10px 12px;border:1px solid var(--line);
border-radius:8px;font:14px/1.6 inherit;resize:vertical;background:#fff}
textarea:focus{outline:2px solid var(--blue-l)}
.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
@media(max-width:720px){.row{grid-template-columns:1fr}}
button{padding:8px 22px;border:1px solid var(--blue);color:var(--blue);
background:var(--blue-l);border-radius:8px;font-size:14px;cursor:pointer;margin-top:10px}
button:hover{background:#d3e6f8}
.panel-title{font-weight:600;font-size:14.5px;margin:2px 0 10px}
.dimbar{display:flex;align-items:center;gap:8px;margin:7px 0}
.dimlabel{width:96px;font-size:12px;color:var(--ink);text-align:right;
flex-shrink:0}
.dimtrack{flex:1;height:16px;position:relative;background:#f2f0ea;
border-radius:4px;overflow:hidden}
.dimfill{position:absolute;top:0;bottom:0;border-radius:4px}
.dimval{width:52px;font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.tag{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:9px;
margin-left:6px;vertical-align:1px}
.tag.phys{background:var(--blue-l);color:var(--blue)}
.tag.abs{background:var(--amber-l);color:var(--amber)}
.stats{font-size:12.5px;color:var(--muted);margin-top:10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{color:var(--muted);font-weight:500;text-align:left;font-size:12px;
border-bottom:1px solid var(--line);padding:4px 8px}
td{border-bottom:1px solid #f0eee6;padding:4px 8px;font-variant-numeric:tabular-nums}
.zi{font-size:20px;line-height:1.2;font-weight:600}
.dimfill.pos{background:var(--pos)}
.dimfill.neg{background:var(--neg)}
.foot{color:var(--muted);font-size:11.5px;line-height:1.8;margin-top:22px;
border-top:1px solid var(--line);padding-top:12px}
#selfcheck{font-size:11.5px;margin-top:8px}
.ok{color:var(--neg)}.bad{color:var(--pos)}
</style>
</head>
<body>
<div class="wrap">
<h1>语义罗盘</h1>
<div class="sub" id="meta">汉语动力学基底字典 v1.1 · 500 字 × 10 维 · 探针指纹 <span id="md5"></span></div>
<div class="card">
  <div class="row">
    <div><div class="panel-title">文本 A</div>
      <textarea id="ta" placeholder="输入任意中文文本，如：价格大幅上涨，市场情绪高涨。"></textarea></div>
    <div><div class="panel-title">文本 B（可选，对比模式）</div>
      <textarea id="tb" placeholder="留空则只分析 A；填写则输出 A、B 与差值 B−A"></textarea></div>
  </div>
  <button onclick="run()">解算</button>
</div>
<div id="out"></div>
<div class="foot">
罗盘 = 字级离线解算（R26 判决的工程化）：10 维电荷 = 字电荷载体的加权质心。
物理 7 维（蓝标 OFFLINE_OK，R26b 可合成性 0.438）离线可信；抽象 3 维（琥珀标 LOW_CONF，0.167）建议探针复核。
高 OOV 或近零电荷时提示升级 L1 全量探针。红色=正电荷方向，绿色=负电荷方向（涨红跌绿口径）。
理论背书：R21-R31 预注册实验 31 轮（&lt;$0.40 API 成本）；字典 r25_charge_table.json；jevcore/lexicon.py 同口径。
</div>
<div id="selfcheck"></div>
</div>
<script>
const D = __DATA__;
const MD = D.dims, ABS3 = MD.filter(p=>!D.phys7.includes(p));
const el = id => document.getElementById(id);
el("md5").textContent = D.meta.md5;

function solve(text){
  const han=[...text].filter(c=>c>='\u4e00'&&c<='\u9fff');
  const inside=han.filter(c=>D.dict[c]);
  const oov=[...new Set(han.filter(c=>!D.dict[c]))];
  if(!inside.length) return {empty:true,oov,han:han.length,cov:0};
  let sw=0, m=MD.map(()=>0), attr=[];
  for(const c of inside){const e=D.dict[c];sw+=e.n;attr.push([c,e.n]);}
  for(const c of inside){const e=D.dict[c],w=e.n/sw;
    MD.forEach((p,k)=>m[k]+=w*e.v[k]);}
  attr.sort((a,b)=>b[1]-a[1]);
  const norm=Math.hypot(...m);
  return {empty:false,m,oov,han:han.length,
    inside:[...new Set(inside)],
    cov:1-oov.length/Math.max(han.length,1), attr, norm,
    l1:(oov.length/Math.max(han.length,1)>0.5)||norm<0.05};
}
function esc(s){return s.replace(/[&<>"]/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[x]))}

function bars(m){
  const mx=0.62;
  let h='';
  MD.forEach((p,k)=>{
    const v=Math.max(-mx,Math.min(mx,m?m[k]:0)), w=Math.abs(v)/mx*50;
    const phys=D.phys7.includes(p);
    h+=`<div class="dimbar"><div class="dimlabel">${D.dims_zh[p]}<span class="tag ${phys?'phys':'abs'}">${phys?'OK':'LOW'}</span></div>
    <div class="dimtrack"><div class="dimfill ${v>=0?'pos':'neg'}" style="${v>=0?`left:50%;width:${w}%`:`left:${50-w}%;width:${w}%`}"></div>
    <div style="position:absolute;left:50%;top:0;bottom:0;width:1px;background:#c8c6bc"></div></div>
    <div class="dimval">${m?(m[k]>=0?'+':'')+m[k].toFixed(3):'—'}</div></div>`;
  });
  return h;
}
function panel(title, s, text){
  let h=`<div class="card"><div class="panel-title">${title}</div>`;
  if(s.empty){h+=`<div class="stats">无可解算的字典内汉字。L1_NEEDED。</div></div>`;return h;}
  h+=bars(s.m);
  h+=`<div class="stats">覆盖 ${s.inside.length}/${s.han} 字（OOV：${s.oov.map(esc).join(' ')||'无'}，覆盖率 ${(s.cov*100).toFixed(0)}%）· 电荷范数 ${s.norm.toFixed(3)} ${s.l1?'· <b>L1_NEEDED</b>：OOV 过高或近零电荷，建议升级全量探针':'· L0 可直出'}</div>`;
  h+=`<table><tr><th>字</th><th>词类</th><th>电荷强度</th><th>主导维度</th><th>贡献权重</th></tr>`;
  let haslc=false;
  for(const [c,w] of s.attr.slice(0,8)){
    const e=D.dict[c];
    const lc=(e.fc!=null&&e.fc<0.25); haslc=haslc||lc;
    let bk=0,bv=0; e.v.forEach((x,k)=>{if(Math.abs(x)>bv){bv=Math.abs(x);bk=k}});
    h+=`<tr><td class="zi"${lc?` title="低置信字：跨框架一致性 ${e.fc} < 0.25（R32 P2：具体名物类语义在状态空间无稳定投影）"`:''}>${c}${lc?`<span style="color:#b8860b"> ⚠</span>`:''}</td><td>${e.p==='u'?'未标':e.p}</td><td>${e.n.toFixed(3)}</td><td>${D.dims_zh[MD[bk]]}</td><td>${(w*100).toFixed(1)}%</td></tr>`;
  }
  h+=`</table>`;
  if(haslc)h+=`<div class="stats">⚠ 低置信字（跨框架一致性 &lt; 0.25）：该字电荷为具体名物类投影，读数仅供参考（R32 P2 判例）。</div>`;
  h+=`</div>`;
  return h;
}
function diffPanel(a,b){
  const d=MD.map((p,k)=>b.m[k]-a.m[k]);
  let h=`<div class="card"><div class="panel-title">差值 B − A（逐维）</div>`+bars(d)+`</div>`;
  return h;
}
function run(){
  const A=el("ta").value.trim(), B=el("tb").value.trim();
  if(!A&&!B){el("out").innerHTML="";return;}
  let h="";
  if(A&&B){const a=solve(A),b=solve(B);
    h=panel("文本 A",a)+panel("文本 B",b)+(a.empty||b.empty?"":diffPanel(a,b));}
  else{const t=A||B;h=panel(t?"文本":"结果",solve(t));}
  el("out").innerHTML=h;
}
function selfcheck(){
  let ok=true, msg=[];
  for(const g of D.golden){
    const s=solve(g.in);
    if(s.empty){ok=false;msg.push(`"${g.in.slice(0,10)}…" empty`);continue;}
    let bad=false;
    s.m.forEach((v,k)=>{if(Math.abs(v-g.all10[k])>1e-6)bad=true;});
    if(bad){ok=false;msg.push(`"${g.in.slice(0,10)}…" mismatch`);}
  }
  el("selfcheck").innerHTML=(ok
    ?`<span class="ok">自检通过：${D.golden.length} 个 golden 用例与 jevcore/lexicon.solve 逐维一致（1e-6）</span>`
    :`<span class="bad">自检失败：${msg.join("; ")}</span>`);
}
selfcheck();
run();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()

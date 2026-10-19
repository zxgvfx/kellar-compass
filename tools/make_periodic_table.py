# -*- coding: utf-8 -*-
"""生成《汉字语义电荷表 · 元素周期表版》HTML 配图
数据源：r32_charge_table.json（3498 字 × 10 维实测电荷表）
布局：10 列 = 10 个维度（族）；每列上端正极（红）→ 下端负极（蓝）；
      颜色越深电荷越强；★ = 文中实验用字。
"""
import json, re, html as H

SRC = r"c:\Users\net02\WorkBuddy\2026-10-16-14-56-08\jev-experiment\r32_charge_table.json"
OUT = r"c:\Users\net02\WorkBuddy\2026-10-16-14-56-08\jev-experiment\charge_periodic.html"

AXES = [
    ("p_valence", "效价"), ("p_scale", "尺度"), ("p_rate", "速率"),
    ("p_time", "时间"), ("p_strength", "强度"), ("p_temp", "温度"),
    ("p_direction", "方向"), ("p_luminance", "明暗"), ("p_transitivity", "外放"),
    ("p_weight", "轻重"),
]
N_POLE = 11          # 每极取的字数
MAX_RANK = 3000      # 频率排名上限（太生僻的不要）
MIN_CONSIST = 0.50   # 帧一致性下限
STAR = set("好坏大小快慢美松散强启俐真假")  # 文中实验用字

HAN = re.compile(r"^[\u4e00-\u9fff]$")

d = json.load(open(SRC, encoding="utf-8"))
chars = d["chars"]

# 每个字分给它的主导维度（带电最强的那一维）
pools = {k: [] for k, _ in AXES}
skipped = 0
for ch, e in chars.items():
    if not HAN.match(ch):
        continue
    v = e["vec"]
    if any(k not in v for k, _ in AXES):
        skipped += 1
        continue
    dom = max(AXES, key=lambda a: abs(v[a[0]]))
    pools[dom[0]].append((ch, v[dom[0]], e))

def ok(ch, val, e):
    return (e.get("rank", 99999) <= MAX_RANK
            and e.get("frame_consistency", 0) >= MIN_CONSIST
            and abs(val) > 1e-4)

columns = []   # [(axis_name, [(ch, val, e)])]
for k, name in AXES:
    cand = [p for p in pools[k] if ok(*p)]
    cand.sort(key=lambda p: -p[1])
    col = cand[:N_POLE] + sorted(cand[-N_POLE:], key=lambda p: -p[1])
    # 去重（同一字不会跨列，但列内防止重复）
    seen, uniq = set(), []
    for ch, val, e in col:
        if ch not in seen:
            seen.add(ch)
            uniq.append((ch, val, e))
    columns.append((name, uniq))
    print(f"{name}({k}): 候选 {len(cand)}，取 {len(uniq)}，"
          f"正极最强 {uniq[0][0]}={uniq[0][1]:+.3f}，"
          f"负极最强 {uniq[-1][0]}={uniq[-1][1]:+.3f}")

# ---------- 生成 HTML ----------
all_chars = {}  # 供点击检查的完整数据
def cell_html(ch, val, depth, saturated):
    """depth: 0~1 电荷强度；saturated: 触及探针动态范围边界（读数不可分辨）"""
    hue, sat = (2, 78) if val > 0 else (212, 72)
    light = 95 - depth * 44          # 95% → 51%
    fg = "#fff" if depth > 0.55 else "#2a2a2a"
    star = '<i class="star">★</i>' if ch in STAR else ""
    num = (f"&asymp;{val:+.2f}" if saturated else f"{val:+.2f}")
    return (f'<div class="cell" style="background:hsl({hue},{sat}%,{light}%);color:{fg}" '
            f'data-ch="{H.escape(ch)}" title="{H.escape(ch)} {val:+.3f}｜排名 {all_chars[ch]["rank"]}">'
            f'{star}<b>{H.escape(ch)}</b><span>{num}</span></div>')

cols_html = []
for name, col in columns:
    maxabs = max(abs(v) for _, v, _ in col) or 1.0
    for ch, v, e in col:
        all_chars[ch] = e
    vtop = col[0][1]     # 该列正极最强
    vbot = col[-1][1]    # 该列负极最强
    cells = "".join(
        cell_html(ch, v, abs(v) / maxabs,
                  (v > 0 and vtop - v <= 0.012) or (v < 0 and v - vbot <= 0.012))
        for ch, v, e in col)
    cols_html.append(
        f'<div class="col"><div class="colhead">{name}</div>{cells}</div>')

AXIS_NAMES = {k: n for k, n in AXES}
data_json = json.dumps(
    {ch: {AXIS_NAMES[k]: round(e["vec"][k], 3) for k, _ in AXES}
     for ch, e in all_chars.items()}, ensure_ascii=False)

page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>汉字语义电荷表 · 元素周期表版</title>
<style>
  body{margin:0;padding:28px 24px;background:#faf9f6;
       font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;}
  .wrap{max-width:1060px;margin:0 auto;background:#fffdf9;border:1px solid #e8e2d5;
        padding:30px 34px 26px;}
  h1{font-size:26px;margin:0 0 6px;color:#26221c;letter-spacing:1px;}
  .sub{font-size:13px;color:#8a7f6d;margin:0 0 4px;}
  .legend{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:14px 0 20px;
          font-size:12.5px;color:#5c5344;}
  .chip{display:inline-flex;align-items:center;gap:5px;background:#f3efe6;
        border-radius:12px;padding:3px 10px;}
  .dot{width:9px;height:9px;border-radius:50%;}
  .board{display:flex;gap:7px;justify-content:center;}
  .col{display:flex;flex-direction:column;gap:5px;flex:1;min-width:0;}
  .colhead{font-size:13.5px;font-weight:700;text-align:center;color:#3a332a;
           background:#efe9dc;border-radius:6px;padding:6px 0;letter-spacing:2px;}
  .cell{position:relative;aspect-ratio:1/1.06;border-radius:6px;cursor:pointer;
        display:flex;flex-direction:column;align-items:center;justify-content:center;
        border:1px solid rgba(0,0,0,.06);transition:transform .12s;}
  .cell:hover{transform:scale(1.08);z-index:2;box-shadow:0 3px 12px rgba(0,0,0,.18);}
  .cell b{font-size:24px;line-height:1.15;font-weight:700;}
  .cell span{font-size:10px;opacity:.82;font-family:Consolas,monospace;}
  .cell.sel{outline:3px solid #d4a017;outline-offset:1px;}
  .star{position:absolute;top:3px;left:6px;font-size:10px;font-style:normal;color:#d4a017;}
  .foot{margin-top:18px;font-size:11.5px;color:#9a8f7d;display:flex;
        justify-content:space-between;flex-wrap:wrap;gap:6px;}
  .panel{display:none;margin-top:16px;background:#f6f2e9;border-radius:8px;padding:14px 18px;}
  .panel h3{margin:0 0 8px;font-size:16px;color:#26221c;}
  .bars{display:grid;grid-template-columns:repeat(10,1fr);gap:8px;}
  .bar{font-size:11px;color:#5c5344;text-align:center;}
  .bar .track{height:52px;background:#ece6d8;border-radius:4px;position:relative;overflow:hidden;}
  .bar .fill{position:absolute;left:0;right:0;bottom:50%;border-radius:4px 4px 0 0;}
  .bar .fill.neg{bottom:auto;top:50%;border-radius:0 0 4px 4px;}
  .bar .lab{margin-top:4px;}
</style>
</head>
<body>
<div class="wrap">
  <h1>汉字语义电荷表 · 元素周期表版</h1>
  <p class="sub">3498 个高频汉字实测 × 10 维语义电荷 —— 每列一族维度，每格一个"语义元素"</p>
  <div class="legend">
    <span class="chip"><span class="dot" style="background:hsl(2,78%,58%)"></span>正电（大 / 快 / 明）</span>
    <span class="chip"><span class="dot" style="background:hsl(212,72%,58%)"></span>负电（小 / 慢 / 暗）</span>
    <span class="chip">颜色越深 = 电荷越强</span>
    <span class="chip">≈ = 读数饱和（如效价负极 −0.43 附近，探针动态范围边界，字与字之间不宜排名）</span>
    <span class="chip"><i style="color:#d4a017;font-style:normal">★</i>文中实验用字</span>
    <span class="chip">格子下方数字 = 主导维读数</span>
  </div>
  <div class="board">__COLS__</div>
  <div class="panel" id="panel"><h3 id="pchar"></h3><div class="bars" id="bars"></div></div>
  <div class="foot">
    <span>数据：jev 53 轮预注册实验 · R32 电荷表 v2.0（3498 字 × 10 维，全量实测）</span>
    <span>自检：效价负极在 −0.43 附近饱和（恶/凶/害/惨 同读数）——探针负向动态范围不足，已列改进队列</span>
  </div>
</div>
<script>
const DATA = __DATA__;
document.querySelectorAll('.cell').forEach(c => c.addEventListener('click', () => {
  document.querySelectorAll('.cell').forEach(x => x.classList.remove('sel'));
  c.classList.add('sel');
  const ch = c.dataset.ch, v = DATA[ch];
  document.getElementById('pchar').textContent = '「' + ch + '」的 10 维电荷';
  const mx = 0.55;
  document.getElementById('bars').innerHTML = Object.entries(v).map(([k, x]) => {
    const h = Math.min(Math.abs(x) / mx, 1) * 100;
    const col = x >= 0 ? 'hsl(2,78%,55%)' : 'hsl(212,72%,55%)';
    const cls = x >= 0 ? 'fill' : 'fill neg';
    return `<div class="bar"><div class="track"><div class="${cls}" style="height:${h}%;background:${col}"></div></div><div class="lab">${k}</div></div>`;
  }).join('');
  document.getElementById('panel').style.display = 'block';
}));
</script>
</body>
</html>"""

page = page.replace("__COLS__", "".join(cols_html)).replace("__DATA__", data_json)
open(OUT, "w", encoding="utf-8").write(page)
print(f"\nOK -> {OUT}（{len(all_chars)} 字入图）")

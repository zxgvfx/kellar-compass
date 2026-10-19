# Kellar Compass · 语义罗盘与电荷表

中文语义的"化学"测量仪器：每个字/词在 10 维语义空间里有确定电荷。

- **3498 字十维电荷表**（`data/r32_charge_table.json`，2.0M 全量）——与早期版本并存：`r22`（512 字首表）、`r23`（千字级）、`r25`（v1.1 冻结版）。
- **语义罗盘 v2.1**（`html/compass.html`）：任意句子的十维电荷剖面可视化，双极复测 r>0.99。
- **电荷周期表**（`html/charge_periodic.html`）：按维度分族的字电荷全景，中文语义的"化学元素表"。
- 工具脚本：`tools/make_compass.py`（罗盘 HTML 生成器）、`tools/make_periodic_table.py`（周期表生成器）。

## 十维

效价 valence / 强度 strength / 速率 rate / 时间 time / 温度 temperature / 方向 direction / 亮度 luminance / 传递性 transitivity / 权重 weight / 尺度 scale——探针测量口径见主仓 `kellar` 的 `experiments/ROADMAP.md`（R25 字典、R32 全表扩量、R33 78 句对人类 P5=0.716 校准）。

## 状态

仪器层接近封版：复测稳定 r>0.99 ✓、对人类 P5≥0.62 ✓（v3 0.716）、已知失败模式全部有标注出口 ✓、协议冻结 ✓。

本仓库属于 Kellar 项目三仓之一：`kellar`（机制库+实验）· `kellar-compass`（本仓）· `kellar-narrative`（编辑器 MVP）。

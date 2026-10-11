// nc68 理论三问逐条答复 → Word
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, BorderStyle, WidthType, ShadingType, HeadingLevel } = require("docx");

const CN = { ascii: "Times New Roman", hAnsi: "Times New Roman", eastAsia: "SimSun" };
const HEAD = { ascii: "Arial", hAnsi: "Arial", eastAsia: "SimHei" };

const border = { style: BorderStyle.SINGLE, size: 1, color: "999999" };
const borders = { top: border, bottom: border, left: border, right: border };
const margins = { top: 80, bottom: 80, left: 100, right: 100 };

function cell(text, w, opts = {}) {
  return new TableCell({
    borders, width: { size: w, type: WidthType.DXA }, margins,
    shading: opts.head ? { fill: "E8E8E8", type: ShadingType.CLEAR } : undefined,
    children: [new Paragraph({
      children: [new TextRun({ text, font: opts.head ? HEAD : CN, size: opts.head ? 20 : 18,
                               bold: !!opts.head, color: "000000" })]
    })]
  });
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.after != null ? opts.after : 120 },
    children: [new TextRun({ text, font: opts.head ? HEAD : CN, size: opts.size || 20,
                             bold: !!opts.bold, color: "000000" })]
  });
}

const W = [500, 2350, 1650, 4526]; // sum = 9026 (A4 content width)

const rows = [
  ["Q1",
   "把 Ka/Ks 的参照思想用于表达比较，是一种研究构想。但理论上目前没有建立：1. 可以识别功能变化与背景变化的生成模型（观察到的表达数据，是怎样由功能变化、技术因素和随机误差共同产生的？）；2. 背景抵消成立的完整条件和误差界（什么形式的背景变化可以被相除抵消？近似公式误差最多多大？）；3. ω 与真实功能变化之间的确定关系（其他条件固定时，功能变化增强，ω 是否一定增强？ω 到底对应什么生物学量？）；4. 校准有效性及偏差控制的新理论结果。",
   "SI Note 20 §A + Lemma 1/2 + Proposition 3/4/5 + Supp Fig 19",
   "四点逐一建立。1）生成模型：Note 20 §A 给出 log x_g = σ_g + β_g + φ_g——σ_g 全局标度（测序深度/捕获效率）、β_g 背景因子（技术变异+中性漂移，跨面板共享）、φ_g 功能因子（仅在调控真正不同的基因上非零）；Lemma 1 证明 σ_g 在 log-softmax 归一化下精确相消（非近似，log1p 残余 O(1/x) 在伪 bulk 计数尺度 <10⁻⁴）。2）抵消条件与误差界：Lemma 2 给出 JS(p, p+δ) = (1/8 ln 2)Σδ²/p + R，线性项逐点相消（无需 Σδ=0），Lagrange 显式余项 |R| ≤ (5/48 ln 2)Σ|δ|³/(p−|δ|)₊²——乘性/加性对数域背景在比值中相消的条件即 C1–C4（二次区、背景能量面板可交换、面板稳定、计数深度足够）；误差界实测（诊断 A，2,937 真实对）：k_n 面板观测中位 2.5–4.0%（定量成立）、k_f 面板 10–18%（仅近似，已据此收窄措辞并写入 Limitations (vi)）。3）ω 与功能变化的确定关系：Proposition 3 给出 estimand ω = α + E_f/E_b + ε——ω − 1 估计的是功能与背景位移能量（χ² 型）之比，这就是 ω 在模型内对应的精确生物学量；Proposition 4 证明二次区内 ∂ω/∂E_f > 0 严格单调（全局因 JS ≤ 1 bit 饱和），ground-truth 网格实证：零背景下 ω 随注入功能位移 δ 单调上升 ρ=0.688（P=5.1e-162），k_n 平坦 ρ=0.004，纯漂移下 ω 下降 ρ=−0.821（保守方向）。4）校准理论：Proposition 5（delta 法）给出比值估计量偏差 E[ω] ≈ (μ_f/μ_n)(1 + CV_n² − ρ CV_f CV_n)，实测二阶偏差仅 −0.18%（脑）/ −0.76%（鼠），可忽略且被联合 bootstrap 传播。"],
  ["Q2",
   "ω = k_f/k_n（k_n 是两个 HK 基因概率分布之间的 JS 散度），相对于 k_f 本身配合有效零分布，HK 分母究竟增加了多少可靠的信息？能否证明“除以 HK 散度”这一步，比直接对 k_f 做正确的统计检验，增加了多少实际价值？",
   "SI Note 20 §E + MS Discussion + Supp Fig 19d",
   "三层增益逐条量化。(i) 可识别性：k_f 单独只能估计 E_f + E_b 之和——“对 k_f 做正确的统计检验”要求以该对自身的背景强度 E_b 为条件构造零分布，而 E_b 不可观测，任何不独立测量 E_b 的校准都无法分离功能与背景能量；HK 面板正是这个独立测量，使比值 E_f/E_b 可识别。这不是增量改进，而是从不可识别到可识别。(ii) 学生化：除以 k_n 使统计量的零分布对 E_b 近似 ancillary，一个全局校准即合法——与样本标准差把均值差变成 t 统计量同一逻辑。实测（诊断 C）：脑跨类零中位离散度 k_f CV 1.21 vs ω CV 0.148（max/min 195 vs 1.63，8 倍收紧）；mouse 0.436 vs 0.251——ω 的零分布在细胞类间可移植，k_f 的不可。(iii) 实测错误率：注入中性漂移下 k_f-only 假阳性率 0.81–1.00 vs ω 0.00–0.067；TCGA 反转是任何 k_f-only 分析不可见的 k_n 现象。附带理论收获：零上 per-gene 能量比 α 中位 14（脑）/8.5（TS）与经验校准基线 6.67–9.73 同阶——校准常数由此获得 winner's-curse 选择膨胀的理论解释。MS Discussion 新增学生化段落（“the logic of a t-statistic”）。"],
  ["Q3",
   "如果把实际算法、成立条件和所宣称的解释连接起来，并证明这些条件适用于文章讨论的范围，那就有一定的理论创新。",
   "SI Note 20 全文（C1–C4 逐条实测）+ Limitations (vi) + Supp Fig 19",
   "已按此标准执行——Note 20 的结构就是「算法 → 条件 → 解释 → 条件实测」的闭环。连接：Methods 的操作性算法（softmax 归一化、HK/top-200 双面板、比值+校准）经 Lemma 1/2 接到 Proposition 3 的 estimand，正文所有解释性声明（“normalizes away shared variation”、跨类排序、ω_cal 读数）都对应到 ω = α + E_f/E_b + ε 的哪一项。条件适用性逐条实测而非假设：C1（二次区）→ 诊断 A，2,937 真实对误差表（k_n 定量 / k_f 近似）；C2（背景能量面板可交换）→ 诊断 B，split-half 零上 per-gene 能量比中位 14/8.5、p10–90 给出散布范围；C3（功能面板非噪声驱动）→ Note 9 leave-pair-out 消融量化循环膨胀；C4（计数深度）→ Note 16 + notebooks/84，(d−1)/(4N ln 2) 低于背景能量。诚实边界：凡条件仅近似成立处（C2 散布、k_f 侧展开），对应声明一律按近似措辞，MS Limitations 新增 (vi) 明示 “exact at the k_n scale, approximate at the k_f scale”；Note 20 末节 Scope 声明明确哪些结论是精确数学（Lemma 1/2）、哪些是模型相对（Proposition 3–5）。"],
];

const table = new Table({
  width: { size: 9026, type: WidthType.DXA },
  columnWidths: W,
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("#", W[0], { head: true }), cell("问题", W[1], { head: true }),
      cell("答复落点", W[2], { head: true }), cell("答复内容", W[3], { head: true })] }),
    ...rows.map(r => new TableRow({ children: [
      cell(r[0], W[0], { head: false }), cell(r[1], W[1]), cell(r[2], W[2]), cell(r[3], W[3])] }))
  ]
});

const doc = new Document({
  styles: { default: { document: { run: { font: CN, size: 20, color: "000000" } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, font: HEAD, color: "000000" },
        paragraph: { spacing: { before: 240, after: 240 }, outlineLevel: 0 } },
    ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 },
      margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.HEADING_1,
        children: [new TextRun({ text: "CKI nc68：三个理论问题逐条答复", font: HEAD, bold: true, color: "000000" })] }),
      para("状态：commit 73666e6（远端 main 已核验一致）；验证链 build 234/234、XV8 64/64、SI 126/126、MS 129/129、CL+Guide 44/44、pytest 29/29；词额 MAIN 4,996/5,000、CL 527/530、Methods 2,942/3,000；投稿包 CKI_Submission_NC.zip（34 条目，含 Supplementary Fig 19）。", { after: 200 }),
      table,
      para("", { after: 120 }),
      para("策略说明：先诊断后成文——notebooks/85_theory_diagnostics.py 在 2,937 个真实对上完成四项诊断（二次区误差、背景能量交换性、零离散度、ground-truth 单调性），诊断结果直接决定措辞强弱：k_f 侧二次展开实测不达标即收窄为近似而非强辩；α 中位 14/8.5 与校准基线同阶则升级为正面论点写入 Results 与 Cover Letter。", { after: 120 }),
      para("主要改动文件：notebooks/68_gen_supplementary_nc.py（新增 SI Note 20 全文 + Supp Fig 19 图注）、notebooks/85_theory_diagnostics.py（新增，断点续跑）、notebooks/_nc68_fig_theory.py（新增，Supp Fig 19）、generate_manuscript_nc.py（Results 理论段 / Discussion 学生化段 / Limitations (vi) / 全文 Notes 1–20）、generate_cover_letter_nc.py（理论亮点句）；诊断产物 results/theory_diagnostics.csv 与同名 .md（按仓库惯例不入库，脚本可复现）。", { after: 120 }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  const out = "C:\\Users\\KnightZ\\Desktop\\细胞受选择\\CKI_nc68_理论三问逐条答复.docx";
  fs.writeFileSync(out, buf);
  console.log("Wrote " + out + " (" + buf.length + " bytes)");
});

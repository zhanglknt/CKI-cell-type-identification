// nc68 八问逐条答复 → Word
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
  ["Q1", "k_n 被进一步解释成可分离的“背景噪声量”？需要额外的噪声模型吗？", "SI Note 1.2",
   "明确 k_n 是操作性基线读数（HK 面板 JS 观测值），不是参数化噪声模型的拟合参数，无需方差分解假设；“baseline noise” 仅为各类 HK 散度来源的统称。可交换性前提由 Note 6 非 HK 锚定漂移对照 + Note 3 split-half 校准直接检验。"],
  ["Q2", "摘要 “decomposes” 究竟是数学成分分解，还是仅计算两个参照指标？", "SI Note 1.1 + 摘要",
   "Note 1.1 披露 JS 链式分解存在但 CKI 刻意不用：HK 与 identity 两子集独立重归一化分别算 JS 再取比，无跨子集可加性假设；摘要改为 “contrasts two self-normalized reference rates—a functional rate (k_f) and a baseline rate (k_n)—and reports their ratio”。"],
  ["Q3", "“normalizes away shared variation” 从数学上讲需特定模型和条件？现在满足吗？", "SI Note 1.4 + MS Intro",
   "补上四条件：(i) 小位移卡方近似 JS≈(1/8 ln 2)Σ(Δp)²/m 下共享乘性偏移在比值中相消；(ii) HK 可交换性（Note 6）；(iii) 面板固定；(iv) 维度失配可忽略（Note 16）。条件外按校准基线经验读数而非精确归一。MS 正文加 “(Supplementary Note 1.4)” 指针（词中性）。"],
  ["Q4", "“理论基线 ω=1 (k_f=k_n)” 成立吗？两个散度都为零会怎样？", "SI Note 1.4 + Fig 1e 图注",
   "ω=1 是全匹配零假设的期望值而非定理——实测基线 7.70 已证伪名义 1，ω=1 实际标志强功能约束；0/0 被 positivity guard 排除（最小实测 k_n 9.2e-5），若出现则无定义而非证据。图注 “theoretical baseline” 改为 “full-matching expectation”。"],
  ["Q5", "Dirichlet 模拟能推出所有采样模型下都没有维度影响吗？", "新脚本 notebooks/84 + Note 16",
   "不能——已实测边界并诚实写入。三族扩展（每格 2,000 对，seed 42，d∈{50,1130,2000,5000}）：(A) Dirichlet α=0.1–10，d≥1,130 比值 0.998–1.000 不变；(B) 零膨胀 z=0.5–0.9 比值 0.999–1.009 不变；(C) 有限计数采样追踪理论预测 (d−1)/(4N ln 2)（emp/theory 1.00–1.10），N=10⁴、d=5,000 时 mean JS 达 0.20 不变性破裂，N≥10⁶ 时 ≤0.002。Note 16 限定语：不变性仅限群体水平比例+足够计数深度，CKI 伪 bulk 有效 N 大且同面板置换零吸收残余。"],
  ["Q6", "低 ω 的分子减少/分母增大分别代表什么生物情况？纯分子降还能代表更易受 k_f 影响吗？", "SI Note 1.4",
   "分子降=功能约束（身份基因异常相似）；分母升=基线噪声升高（TCGA 反转机制）——生物学含义相反；纯分子降仍表示 k_f 侧约束更强，而非“对 k_f 更敏感”。故所有低 ω 排序声明均配 Note 5 组分对照。"],
  ["Q7", "比值上偏与“校准吸收”两者成立的条件是什么？", "SI Note 4",
   "吸收成立需三条件：(i) 基线与检验统计量同估计量/基因集/预处理；(ii) 偏差是 k_n 的光滑函数（delta-method ρ=0.99）；(iii) 推断对经验零分布而非绝对阈值。跨 k_n 尺度不转移——小分母对读大分母基线时 +6.5% 偏差不被吸收。"],
  ["Q8", "k_f 是哪些目标量的上界？在什么条件下成立？", "SI Note 9 + MS Limitations",
   "estimand 明确为同对非循环 leave-pair-out 面板的 k_f；1.61 倍是分布中位数（IQR 1.27–2.07），非逐对确定不等式，同背景/方案/预处理下成立。MS Limitations “inflated upper bounds” 改为 “exceed non-circular panel values”。"],
];

const table = new Table({
  width: { size: 9026, type: WidthType.DXA },
  columnWidths: W,
  rows: [
    new TableRow({ tableHeader: true, children: [
      cell("#", W[0], { head: true }), cell("问题", W[1], { head: true }),
      cell("修复位置", W[2], { head: true }), cell("修复内容", W[3], { head: true })] }),
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
        children: [new TextRun({ text: "CKI nc68：八个方法论问题逐条答复", font: HEAD, bold: true, color: "000000" })] }),
      para("状态：commit 9257603（远端 main 已核验一致）；验证链 build 233/233、XV8 64/64、pytest 29/29；MAIN 词额 4,998/5,000；投稿包 CKI_Submission_NC.zip 已重建。", { after: 200 }),
      table,
      para("", { after: 120 }),
      para("两个真软肋的处理：Q2 通过 SI Note 1.1 披露 + 摘要措辞修正彻底消除误导；Q5 不仅加了限定语，还补了 36 格新模拟把边界量化——经验值与卡方理论 (d−1)/(4N ln 2) 吻合度 1.00–1.10，边界位置与 CKI 不在边界上的理由均已写清。", { after: 120 }),
      para("主要改动文件：notebooks/68_gen_supplementary_nc.py（SI Note 1.1/1.2/1.4/4/9/16）、generate_manuscript_nc.py（摘要/Intro/Fig 1e 图注/Limitations）、notebooks/84_dirichlet_overdispersed_dimension.py（新增）；Q5 产物 results/dirichlet_overdispersed_dimension.csv 与同名 report.md（按仓库惯例不入库，脚本可复现）。", { after: 120 }),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  const out = "C:\\Users\\KnightZ\\Desktop\\细胞受选择\\CKI_nc68_八问逐条答复.docx";
  fs.writeFileSync(out, buf);
  console.log("Wrote " + out + " (" + buf.length + " bytes)");
});

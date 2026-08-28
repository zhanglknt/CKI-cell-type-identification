# CKI 复现环境设置与数据来源

> **适用版本**: CKI v0.4.0+
> **最后更新**: 2026-08-10
> **配套 Notebook**: `CKI_Reproducibility.ipynb`

---

## 1. 环境要求

| 项目 | 最低要求 | 推荐配置 |
|------|---------|---------|
| Python | >= 3.10 | 3.11+ |
| RAM | 16 GB | 32 GB (脑区分区分析) |
| 磁盘 | 20 GB 空闲 | 50 GB |
| OS | Linux / macOS / Windows | Linux |

---

## 2. 安装步骤

### 2.1 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv cki_env

# 激活环境
# Linux/macOS:
source cki_env/bin/activate
# Windows:
cki_env\Scripts\activate
```

### 2.2 安装依赖

```bash
# 方式一：从 requirements.txt 安装
pip install -r requirements.txt

# 方式二：从 pyproject.toml 安装（含 CKI 包本身）
pip install -e ".[all]"
```

### 2.3 验证安装

```python
import cki
from cki.core import js_divergence, compute_omega
print(f"CKI version: {cki.__version__}")  # 应输出 >= 0.4.0
```

---

## 3. 数据来源

### 3.1 数据总览

所有数据文件需放置在 `data/` 目录下，结构如下：

```
data/
├── housekeeping/
│   └── Human_Mouse_Common.csv       # HRT Atlas 管家基因列表
├── FACS/
│   └── FACS/                        # Tabula Muris 各组织 count 矩阵
│       ├── Liver-counts.csv
│       ├── Kidney-counts.csv
│       ├── Spleen-counts.csv
│       ├── Lung-counts.csv
│       ├── Heart-counts.csv
│       └── Marrow-counts.csv
├── annotations_FACS.csv             # Tabula Muris 细胞注释
├── metadata_FACS.csv                # Tabula Muris 元数据
├── ts_human/                        # Tabula Sapiens 各器官 h5ad
│   ├── TS_Liver.h5ad
│   ├── TS_Kidney.h5ad
│   ├── TS_Heart.h5ad
│   ├── TS_Bone_Marrow.h5ad
│   ├── TS_Spleen.h5ad
│   └── TS_Lung.h5ad
├── tcga/                            # TCGA 数据
│   ├── tcga_RSEM_gene_tpm.gz        # TCGA RSEM TPM 基因表达矩阵
│   └── probemap.tsv                 # ENSG ID → Gene Symbol 映射
└── brain/
    └── Nonneurons.h5ad              # Siletti 脑图谱（非神经元）
```

### 3.2 详细来源

#### A. Tabula Muris FACS（小鼠）

- **论文**: Schaum et al., *Nature* 2018, "Single-cell transcriptomics of 20 mouse organs creates a Tabula Muris"
- **下载**: https://figshare.com/projects/Tabula_Muris_Transcriptomic_characterization_of_20_organs_and_tissues_from_Mus_musculus_at_single_cell_resolution/27733
- **文件**: FACS 各组织的 `*_counts.csv.gz`（解压后改名 `<tissue>-counts.csv`）
- **注释**: `annotations_FACS.csv` 来自 Tabula Muris 项目
- **元数据**: `metadata_FACS.csv` 来自 Tabula Muris 项目

#### B. Tabula Sapiens（人类）

- **论文**: Jones et al., *Science* 2022, "The Tabula Sapiens: A multiple-organ, single-cell transcriptomic atlas of humans"
- **下载**: https://tabula-sapiens-portal.ds.czbiohub.org/ （或 Console）
- **文件**: 6 个器官的 h5ad 文件（Liver, Kidney, Heart, Bone Marrow, Spleen, Lung）
- **推荐**: 使用预处理的 per-organ h5ad（每个 ~1-2 GB）

#### C. TCGA Pan-Cancer（人类肿瘤）

- **来源**: UCSC Xena
- **下载**: https://xenabrowser.net/datapages/
- **文件**:
  - `tcga_RSEM_gene_tpm` — TCGA PANCAN RSEM 基因 TPM 矩阵（~740MB gz）
  - `probeMap` — GENCODE v23 探针映射
- **注意**: TCGA 数据属于 Controlled Access（部分队列），如无法访问可跳过 Part 3

#### D. Siletti 脑图谱（人类脑区）

- **论文**: Siletti et al., *Science* 2023, "Transcriptomic diversity of cell types across the adult human brain"
- **下载**: https://zenodo.org/records/7865491
- **文件**: `Nonneurons.h5ad`（~4.5 GB）
- **注意**: 脑区分析需要 >= 16 GB RAM，推荐 >= 32 GB

#### E. 管家基因列表（HRT Atlas）

- **来源**: HRT Atlas v1.0 (Housekeeping & Reference Transcript Atlas)
- **网站**: http://www.housekeeping.unicamp.br/
- **论文**: Hounkpe et al., *Nucleic Acids Research* 2021
- **文件**: `Human_Mouse_Common.csv` 已在 repo 中
  - 包含 1,130 个 human HK 基因和 1,105 个 mouse HK 基因（人鼠共同部分）
- **无需重新下载**，已在 CKI 包中内置

---

## 4. 运行复现 Notebook

### 4.1 启动 Jupyter

```bash
jupyter notebook CKI_Reproducibility.ipynb
```

### 4.2 Notebook 结构

| Part | 内容 | 数据集 | Pairs 数 | 预计运行时间 |
|------|------|--------|----------|------------|
| 1 | 小鼠先导验证 + 全矩阵 | Tabula Muris FACS | 15 + 703 | 10-20 分钟 |
| 2 | 人类独立验证 + 方法比较 | Tabula Sapiens | 5,151 | 1-2 小时 |
| 3 | TCGA 肿瘤-正常 ω | TCGA | ~20,000 | 1-2 小时 |
| 3b | 临床分层分析（paired/unpaired） | TCGA + cBioPortal | — | 30 分钟* |
| 4 | 脑区跨区域分析 | Siletti Atlas | 31,764 | 4-8 小时 |
| 5 | 结果汇总与交叉验证 | — | — | 1 分钟 |

\* Part 3b 需要额外的 cBioPortal 临床数据 API 访问

### 4.3 跳过特定 Part

如果缺少某些数据集，可以直接跳过对应的 Section：
- 无 TCGA 数据：跳过 Part 3 和 3b
- 无脑图谱数据：跳过 Part 4
- 仅需小鼠/人类核心结果：运行 Part 1 + Part 2 即可

---

## 5. 输出结果

所有结果输出到 `results/` 目录：

| 文件 | 内容 | Notebook Part |
|------|------|--------------|
| `mouse_pilot_v2b_results.csv` | 小鼠先导 ω + P 值 | Part 1 |
| `mouse_pilot_v2b_key_values.csv` | 小鼠先导汇总统计 | Part 1 |
| `full_matrix_omega.csv` | 小鼠 703 对 ω 矩阵 | Part 1 |
| `full_matrix_pairs.csv` | 小鼠全矩阵 pairs 列表 | Part 1 |
| `phase33_v3_human_*.csv` | 人类 ω 矩阵和 pairs | Part 2 |
| `phase34_v2_*_pairs.csv` | TCGA 各癌种 pairs | Part 3 |
| `phase34_v2_summary.csv` | TCGA 各癌种汇总 | Part 3 |
| `brain_siletti_omega_pairs_v3.csv` | 脑区 pair ω | Part 4 |
| `brain_siletti_ct_summary_v3.csv` | 脑区各细胞类型汇总 | Part 4 |
| `brain_siletti_migration_candidates_v3.csv` | 迁移候选信号 | Part 4 |

---

## 6. 关键数值验证

运行完 Notebook 后，验证以下 6 组核心数值与稿件一致：

### (1) LIHC Edmondson grade ω

| Grade | ω (mean) | n |
|-------|----------|---|
| G1 | 101.8 | 39 |
| G2 | 100.2 | 133 |
| G3 | 96.8 | 105 |
| G4 | 90.0 | 11 |

Part 3b → `phase34_clinical_severity.csv`

### (2) BRCA PAM50 subtype ω

| Subtype | ω |
|---------|-----|
| Luminal A | 344.5 |
| Luminal B | 313.6 |
| HER2-enriched | 263.0 |
| Basal-like | 223.4 |
| Normal-like | 108.0 |

Part 3b → `phase34_clinical_severity.csv`

### (3) LUAD EGFR/KRAS mutation ω

| Genotype | ω |
|----------|-----|
| EGFR-mutant | 285.3 |
| KRAS-mutant | 284.6 |
| Wild-type | 237.6 |

Part 3b → `phase34_clinical_severity.csv`

### (4) 脑区分化梯度

- 跨细胞类型 ω 梯度: ~6.1x
- Bergmann glia ω: ~2.4
- Astrocyte ω: ~14.4

Part 4 → `brain_siletti_ct_summary_v3.csv`

### (5) CKI vs 标准指标 Spearman 相关

| 对比 | r |
|------|---|
| CKI vs Raw JS | -0.550 |
| CKI vs Spearman distance | -0.568 |
| CKI vs Cosine distance | -0.442 |
| CKI vs Marker Jaccard | -0.384 |

Part 2 → `figure_data_correlations.npy`

### (6) Table 1 AUC 值

| 指标 | AUC |
|------|-----|
| CKI ω | 0.716 |
| Cosine distance | 0.887 |
| Raw JS divergence | 0.836 |
| Marker Jaccard | 0.801 |
| Spearman distance | 0.690 |

Part 2 → `figure_data_auc.npy`

---

## 7. 常见问题

### Q: `import cki` 失败
确认 CKI 包已安装：`pip install -e .`（在项目根目录运行）

### Q: 数据文件未找到
检查 `data/` 目录结构是否与 §3.1 一致

### Q: 内存不足 (Part 4 脑区)
- 确保 >= 16 GB RAM
- 关闭其他占用内存的程序
- 可在 `read_h5ad` 时添加 `backed='r'` 参数

### Q: TCGA 数据无法下载
TCGA 部分数据受控访问。如无法获取，跳过 Part 3 不影响核心结果（Part 1 + 2 完全公开数据）

### Q: 数值与稿件不一致
确认使用的是 `cki/core.py` 稿件版本（`np.log` 而非 `np.log2`，无 `kn_min` floor）：
```bash
grep -n "log2\|kn_min" cki/core.py
# 应该无输出（确认无 log2 和 kn_min）
```

---

## 8. 参考信息

- **CKI GitHub**: https://github.com/zhanglknt/CKI-cell-type-identification
- **CKI 版本**: v0.4.0（代码与发布一致）
- **关键提交**: cki/core.py 使用 base-2 log（`np.log2`，与稿件一致），支持可选 `kn_floor`（默认 0，仅正性保护；TCGA 分析用 1e-4）

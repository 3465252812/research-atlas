# 3DGS 方法合集与技术演进图

使用本仓库的通用模板展示既有 3D Gaussian Splatting 文献记录：**493 个方法、21 类技术方向、484 条技术关联、5 篇综述来源**。

- [交互式 HTML](index.html)：下载后用浏览器打开，或克隆仓库后直接打开本文件夹中的 `index.html`。GitHub 文件页面只展示源码。
- [结构化数据](project-data.json)：可使用仓库脚本重新构建、校验和导出。

界面包含方法合集和技术演进图，图谱首次打开和重置后均展示全部 **493 个方法、484 条关系**，不设置精选主线。可搜索、筛选、分页、查看论文与方法详情、定位节点、筛选关系、缩放拖动及导出 JSON / SVG。搜索唯一方法时自动显示直接关联节点和连线。

数据保留已有论文与方法 ID、常规技术分类、方法间关系、综述引用和日期来源记录。只有常规方法视图，`research_tracks` 为空；原始资料不随示例分发。

技术方向采用“辐射场表示”“高斯光栅化”“稀疏视角重建”“3DGS-SLAM”等任务或机制术语。[命名对照和文献依据](taxonomy-notes.md)记录全部21类的调整，分类ID和方法归属不变。

原记录截止日期为 **2026-10-13**。**2026-11-14** 对14个原缺日期且无连线的方法进行局部复核，依据 arXiv、CVF 论文集和作者机构记录补充日期及20条有来源的关系；原有464条关系保留。具体依据、位置及核验状态见 JSON，未对全库重新检索或逐篇核验。同方向连线不表示继承，部分方法价值仍为空。

GaussianImage 采用 arXiv v1 的 **2024-03-13**。HHAvatar 采用动态头发扩展 v3 的 **2024-11-20**，与早期 Gaussian Head Avatar 区分。两项仅有官方论文集月份证据的记录按 **2025-10** 放置，不推定具体日。`method-157` 和 `method-175` 很可能对应 GaussianMesh 的不同题名记录，以版本对照关联，保留稳定 ID，未自动合并。

在仓库根目录运行：

```bash
python scripts/validate_data.py examples/3dgs/project-data.json --report output/3dgs-validation.json
python scripts/build_html.py examples/3dgs/project-data.json --output output/3dgs/index.html
```

构建目录还会包含文献 CSV/BibTeX、分类与关系 JSON、核验报告和待核清单。`output/` 为本地生成目录，不提交到仓库。

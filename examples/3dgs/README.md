# 3DGS 方法合集与技术演进图

使用本仓库的通用模板展示既有 3D Gaussian Splatting 文献记录：**493 个方法、21 类技术方向、464 条技术关联、5 篇综述来源**。

- [交互式 HTML](index.html)：下载后用浏览器打开，或克隆仓库后直接打开本文件夹中的 `index.html`。GitHub 文件页面只展示源码。
- [结构化数据](project-data.json)：可使用仓库脚本重新构建、校验和导出。

界面包含方法合集和技术演进图，图谱首次打开和重置后均展示全部 **493 个方法、464 条关系**，不设置精选主线。可搜索、筛选、分页、查看论文与方法详情、定位节点、筛选关系、缩放拖动及导出 JSON / SVG。

数据保留已有论文与方法 ID、常规技术分类、方法间关系、综述引用和日期来源记录。只有常规方法视图，`research_tracks` 为空；原始资料不随示例分发。

本次为既有数据的模板化整理，没有新增文献检索或原文复核。原记录截止日期为 **2026-10-13**；缺失信息和关系判断仍保留待核标记，同方向连线不表示继承。部分方法价值尚待补充，保持为空。示例不代表穷尽收录或已完成全部事实核验。

在仓库根目录运行：

```bash
python scripts/validate_data.py examples/3dgs/project-data.json --report output/3dgs-validation.json
python scripts/build_html.py examples/3dgs/project-data.json --output output/3dgs/index.html
```

构建目录还会包含文献 CSV/BibTeX、分类与关系 JSON、核验报告和待核清单。`output/` 为本地生成目录，不提交到仓库。

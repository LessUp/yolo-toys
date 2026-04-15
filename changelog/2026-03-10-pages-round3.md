---
date: "2026-03-10"
title: "GitHub Pages 第三轮优化"
---

# 2026-03-10 GitHub Pages 第三轮优化

## 变更内容

### CI 工作流优化
- **ci.yml 添加 paths-ignore** — 文档专属文件（`*.md`、`docs/`、`changelog/`、`_config.yml`、`index.md`、`LICENSE`、`404.md`）变更不再触发 CI 构建，节省 CI 分钟数
- **移除冗余 master 分支** — 仓库仅使用 `main`，移除多余的 `master` 触发条件

### Pages 工作流优化
- **cancel-in-progress 改为 true** — 快速连续推送文档变更时，自动取消旧的构建任务，避免排队等待
- **sparse-checkout 添加 404.md** — 确保自定义 404 页面被正确构建

### Jekyll 配置增强
- **添加 jekyll-sitemap 插件** — 自动生成 `sitemap.xml`，改善搜索引擎索引

### 新增文件
- **404.md** — 自定义 404 错误页面，提供返回首页链接，提升用户体验

### 文档修正
- **docs/README.md** — `python3` 改为 `python`（跨平台兼容），添加虚拟环境激活步骤（Linux/macOS + Windows）
- **index.md** — 添加 Pages 部署状态 badge，更新最近更新表

### Changelog
- **changelog/index.md** — 添加本轮变更记录条目

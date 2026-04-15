---
date: "2026-02-25"
title: "前端 UI 美化优化"
---

# 2026-02-25 前端 UI 美化优化

## 概述
对前端进行全面视觉优化，提升设计质感和交互体验，零破坏性改动（不涉及 JS 逻辑）。

## 改动文件
- `frontend/index.html` — 引入 Google Fonts、更新版本号
- `frontend/style.css` — 全面 CSS 改造

## 详细变更

### 字体系统
- 引入 **Inter** 作为正文字体，**JetBrains Mono** 作为等宽字体
- 新增 `--font-sans` / `--font-mono` CSS 变量统一管理
- 启用字体抗锯齿优化

### 设计 Token 扩展
- 新增 `--primary-subtle`、`--accent-glow`、`--shadow-lg`、`--radius-xl` 变量
- 新增 `--transition-fast` / `--transition-normal` / `--transition-slow` 统一动效时长

### Header
- 底部渐变装饰线 (primary → accent)
- Logo hover 旋转动效
- 版本徽章改为胶囊形 + mono 字体 + 边框

### 空白状态
- SVG 图标呼吸脉搏动画 (`emptyPulse`)
- 标题文字渐变色 (`background-clip: text`)
- 舞台区域微弱径向渐变背景

### 按钮系统
- hover 上浮 (`translateY(-1px)`)
- active 按下缩放 (`scale(0.97)`)
- Primary 按钮悬浮发光阴影
- Danger 按钮悬浮红色光晕
- Icon 按钮独立 hover 行为

### 控制栏
- 顶部渐变分隔线（透明 → border → primary → border → 透明）
- Stats bar 改为胶囊形背景

### 侧边栏
- 统计卡片改为无分隔线设计，行 hover 高亮
- 类别项 hover 右移微动效 + 边框显现
- Count 徽章胶囊化 + mono 字体

### 设置面板
- 滑入动画使用 cubic-bezier 缓动
- Section 间增加 border-bottom 分隔
- Model Tabs 改为嵌套在背景容器中的 segmented control 风格
- Checkbox label hover 高亮背景
- Model item selected 状态增加 box-shadow ring

### Toast 通知
- 左侧 3px 彩色条指示类型
- 弹性入场动画 (`cubic-bezier(0.21, 1.02, 0.73, 1)`)
- 容器 `pointer-events: none` 避免遮挡

### 其他
- 自定义滚动条（6px 细条、圆角、hover 变色）
- 文本选中色匹配主题
- Overlay info / Caption result 增加 border + shadow
- Caption result 入场淡入动画
- 响应式断点增加移动端 padding/字号调整
- 版本号更新为 v3.0

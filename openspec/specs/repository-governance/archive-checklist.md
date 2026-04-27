# YOLO-Toys 归档就绪检查清单

> 最后更新: 2026-04-27

本文档定义了项目达到「最终完结状态」必须满足的所有条件。

---

## 结构完整性

- [ ] 目录结构符合 `PROJECT_STRUCTURE.md` 规范
- [ ] 无遗留缓存文件 (`__pycache__`, `.ruff_cache`, `.pytest_cache`)
- [ ] 无重复或冗余文档
- [ ] 模型文件位于 `models/` 目录
- [ ] `.gitignore` 规则完整

## 代码质量

- [ ] 所有测试通过 (`make test`)
- [ ] 测试覆盖率 >= 80%
- [ ] 无安全漏洞 (`pip-audit`)
- [ ] 无 lint 错误 (`make lint`)
- [ ] 无类型错误 (`basedpyright`)
- [ ] 代码风格一致 (`make format`)

## 文档完整性

- [ ] 所有文档有英文版本
- [ ] 核心文档有中文版本
- [ ] CHANGELOG 遵循 Keep a Changelog 格式
- [ ] README 准确反映项目现状
- [ ] API 文档与实现同步

## 自动化完整性

- [ ] CI 流程全部通过
- [ ] GitHub Pages 正常部署
- [ ] 安全扫描无高危问题
- [ ] Dependabot 正常工作

## 元数据完整性

- [ ] `pyproject.toml` 信息完整且准确
- [ ] LICENSE 文件存在
- [ ] GitHub 仓库 description 和 tags 已配置

---

## 验收命令

```bash
# 1. 代码质量检查
make lint && make format --check

# 2. 类型检查
basedpyright app/

# 3. 测试验证
make test

# 4. 安全检查
pip-audit

# 5. 构建验证
pip wheel . --no-deps -w dist/
```

---

## 签署

当所有检查项都打勾时，项目即达到归档就绪状态。

| 角色 | 签署 | 日期 |
|------|------|------|
| 项目负责人 | | |
| 代码审查 | | |
| QA 验收 | | |

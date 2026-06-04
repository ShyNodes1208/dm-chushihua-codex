# Git 代码管理指南

> 远程仓库: https://github.com/ShyNodes1208/dm-chushihua-codex.git

## 1. 首次提交（初始化仓库）

```bash
cd E:\code\dm-chushihua-codex

# 初始化 Git（如果还没有 .git）
git init

# 添加远程仓库
git remote add origin https://github.com/ShyNodes1208/dm-chushihua-codex.git

# 将所有文件加入暂存区
git add .

# 提交
git commit -m "init: 达梦多实例 SQL 查询看板"

# 推送到 GitHub（首次需要 -u 建立追踪）
git branch -M main
git push -u origin main
```

## 2. 日常提交流程

```bash
# 查看当前状态（哪些文件改了）
git status

# 查看具体改了什么
git diff

# 将改动加入暂存区
git add .                          # 添加全部改动
git add app.py                     # 或只添加指定文件

# 提交
git commit -m "类型: 简短描述"

# 推送到 GitHub
git push
```

## 3. 提交信息规范

采用 `类型: 描述` 格式，保持清晰可追溯：

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 添加导出 Excel 功能` |
| `fix` | 修复 Bug | `fix: 修复 SQL 注入漏洞` |
| `docs` | 文档变更 | `docs: 添加离线部署说明` |
| `refactor` | 代码重构 | `refactor: 优化数据库连接管理` |
| `chore` | 杂项/配置 | `chore: 更新 .gitignore` |
| `style` | 格式调整 | `style: 统一缩进为 4 空格` |

## 4. 建议的 .gitignore

在项目根目录创建 `.gitignore` 文件，排除不应提交的内容：

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.venv/

# 运行时文件
cache/*.json
*.log

# 离线包/发布文件（体积大，不需要版本管理）
release/
offline_package/
offline_packages/

# IDE
.vscode/
.idea/

# 环境配置（含密码的 config 不要提交）
config.json

# 系统文件
Thumbs.db
Desktop.ini
```

> ⚠️ **重要**: `config.json` 包含数据库密码，**绝对不要提交到 GitHub**。应提供一个 `config.example.json` 模板给其他开发者参考。

## 5. 创建配置模板（替代 config.json）

```bash
# 复制一份去掉密码的模板
cp config.json config.example.json
# 然后编辑 config.example.json，把 password 改为 "YOUR_PASSWORD"
```

提交 `config.example.json`，不提交 `config.json`。

## 6. 分支管理（推荐）

```
main          ← 稳定版本，可随时部署
  └── dev     ← 日常开发
       ├── feat/xxx   ← 新功能分支
       └── fix/xxx    ← Bug 修复分支
```

```bash
# 创建开发分支
git checkout -b dev
git push -u origin dev

# 开发新功能
git checkout -b feat/excel-export
# ... 写代码 ...
git add .
git commit -m "feat: Excel 导出支持多 sheet"
git push -u origin feat/excel-export

# 合并回 dev
git checkout dev
git merge feat/excel-export
git push
```

## 7. 常用操作速查

```bash
# 撤销工作区改动
git checkout -- app.py

# 撤销 git add
git reset HEAD app.py

# 撤销最近一次 commit（保留改动）
git reset --soft HEAD~1

# 查看提交历史
git log --oneline -10

# 查看远程仓库地址
git remote -v

# 拉取远程更新
git pull

# 强制覆盖本地（谨慎！）
git fetch origin
git reset --hard origin/main
```

## 8. 首次推送如果报错

如果 GitHub 仓库已有 README 或 LICENSE 导致冲突：

```bash
# 先拉取远程内容并合并
git pull origin main --allow-unrelated-histories

# 解决冲突后再推送
git push -u origin main
```

## 9. Token 认证（2026 年 GitHub 已不支持密码登录）

如果推送时提示认证失败，需要用 Personal Access Token：

1. 登录 GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新 Token，勾选 `repo` 权限
3. 推送时用户名填 GitHub 用户名，密码填 Token

```bash
# 缓存凭据（避免每次输入）
git config --global credential.helper wincred
```

---

> **一句话总结**: `git add` → `git commit` → `git push`，记得不要把 `config.json` 和 `release/` 提交上去。

# 达梦多实例 SQL 查询看板

这是一个轻量 Flask Web 应用，用于对多个达梦数据库实例执行同一份 SQL，并把结果汇总展示到网页中。支持 SQL 模板变量、JSON 缓存、缓存状态提示、前端搜索、分页和 Excel 导出。

## 主要功能

- 多实例并发查询，结果按实例汇总成表格
- 缓存状态提示：SQL 改动会标记"已过期"，并按时间显示"数据是多久前查的"
- 顶部成功/失败汇总，可一键"只看失败"
- **连接测试**：逐台探测实例是否可连通
- **网页内管理**：直接在"管理"弹窗里增删改实例与 SQL 模板，无需手改文件
- **定时自动刷新**：可设置每 30 秒 ~ 10 分钟自动刷新当前查询
- **对比上次**：高亮本次与上次查询结果的差异单元格
- 列设置（显隐/列宽/排序）会记忆在浏览器本地；支持深色模式
- 导出：导出当前查询（尊重搜索词与可见列）或一键导出全部查询到一个 Excel
- 双击单元格复制内容，Shift+双击复制整行
- 可选访问口令保护（默认关闭）

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`dmPython` 需要达梦客户端环境支持。如果暂未安装，应用仍可启动，但刷新查询时会在对应实例行显示驱动缺失错误。

## 配置

编辑 `config.json`：

```json
{
  "instances": [
    {"label": "DB-01", "host": "192.168.1.101"},
    {"label": "DB-02", "host": "192.168.1.102"}
  ],
  "defaults": {
    "port": 5236,
    "user": "SYSDBA",
    "password": "SYSDBA"
  },
  "sql_dir": "./sql_templates",
  "cache_dir": "./cache",
  "page_size": 10
}
```

`defaults` 会作为所有实例的默认连接信息；单个实例可写同名字段覆盖默认值。

可选字段：

- `cache_max_age_minutes`：数据超过该分钟数后界面提示"已过期"，`0` 表示不提示。
- `auth`：`{"enabled": true, "password": "口令"}` 开启访问口令；也可用环境变量 `DM_AUTH_PASSWORD` 临时开启。
- 密码避免明文：推荐把真实密码写在 `config.local.json`（已被 git 忽略，不会提交），例如 `{"defaults": {"password": "真实密码"}}`，它会自动覆盖 `config.json` 里的占位值；`config.json` 中保留 `"env:DM_PASSWORD"` 占位即可。也可改用环境变量：设置 `DM_PASSWORD` 覆盖默认密码。
- 调试模式：默认关闭，需要时设置环境变量 `DM_DEBUG=1`。

## SQL 模板

把 `.sql` 文件放到 `sql_templates/` 下，文件名就是查询名称。支持以下变量：

- `${host}` 当前实例 IP
- `${port}` 当前实例端口
- `${label}` 当前实例标签
- `${user}` 当前实例用户名
- `$${name}` URL 查询参数，例如刷新时请求 `/api/query/demo/refresh?name=test`

内置示例为 `sql_templates/instance_info.sql`。

## 启动

```powershell
python app.py
```

浏览器打开 `http://127.0.0.1:5000`。

## API

- `GET /`：主页
- `GET /api/session`：是否启用口令、是否已登录
- `POST /api/login` / `POST /api/logout`：登录 / 退出（启用口令时）
- `GET /api/queries`：查询列表和缓存状态
- `GET /api/query/<name>`：读取缓存结果（含上次快照，用于对比）
- `POST /api/query/<name>/refresh`：刷新单个查询
- `POST /api/refresh-all`：刷新全部查询
- `POST /api/test-connections`：逐台连接测试
- `GET /api/query/<name>/export`：导出单个查询（支持 `search`、`columns`）
- `GET /api/export-all`：导出全部查询到一个 Excel
- `GET /api/config` / `POST /api/instances`：读取配置 / 保存实例列表
- `GET /api/sql/<name>` / `POST /api/sql/<name>` / `DELETE /api/sql/<name>`：管理 SQL 模板

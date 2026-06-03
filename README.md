# 达梦多实例 SQL 查询看板

这是一个轻量 Flask Web 应用，用于对多个达梦数据库实例执行同一份 SQL，并把结果汇总展示到网页中。支持 SQL 模板变量、JSON 缓存、缓存状态提示、前端搜索、分页和 Excel 导出。

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
- `GET /api/queries`：查询列表和缓存状态
- `GET /api/query/<name>`：读取缓存结果
- `POST /api/query/<name>/refresh`：刷新单个查询
- `GET /api/query/<name>/export`：导出 Excel
- `POST /api/refresh-all`：刷新全部查询

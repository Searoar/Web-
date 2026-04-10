# 故事与星空慢游规划 API

FastAPI + SQLAlchemy + SQLite。用户创建多段行程（交通方式 + 距离），挂载文学/取景地与暗夜观星点；提供行程摘要与「碳足迹 / 叙事连贯度 / 观星适宜度」分析端点。

## 环境

- Python 3.11+（推荐）

## 安装与运行

```bash
cd code
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- 交互式文档：<http://127.0.0.1:8000/docs>（Swagger UI 已开启 **`persistAuthorization`**，Authorize 一次后刷新页面仍保留 Key）
- 本地数据库文件：默认 `slowtravel.db`（可在环境变量 `SQLITE_PATH` 中覆盖；测试使用 `SQLITE_PATH=:memory:`）
- 环境变量示例见 `.env.example`（可复制为 `.env`）

### 鉴权（写操作）

- `POST /journeys`、`PATCH /journeys/{id}`、`DELETE /journeys/{id}` 需在请求头携带 **`X-API-Key`**，与配置项 **`API_KEY`**（默认 `dev-api-key`）一致。OpenAPI 中已声明 **`apiKey`** 安全方案（Header 名 `X-API-Key`），在 **`/docs` 右上角 Authorize** 填入与 `API_KEY` 相同的值即可对写操作一键带 Key。
- 所有 **GET**（含 `/journeys`、`/reference/*`）为公开读取，无需密钥。
- 将 **`API_KEY` 设为空字符串** 可关闭校验（仅建议本地调试；生产或提交演示请保留密钥）。

### 分页（列表类 GET）

所有带分页的列表端点使用统一查询参数 **`skip`**、**`limit`**（定义见 `app/pagination.py`）：

- **`skip`**：非负整数，默认 **0**（从第几条开始偏移）。
- **`limit`**：默认 **50**，最小 **1**，最大 **500**（`MAX_PAGE_SIZE`）。超出范围会返回 **422**。

### 错误与状态码约定

| 情况 | HTTP | `error.code` |
|------|------|----------------|
| 旅程 id 在 URL 中不存在 | 404 | `not_found` |
| `literary_location_id` / `dark_sky_site_id` / `naptan_access_node_id` 在库中不存在 | **422** | `invalid_reference` |
| 请求体/查询不符合 Pydantic 模式（含类型错误、空标题等） | 422 | `validation_error` |
| 写操作缺少或错误 API Key | 401 | `unauthorized` |

说明：外键类引用错误使用 **422**（语义上「请求内容不可处理」）；URL 上的旅程资源不存在使用 **404**。成功响应体仍为各端点定义的模型；错误响应统一为 `{"error": {...}}`（校验失败可含 `errors` 列表）。

## `data/` 目录里的 CSV 有什么用？怎么进 API？

- **作用**：`data/` 里是**开放数据示例或小样本**（见仓库 `data/DATASETS.md`），用来**扩充**数据库里的两类**参考表**：`literary_locations`（文学/取景/遗产点）、`dark_sky_sites`（观星点）。用户创建旅程时，`POST /journeys` 里填的 `literary_location_id`、`dark_sky_site_id` 必须对应这些表里的 `id`；导入越多，可选点越多。
- **与代码的关系**：应用启动时 `app/seed.py` 会先写入一批**内置种子**；你额外下载或维护的 CSV 可通过下面脚本**合并导入**（已存在的 `title+latitude` / `name+latitude` 会跳过，避免重复）。
- **NaPTAN / NPTG（加分项）**：全量/样本 CSV 可导入表 **`naptan_access_nodes`**、**`nptg_localities`**，并通过 **`GET /reference/naptan-access-nodes`**、**`GET /reference/nptg-localities`** 查询。行程经停 **`POST/PATCH /journeys`** 的 `stops[]` 中可填 **`naptan_access_node_id`**（与 `literary_location_id` 等并列，均为可选外键）。ETL 见下「NaPTAN/NPTG ETL」。

**导入命令**（在 `code` 目录执行，需已配置 `SQLITE_PATH` 或默认 `./slowtravel.db`）：

```bash
python -m scripts.import_local_data
```

若 `data` 不在默认相对路径，可指定：

```bash
python -m scripts.import_local_data --data-root "G:\...\cwk1\data"
```

导入后重启或直接用同一数据库文件，调用 **`GET /reference/literary-locations`**、**`GET /reference/dark-sky-sites`** 即可看到新数据；创建旅程时用返回 JSON 里的 `id` 作为外键即可。

再次运行若显示 **新增 0 条、跳过若干条**，表示 CSV 行与库里已有记录重复（含启动时 `seed` 或上次导入），属正常。需要重新全量导入时可**删除** `slowtravel.db` 后再执行导入脚本。

### NaPTAN / NPTG ETL（`data/downloads/transport`）

默认从仓库 **`../data/downloads/transport/`** 读取 `naptan_access_nodes_HEAD_2mb.csv` 与 `nptg_localities.csv`（与 `DATASETS.md` 下载说明一致），批量写入 `naptan_access_nodes`、`nptg_localities`（按 `atco_code` / `nptg_locality_code` 去重）。演示库多为**小样本**；文学/取景地仍以启动时 **`seed`** 为主，导入 CSV 是在种子之上**合并**更多可选点。

**改为「全量」对接 NaPTAN/NPTG（作业演示外）：**

1. 从英国交通开放数据门户（如 [data.gov.uk NaPTAN](https://data.gov.uk/) 相关数据集）或官方发布的 **NaPTAN / NPTG** 全量包下载 **CSV**（全量 Stops 可达数百万行、体积很大，勿提交进 Git）。
2. 将下载路径传给 ETL，例如：  
   `python -m scripts.etl_naptan_nptg --naptan-csv "D:\datasets\naptan\Stops.csv" --nptg-csv "D:\datasets\nptg\Localities.csv"`（列名需与脚本中读取的字段一致，如 `ATCOCode`、`Latitude`、`Longitude` 等；具体文件名以官方包为准）。
3. 首次全量导入建议在**空库或备份后**执行，并预留足够磁盘与导入时间；导入完成后 `GET /reference/naptan-access-nodes` 即可分页浏览真实全国站点。

```bash
python -m scripts.etl_naptan_nptg
python -m scripts.etl_naptan_nptg --naptan-csv "..\\..\\data\\downloads\\transport\\naptan_access_nodes_HEAD_2mb.csv"
```

### Alembic 数据库迁移

- 迁移脚本目录：`code/alembic/versions/`。
- **文件数据库**（默认 `./slowtravel.db`）：应用启动时会执行 **`alembic upgrade head`**，亦可手动：

```bash
alembic upgrade head
```

- **pytest（`SQLITE_PATH=:memory:`）**：仍使用 `Base.metadata.create_all`，与 Alembic 模型定义一致，**不跑** `alembic upgrade`（避免 CI/本地测试依赖磁盘上的迁移历史文件与修订顺序）。模型与迁移应保持一致；若改了模型，请同步生成 Alembic 修订并在文件库上 `upgrade head` 验证。
- **从旧版仅 `create_all` 升上来**：若启动报错「表已存在」，请**备份后删除** `slowtravel.db` 再启动，或在新环境重新生成库。

**为何两套路径？** 文件库需要可追溯的 schema 版本与索引变更（`alembic/versions/`）；测试用内存库追求快速、可重复、零副作用，用 `create_all` 直接对齐当前 ORM 定义即可。报告里可照此一句说明，避免被问「为什么既 Alembic 又 create_all」。

## 测试

```bash
pip install -r requirements.txt
pytest
```

**策略简述：** 核心 CRUD、鉴权与校验在 `tests/test_api.py`；参考数据与交通列表在 `tests/test_transport.py`；**加分/抛光** 场景在 `tests/test_polish.py`（分页越界 422、`naptan_access_node_id` 合法创建与非法外键 422、`/openapi.json` 中含 **apiKey** 安全声明、`/health` 含数据库连通字段）。运行前勿改 `API_KEY` 测试约定（见 `tests/conftest.py` 若存在）。

## 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查（`status` + `database`：能否对 SQLite 执行 `SELECT 1`） |
| GET | `/reference/literary-locations` | 文学/取景地（种子数据，可筛选） |
| GET | `/reference/dark-sky-sites` | 暗夜观星点（种子数据，可筛选） |
| GET | `/reference/naptan-access-nodes` | NaPTAN 访问点（需先 ETL 导入） |
| GET | `/reference/nptg-localities` | NPTG 地名（需先 ETL 导入） |
| POST | `/journeys` | 创建旅程及经停 |
| GET | `/journeys` | 旅程列表 |
| GET | `/journeys/{id}` | 旅程详情（含展开关联） |
| PATCH | `/journeys/{id}` | 更新旅程（可替换经停） |
| DELETE | `/journeys/{id}` | 删除旅程 |
| GET | `/journeys/{id}/summary` | 统计摘要 |
| GET | `/journeys/{id}/analytics` | 碳足迹、叙事、观星分析 |


## 技术说明

- 碳排放系数为简化常数（`app/services/analytics.py`），报告中应说明假设与可改进方向。
- 数据库结构由 **Alembic** 管理；初始修订见 `alembic/versions/3b772aadc5b9_initial_schema.py`（随模型变更可 `alembic revision --autogenerate` 生成新修订）。

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

- 交互式文档：<http://127.0.0.1:8000/docs>
- 本地数据库文件：默认 `slowtravel.db`（可在环境变量 `SQLITE_PATH` 中覆盖；测试使用 `SQLITE_PATH=:memory:`）

## 测试

```bash
pip install -r requirements.txt
pytest
```

## 主要端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 健康检查 |
| GET | `/reference/literary-locations` | 文学/取景地（种子数据，可筛选） |
| GET | `/reference/dark-sky-sites` | 暗夜观星点（种子数据，可筛选） |
| POST | `/journeys` | 创建旅程及经停 |
| GET | `/journeys` | 旅程列表 |
| GET | `/journeys/{id}` | 旅程详情（含展开关联） |
| PATCH | `/journeys/{id}` | 更新旅程（可替换经停） |
| DELETE | `/journeys/{id}` | 删除旅程 |
| GET | `/journeys/{id}/summary` | 统计摘要 |
| GET | `/journeys/{id}/analytics` | 碳足迹、叙事、观星分析 |


## 技术说明

- 碳排放系数为简化常数（`app/services/analytics.py`），报告中应说明假设与可改进方向。
- `alembic` 已列入依赖，如需迁移可在本地执行 `alembic init` 后与 `app.models` 对齐。

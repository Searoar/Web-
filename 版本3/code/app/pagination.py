"""统一分页查询参数（全站 list 端点一致）。

FastAPI 要求：`Annotated[..., Query(...)]` 内不要写 `Query(0)` 默认值，应在参数上写 `= 0`。
"""

from typing import Annotated

from fastapi import Query

MAX_PAGE_SIZE = 500
DEFAULT_PAGE_SIZE = 50

SkipQuery = Annotated[
    int,
    Query(ge=0, description="跳过条数（偏移量），从 0 开始"),
]

LimitQuery = Annotated[
    int,
    Query(
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"每页条数，最小 1，最大 {MAX_PAGE_SIZE}",
    ),
]

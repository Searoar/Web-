"""依赖注入：写操作需 API Key（Header: X-API-Key）。"""

from typing import Annotated

from fastapi import Header, HTTPException, status

from app.config import settings


def require_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> None:
    """
    当配置了 api_key（非空）时，校验请求头。
    读操作路由不使用本依赖；写操作（POST/PATCH/DELETE）使用。
    """
    expected = (settings.api_key or "").strip()
    if not expected:
        return
    if not x_api_key or x_api_key.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "unauthorized",
                    "message": "Invalid or missing API key. Send header X-API-Key.",
                }
            },
        )

"""依赖注入：写操作需 API Key（Header: X-API-Key），并在 OpenAPI 中声明为 apiKey 安全方案。"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(api_key: str | None = Security(api_key_header)) -> None:
    """
    当配置了 api_key（非空）时，校验请求头。
    读操作路由不使用本依赖；写操作（POST/PATCH/DELETE）使用。
    在 /docs 中点击 Authorize，输入 Key 即可带全站写请求。
    """
    expected = (settings.api_key or "").strip()
    if not expected:
        return
    if not api_key or api_key.strip() != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "unauthorized",
                    "message": "Invalid or missing API key. Send header X-API-Key or use Authorize in /docs.",
                }
            },
        )

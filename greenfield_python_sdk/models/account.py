from typing import Optional

from pydantic import BaseModel


class PaginationParams(BaseModel):
    key: Optional[bytes] = None
    limit: Optional[int] = None
    reverse: Optional[bool] = None

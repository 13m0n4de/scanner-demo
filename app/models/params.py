from typing import Optional

from pydantic import BaseModel, Field


class MasscanParams(BaseModel):
    target: str = Field(..., example="8.8.8.8", description="扫描目标")
    port_range: str = Field(..., example="1-65535", description="端口范围")
    rate: int = Field(10000, description="扫描速率")
    source_ip: Optional[str] = Field(None, description="源 IP 地址")


class HttpxParams(BaseModel):
    target: str = Field(..., description="扫描目标")
    port_range: str = Field(..., description="端口范围")


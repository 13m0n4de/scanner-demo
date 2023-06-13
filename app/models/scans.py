from pydantic import BaseModel, Field


class MasscanConfig(BaseModel):
    target: str = Field(..., description="扫描目标")
    port_range: str = Field(..., description="端口范围")
    rate: int = Field(10000, description="扫描速率")
    source_ip: str = Field(None, description="源 IP 地址")

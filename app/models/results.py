from typing import Optional, List

from pydantic import BaseModel, Field


class PortResult(BaseModel):
    port: int = Field(..., description="端口号")
    protocol: Optional[str] = Field(None, description="协议")
    service: Optional[str] = Field(None, description="服务")
    vulnerabilities: List[str] = Field([], description="存在的漏洞")


class ScanResult(BaseModel):
    ip: str = Field(..., description="IP")
    ports: List[PortResult] = Field([], description="端口列表")

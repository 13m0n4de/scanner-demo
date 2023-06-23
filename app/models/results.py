from enum import Enum
from typing import Optional, List

from pydantic import BaseModel, Field


class PortStatus(str, Enum):
    open = "open"
    closed = "closed"
    filtered = "filtered"


class PortDetail(BaseModel):
    port: int
    status: PortStatus
    protocol: Optional[str]
    ttl: Optional[int]


class PortScanResult(BaseModel):
    ip: str
    open_ports: List[int]
    closed_ports: List[int]
    filtered_ports: List[int]
    details: List[PortDetail]


class ServiceDetail(BaseModel):
    port: int
    name: Optional[str]
    version: Optional[str]
    banner: Optional[str]


class ServiceScanResult(BaseModel):
    ip: str
    services: List[ServiceDetail]

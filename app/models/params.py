from typing import Optional
from pydantic import BaseModel, Field, validator, root_validator

from app.utils import (
    validate_ip_address,
    validate_ip_network,
    validate_ip_list,
    validate_ip_range,
    validate_port_list,
    validate_port_range,
)


class MasscanParams(BaseModel):
    target: str = Field(..., example="8.8.8.8", description="扫描目标")
    ports: str = Field(..., example="1-65535", description="端口范围")
    rate: int = Field(10000, description="扫描速率")
    source_ip: Optional[str] = Field(None, description="源 IP 地址")

    @validator("target")
    def validate_target(cls, value):
        if (
            not validate_ip_address(value)
            and not validate_ip_network(value)
            and not validate_ip_range(value)
            and not validate_ip_list(value)
        ):
            raise ValueError("Invalid target format")

        return value

    @validator("ports")
    def validate_port_range(cls, value):
        if not validate_port_list(value) and not validate_port_range(value):
            raise ValueError("Invalid ports format")

        return value


class RustscanParams(BaseModel):
    addresses: str = Field(..., description="扫描目标")
    ports: Optional[str] = Field(None, description="端口")
    port_range: Optional[str] = Field(None, description="端口")
    batch_size: int = Field(4500, description="")

    @validator("addresses")
    def validate_addresses(cls, value):
        if (
            not validate_ip_address(value)
            and not validate_ip_network(value)
            and not validate_ip_range(value)
            and not validate_ip_list(value)
        ):
            raise ValueError("Invalid addresses format")

        return value

    @validator("ports")
    def validate_ports(cls, value):
        if value is not None and not validate_port_list(value):
            raise ValueError("Invalid ports format")
        return value

    @validator("port_range")
    def validate_range(cls, value):
        if value is not None and not validate_port_range(value):
            raise ValueError("invalid range format")
        return value

    @root_validator
    def check_ports_and_range(cls, values):
        ports = values.get("ports")
        port_range = values.get("port_range")
        if (ports and port_range) or (ports is None and port_range is None):
            raise ValueError("Only one of 'ports' or 'port_range' can be specified.")

        return values


class HttpxParams(BaseModel):
    target: str = Field(..., description="扫描目标")
    port_range: str = Field(..., description="端口范围")

from ipaddress import ip_address, ip_network


def validate_ip_address(ip: str) -> bool:
    try:
        ip_address(ip)
    except ValueError:
        return False
    else:
        return True


def validate_ip_network(network: str) -> bool:
    try:
        ip_network(network)
    except ValueError:
        return False
    else:
        return True


def validate_ip_range(ip_range: str) -> bool:
    start_ip, end_ip = ip_range.split("-")
    try:
        ip_address(start_ip.strip())
        ip_address(end_ip.strip())
    except ValueError:
        return False
    else:
        return True


def validate_ip_list(ip_list: str) -> bool:
    ips = ip_list.split(",")
    try:
        for ip in ips:
            ip_address(ip.strip())
    except ValueError:
        return False
    else:
        return True


def validate_port_list(port_list: str) -> bool:
    try:
        ports = map(int, port_list.split(","))
        return all(0 <= port <= 65535 for port in ports)
    except ValueError:
        return False


def validate_port_range(port_range: str) -> bool:
    try:
        start_port, end_port = map(int, port_range.split("-"))
    except (ValueError, AttributeError):
        return False
    else:
        if start_port > end_port:
            return False
        if start_port < 0 or end_port > 65535:
            return False

    return True

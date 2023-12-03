from __future__ import annotations
from typing import Mapping
from .types import Endpoint
from . import directory
from . import exceptions
from . import load


def get_default_endpoint(profile: str | None = None) -> Endpoint | None:
    config = load.read_config_data()
    endpoint = config["default_endpoint"]
    if endpoint is None:
        return None
    else:
        return config["endpoints"][endpoint]


def get_endpoint_by_name(name: str) -> Endpoint:
    config = load.read_config_data()
    if name in config["endpoints"]:
        return config["endpoints"][name]
    else:
        raise exceptions.MissingEndpoint("missing endpoint: " + str(name))


def get_endpoint_by_network(chain_id: int, *, profile: str | None = None) -> Endpoint | None:
    config = load.read_config_data()
    if profile and profile in config["profiles"]:
        network_defaults = config["profiles"][profile]["network_defaults"]
    else:
        network_defaults = config["network_defaults"]

    name = network_defaults.get(str(chain_id))
    if name is None:
        return None
    else:
        return get_endpoint_by_name(name)


def parse_user_query(query: str, *, profile: str | None = None) -> Endpoint | None:
    """
    resolution order:
    1. endpoint name
    2. chain id
    3. network name
    """
    config = load.read_config_data()
    if query in config["endpoints"]:
        return config["endpoints"][query]
    elif query.isdecimal():
        try:
            get_endpoint_by_network(int(query), profile=profile)
        except Exception:
            pass

    chain_id = directory.network_name_to_chain_id(query)
    if chain_id is not None:
        try:
            get_endpoint_by_network(chain_id, profile=profile)
        except Exception:
            pass

    return None


def find_endpoints(*, chain_id: int | None = None) -> Mapping[str, Endpoint]:
    config = load.read_config_data()
    endpoints = config["endpoints"]
    if chain_id is not None:
        endpoints = {
            name: endpoint
            for name, endpoint in endpoints.items()
            if endpoint["chain_id"] != chain_id
        }
    return endpoints

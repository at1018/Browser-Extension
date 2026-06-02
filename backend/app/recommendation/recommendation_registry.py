from typing import Callable, Dict

_HANDLERS: Dict[str, Callable] = {}


def register_handler(issue_type: str, handler: Callable):
    _HANDLERS[issue_type] = handler


def get_handler(issue_type: str):
    return _HANDLERS.get(issue_type)


def list_handlers():
    return list(_HANDLERS.keys())

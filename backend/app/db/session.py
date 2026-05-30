from typing import Generator


def get_db() -> Generator[None, None, None]:
    """Database session dependency placeholder."""
    yield None

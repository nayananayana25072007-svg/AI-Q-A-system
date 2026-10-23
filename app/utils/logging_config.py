"""Safe defaults for application logging."""

import logging


def configure_logging() -> None:
    """Configure standard application logging without recording user content."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

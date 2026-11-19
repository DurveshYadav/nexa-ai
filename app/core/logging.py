import logging
logger = logging.getLogger(__name__)

def setup_logging() -> None:
    """
    Configure basic application logging.
    """

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    
    
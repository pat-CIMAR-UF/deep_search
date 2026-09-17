import os
from dotenv import load_dotenv,find_dotenv
from typing import Tuple, Optional

_=load_dotenv(find_dotenv())
def _load_ragflow_env() ->Tuple[Optional[str], Optional[str]]:
    """Load RAGFlow environment variables."""
    return (
        os.getenv("RAGFLOW_API_KEY"),
        os.getenv("RAGFLOW_API_URL"),
    )

import logging
import os
from typing import Optional


def get_environment_variable(variable: str, default: Optional[str] = None, exception = False) -> str:
    """Read an environment variable. Raises errors if it is not defined or is empty.
    Parameters:
    ----------
        variable: str
            the name of the environment variable
        default: str (optional)
            the default value for the environment variable

    Returns:
    -------
        env_var: str
            the value of the environment variable
    """

    # Get the environment variable and return the value if anything assigned or the default value
    env_var = os.environ.get(variable, default)
    if env_var is None:
        logging.warning(f"{variable} or has no value assigned")
        if exception: raise KeyError( f"{variable} not defined or has no value assigned")

    return env_var

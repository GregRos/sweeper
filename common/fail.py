from __future__ import annotations

from logging import getLogger
from os import getenv, access, X_OK
from pathlib import Path
from typing import Any, NoReturn, Optional

logger = getLogger("sweeper")


class SweeperError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code} {message}")
        self.code = code


def insert_code(code: str, message: str):
    return f"{code} {message}"


def not_enough_info(message: str, error: bool):
    if error:
        raise SweeperError("LOW_INFO", message)
    else:
        logger.warning(insert_code("LOW_INFO", message))


def detector_mismatch(message: str, error: bool):
    err_code = "DETECTOR_MISMATCH"
    if error:
        raise SweeperError(err_code, message)
    else:
        logger.warning(insert_code(err_code, message))


def file_exists(what: Path, following_action: str | None):
    err_code = "FILE_EXISTS"
    if not following_action:
        raise SweeperError(err_code, f"Path '{what}' already exists.")
    else:
        logger.warning(
            insert_code(err_code, f"Path '{what}' already exists. {following_action}")
        )


def raise_bad_input(message: str) -> NoReturn:
    raise SweeperError("BAD_INPUT", message)


def get_input_dir(
    var_name: str, var_value: str | list[str] | None, can_create: bool = False
):
    def raise_err(text: str) -> NoReturn:
        raise_bad_input(f"Path input '{var_name}'='{var_value}' is bad, because {text}")

    match var_value:
        case str(x):
            final_value = x
        case list(xs):
            final_value = " ".join(xs)
        case _:
            raise_err("it's missing.")

    p = Path(final_value)
    if not p.exists():
        if can_create:
            p.mkdir()
        else:
            raise_err("it doesn't exist.")

    return p


def raise_bad_env(message: str):
    raise SweeperError("BAD_ENV", message)


def get_path_env(
    var_name: str,
    is_dir: Optional[bool] = None,
    can_create: bool = False,
    check_exe: bool = False,
    default: Optional[Path] = None,
) -> Path:
    def raise_err(rest: str) -> Any:
        raise_bad_env(f"Env variable '{var_name}' is bad: {rest}")

    value = getenv(var_name)
    if value is None:
        return Path(default) if default else raise_err("it's empty.")

    p = Path(value)

    if not p.exists():
        if is_dir is True and can_create:
            p.mkdir()
        else:
            raise_err("path doesn't exist.")

    if is_dir is True and not p.is_dir():
        raise_err("it's not a dir.")
    elif is_dir is False and p.is_dir():
        raise_err("it's not a file.")

    if check_exe and not access(p, X_OK):
        raise_err("it's not executable.")
    return p

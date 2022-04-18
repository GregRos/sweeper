import sys
from logging import getLogger
from os import getenv, access, X_OK
from pathlib import Path
from typing import NoReturn

from common import Torrent

logger = getLogger("sweeper")


class SweeperError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")


def insert_code(code: str, message: str):
    return f"!{code}! {message}"


class DetectionMismatch(Warning):
    def __init__(self, message: str):
        super().__init__(f"!DetectionMismatch! {message}")

    pass


class LowInfo(Warning):
    def __init__(self, message: str):
        super().__init__(f"!LowInfo! {message}")


def not_enough_info(message: str, error: bool):
    if error:
        raise SweeperError("LowInfo", message)
    else:
        logger.warning(
            message,
            exc_info=LowInfo(message)
        )


def detector_mismatch(message: str, error: bool):
    err_code = "DetectorMismatch"
    if error:
        raise SweeperError(err_code, message)
    else:
        logger.warning(
            message,
            exc_info=DetectionMismatch(message),
            stack_info=
        )


def invalid_input(var_name: str, expected: str):
    err_code = "InvalidInput"
    raise SweeperError(err_code, f"Bad input {var_name} - expected {expected}.")


def raise_bad_input(message: str):
    raise SweeperError("BadInput", message)


def get_input_dir(var_name: str, var_value: str, can_create=False):
    def raise_err(text: str):
        raise_bad_input(f"Input {var_name} is bad - {text}")

    if not var_name:
        raise_err("is missing")

    p = Path(var_value)
    if not p.exists():
        if can_create:
            p.mkdir()
        else:
            raise_err("doesn't exist")

    return p


def raise_bad_env(message: str):
    raise SweeperError("BadEnv", message)


def get_path_env(var_name: str, is_dir: bool = None, can_create: bool = False, check_exe=False):
    def raise_err(rest: str):
        raise_bad_env(f"Bad environment var {var_name} - {rest}")

    if not var_name:
        raise_err("is empty")
    value = getenv(var_name)
    if value is None:
        raise_err("missing")

    p = Path(value)

    if not p.exists():
        if is_dir is True and can_create:
            p.mkdir()
        else:
            raise_err("path does not exist")

    if is_dir is True and not p.is_dir():
        raise_err("must be a directory")
    elif is_dir is False and p.is_dir():
        raise_err("must be a file")

    if check_exe and not access(p, X_OK):
        raise_err("must be executable")
    return p

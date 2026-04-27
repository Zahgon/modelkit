import functools
import inspect
import os
import traceback
import types
from typing import Any, Callable, Optional, TypeVar, cast

import pydantic

PYDANTIC_ERROR_TRUNCATION = 20


class ModelsNotFound(Exception):
    pass


class PredictionError(Exception):
    def __init__(self, exc):
        self.exc = exc


class ModelkitDataValidationException(Exception):
    def __init__(
        self,
        model_identifier: str,
        pydantic_exc: Optional[pydantic.ValidationError] = None,
        error_str: str = "Data validation error in model",
    ):
        pydantic_exc_output = ""
        if pydantic_exc:
            exc_lines = str(pydantic_exc).split("\n")
            if len(exc_lines) > PYDANTIC_ERROR_TRUNCATION:
                pydantic_exc_output += "Pydantic error message "
                pydantic_exc_output += (
                    f"(truncated to {PYDANTIC_ERROR_TRUNCATION} lines):\n"
                )
                pydantic_exc_output += "\n".join(exc_lines[:PYDANTIC_ERROR_TRUNCATION])
                pydantic_exc_output += (
                    f"\n({len(exc_lines)-PYDANTIC_ERROR_TRUNCATION} lines truncated)"
                )
            else:
                pydantic_exc_output += "Pydantic error message:\n"
                pydantic_exc_output += str(pydantic_exc)

        super().__init__(f"{error_str} `{model_identifier}`.\n" + pydantic_exc_output)


class ValidationInitializationException(
    ModelkitDataValidationException
):  # pragma: no cover
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            error_str="Exception when setting up pydantic validation models",
            pydantic_exc=kwargs.pop("pydantic_exc"),
        )


class ReturnValueValidationException(ModelkitDataValidationException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            error_str="Return value validation error when calling model",
            pydantic_exc=kwargs.pop("pydantic_exc"),
        )


class ItemValidationException(ModelkitDataValidationException):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            error_str="Predict item validation error when calling model",
            pydantic_exc=kwargs.pop("pydantic_exc"),
        )


def is_modelkit_internal_frame(frame: types.FrameType):
    """
    Guess whether the frame originates from a submodule of `modelkit`
    """
    pass


def strip_modelkit_traceback_frames(exc: BaseException):
    """
    Walk the traceback and remove frames that originate from within modelkit
    Return an exception with the filtered traceback
    """
    pass


T = TypeVar("T", bound=Callable[..., Any])


# Decorators to wrap prediction methods to simplify tracebacks
def wrap_modelkit_exceptions(func: T) -> T:
    @functools.wraps(func)
    pass


def wrap_modelkit_exceptions_gen(func: T) -> T:
    @functools.wraps(func)
    pass


def wrap_modelkit_exceptions_async(func: T) -> T:
    @functools.wraps(func)
    pass


def wrap_modelkit_exceptions_gen_async(func: T) -> T:
    @functools.wraps(func)
    pass

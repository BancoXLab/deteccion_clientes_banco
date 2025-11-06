
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional
import pandas as pd

from scr.utils.log import Log


class Processor(ABC):
    """Base class for data processors.

    Usage: subclass and implement `process(self, df)` returning the processed DataFrame
    or result. Use `run(df)` to execute with standardized logging and error handling.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        raise_on_error: bool = False,
    ):
        self.name = name or self.__class__.__name__
        # crear logger sin sanitización específica
        self.log = Log(self.name)
        self.raise_on_error = raise_on_error

    def loggins(self, msg: str, **meta: Any) -> None:
        self.log.info(msg, **meta)

    @abstractmethod
    def process(self, df: pd.DataFrame) -> Any:
        """Implementar la lógica de procesamiento. Debe aceptar y devolver DataFrame u objeto."""

    def run(self, df: pd.DataFrame) -> Any:
        """Ejecuta `process` con manejo de errores y logging estándar."""
        try:
            self.loggins("start processing", rows=getattr(df, "shape", (None,))[0])
            result = self.process(df)
            return result
        except Exception as e:
            # el logger ya aplica sanitización antes de escribir
            self.log.error("processing error", fn=self.process.__name__, err=str(e))
            if self.raise_on_error:
                raise
            return None
        finally:
            try:
                self.loggins("end processing", rows=getattr(df, "shape", (None,))[0])
            except Exception:
                # no queremos que el logging final rompa la ejecución
                pass


class ETLProcessor(Processor):
    """Ejemplo de Processor que realiza validaciones básicas y limpieza ligera."""

    def __init__(self, *args, expected_columns: Optional[list] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.expected_columns = expected_columns or []

    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("ETLProcessor.process expects a pandas DataFrame")

        # Validaciones simples
        missing = [c for c in self.expected_columns if c not in df.columns]
        if missing:
            # registramos pero no rompemos por defecto
            self.log.warn("missing_expected_columns", missing=missing)

        # limpieza: eliminar duplicados
        n_before = len(df)
        df = df.drop_duplicates()
        n_after = len(df)
        if n_before != n_after:
            self.loggins("removed_duplicates", removed=n_before - n_after)

        return df

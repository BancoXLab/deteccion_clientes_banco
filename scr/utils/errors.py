import functools
from typing import Callable, Any
from scr.utils.log import Log


def handle_exceptions(default: Any = None, reraise: bool = False, sanitize_fn: Callable[[tuple, dict], dict] | None = None, logger_name: str = "errors"):
    """Decorator para capturar excepciones y loggearlas de forma centralizada.

    Parámetros:
    - default: valor a devolver si ocurre una excepción y no se re-lanza.
    - reraise: si True vuelve a lanzar la excepción (útil para tests o para que frameworks manejen el error).
    - sanitize_fn: función opcional que recibe (args, kwargs) y debe devolver un diccionario serializable
      con información ya anonimizada / segura para loggear.
    - logger_name: nombre del logger a instanciar.

    Ejemplo de sanitize_fn:
        def san(args, kwargs):
            return {"args": "<omitted>", "kwargs": "<omitted>"}
    """

    log = Log(logger_name)

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                try:
                    safe_meta = sanitize_fn(args, kwargs) if sanitize_fn else {}
                except Exception:
                    # si la sanitización falla, no evitar el log principal
                    safe_meta = {"sanitization_error": "failed"}

                # incluir siempre el nombre de la función y el mensaje de error
                meta = {"fn": fn.__name__, "err": str(e)}
                meta.update(safe_meta if isinstance(safe_meta, dict) else {"safe": str(safe_meta)})

                log.error("unhandled exception", exc_info=True, **meta)
                if reraise:
                    raise
                return default

        return wrapper

    return decorator
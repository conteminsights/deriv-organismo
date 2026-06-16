import importlib
import sys
import warnings

from starlette.exceptions import StarletteDeprecationWarning


def test_fastapi_testclient_import_does_not_emit_starlette_deprecation_warning():
    sys.modules.pop('fastapi.testclient', None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        importlib.import_module('fastapi.testclient')

    warning_types = [type(item.message) for item in caught]
    assert StarletteDeprecationWarning not in warning_types

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Importa os modelos no carregamento do módulo para registrar as tabelas no metadata.
# noqa: F401
from deriv_organismo.db import models as _models

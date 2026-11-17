from datetime import datetime, timezone
from zoneinfo import ZoneInfo

FUSO = ZoneInfo("America/Sao_Paulo")


def agora():
    return datetime.now(timezone.utc)


def hoje_local():
    return datetime.now(FUSO).date()


def como_utc(valor):
    """O SQLite devolve datas sem fuso; elas foram gravadas em UTC."""
    if valor is not None and valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor

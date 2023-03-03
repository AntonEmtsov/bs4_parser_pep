class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ListVersionsNotFound(Exception):
    """Вызывается, когда парсер не может найти список с версиями."""
    pass

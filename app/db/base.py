from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    All database models will inherit from this class.
    It provides the link between Python classes and Postgres tables.
    """
    pass
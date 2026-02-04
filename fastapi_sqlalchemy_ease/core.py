from sqlalchemy import (
    create_engine,
    Column, Integer, String, Text, Float, Boolean, 
    Date, DateTime, Time,
    JSON, LargeBinary, 
    Numeric,
    ForeignKey,
    UniqueConstraint, CheckConstraint,
    Index, Table,
    func, and_, any_, not_, or_, select, update, delete, desc, asc
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from typing import Generator, Optional
from .exceptions import DatabaseNotInitializedError


class SQLAlchemy:
    # Singleton - ensures only one instance exists in the app
    _instance = None

    # All sqlalchemy types as class attributes
    '''Data types'''
    Column = Column
    String = String
    Integer = Integer
    Float = Float
    Boolean = Boolean
    Text = Text
    Date = Date
    DateTime = DateTime
    Time = Time
    JSON = JSON
    LargeBinary = LargeBinary
    Numeric = Numeric

    '''Logic and Boolean operators'''
    and_ = and_
    or_ = or_
    not_ = not_

    '''SQL Functions (count, now, max, min, etc.)'''
    func = func

    '''Query Execution Utilities'''
    select = select
    update = update
    delete = delete

    '''ordering'''
    desc = desc
    asc = asc


    '''Relationships and Constraints'''
    ForeignKey = ForeignKey
    UniqueConstraint = UniqueConstraint
    CheckConstraint = CheckConstraint
    Index = Index
    Table = Table
    
    # prevents binding issues
    @staticmethod
    def relationship(*args, **kwargs):
        """
        Creates a relationship between two models.
        This is a wrapper around SQLAlchemy's relationship function.
        """
        return relationship(*args, **kwargs)


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._Model = declarative_base()
        return cls._instance
    

    def __init__(self):
        if not hasattr(self, '_initialized_vars'):
            # Everything starts as None Until db.init_app() is called
            self.engine = None
            self._SessionLocal = None
            self.session = None 
            self._initialized = False
            self._initialized_vars = True


    def init_app(self, DATABASE_URI: str, **kwargs):
        '''
        Docstring for init_app
        
        used to Initialized database.

        DATABASE_URI: database url, type : string
        connect_args: used only when initializing sqlite db
        '''

        engine_kwargs={
            "pool_pre_ping": True,
        }

        # Only add pooling if NOT using SQLite
        if not DATABASE_URI.startswith("sqlite"):
            engine_kwargs["pool_size"] = kwargs.get("pool_size", 10)
            engine_kwargs["max_overflow"] = kwargs.get("max_overflow", 20)

        engine_kwargs.update(kwargs)

        # Engine connection to database
        self.engine = create_engine(DATABASE_URI, **engine_kwargs)

        # SessionLocal - Factory data creates new sessions
        self._SessionLocal = sessionmaker(autoflush=False ,bind=self.engine)

        from sqlalchemy.orm import scoped_session
        self.session = scoped_session(self._SessionLocal)
        self._Model.query = self.session.query_property()

        self._initialized = True


    @property
    def Model(self):
        '''
        Docstring for Model
        
        Base class for creating database models
        User writes: class User(db.Model):
        '''
        
        return self._Model
    

    def create_all(self):
        '''
        Docstring for create_all
        
        create all tables in the database
        '''

        if not self._initialized:
            raise DatabaseNotInitializedError('Database not Intialized, call db.init_app() first.')
        
        self._Model.metadata.create_all(self.engine)


    def drop_all(self):
        '''
        Docstring for drop_all
        
        delete all tables from the database.
        '''
        if not self._initialized:
            raise DatabaseNotInitializedError('Database not Intialized, call db.init_app() first.')

        self._Model.metadata.drop_all(self.engine)


    def Session(self) -> Generator[Session, None, None]:
        '''
        Docstring for Session
        
        creates a new session per request.
        must use with Depends in FastAPI().
        Auto closes sessions after request is done.

        '''

        if not self._initialized:
            raise DatabaseNotInitializedError('Database not Intialized, call db.init_app() first.')
            
        session = self.session()
        try:
            yield session # Give session to the route
        finally:
            self.session.remove() #proper cleanup for scoped sessions
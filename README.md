# fastapi-sqlalchemy-ease  
  
fastapi-sqlalchemy-ease is a singleton-based SQLAlchemy extension for FastAPI. It provides a centralized interface for database initialization, model declaration, and session management, inspired by the simplicity of Flask-SQLAlchemy.  
  
## ◽ Key Features  
  
- Singleton Design: Ensures a single database instance across your entire FastAPI application.  
  
- Consolidated API: Access all SQLAlchemy types (Integer, String, ForeignKey, etc.) directly from the db object.  
  
- Auto-Cleanup: Includes a generator-based session handler designed for FastAPI's Depends to ensure sessions are always closed.  
  
- Built-in Lifecycle Management: Simple methods for create_all() and drop_all().  
  
  
## ◽ Installation  
  
pip install fastapi-sqlalchemy-ease  
  


## ◽ Usage Guide  
  
### 1. Basic setup  
Initialize your database instance in a centralized file (e.g. database.py).  
  

    from fastapi_sqlalchemy_ease import SQLAlchemy  

    '''Create the singleton instance''' 
    db = SQLAlchemy()  

    '''Initialize with your URI'''  
    DATABASE_URI = "sqlite:///./test.db"  

    '''Use connect_args={"check_same_thread": False} for SQLite'''  
    db.init_app(DATABASE_URI, connect_args={"check_same_thread": False})  
  
  
  
### 2. Defining Models  
No need to import types from SQLAlchemy; use the db instance directly.  
  
    class User(db.Model):  
        __tablename__ = "users"  

        id = db.Column(db.Integer, primary_key=True)  
        username = db.Column(db.String, unique=True, nullable=False)  
        created_at = db.Column(db.DateTime, default_server=db.func.now())  
  
  
  
### 3. Creating Tables  
You can trigger table creation easily.  
  
    db.create_all()  
  
  
  
### 3. Database Operations in Routes  
The extension provides a thread-safe db.Session for FastAPI dependencies and a Flask-like query property on models.  
  
    from fastapi import FastAPI, Depends  
    from .. import db  

    app = FastAPI()  
    
    # Best for Reads
    @app.get("/users")
    def get_users():
        return User.query.all()

    # Best for Writes (Auto-cleanup)
    @app.post("/users")
    def create_user(user_data: UserSchema, session=Depends(db.Session)):
        user = User(**user_data.dict())
        session.add(user)
        session.commit()
        return user  
  
  
  
## ◽ Available Attributes  
Your db instance provides easy access to standard SQLAlchemy types and constraints:  
  
Category - Available Attributes  

Data Types	-  String, Integer, Float, Boolean, Text, Date, DateTime, JSON, Numeric  
Constraints	- ForeignKey, UniqueConstraint, CheckConstraint, Index  
ORM	- relationship, Table, Column  
Logic and Boolean operators = and_, or_, not_  
SQL Functions (count, now, max, min, etc.) = func  
Query Execution Utilities = select, update, delete
ordering = desc, asc
  
  
## ◽ Error Handling
The library includes a DatabaseNotInitializedError. If you attempt to access db.Model, db.Session, or lifecycle methods before calling db.init_app(), a clear exception will be raised to help you debug quickly.  
  

  
## 📄 License
Distributed under the MIT License.  

--
# Crud simples com FastAPI e Sqlalchemy

## database.py
Creates a `sqlite` database instance
with an `engine` from the orm to manage the connection pool,
a `sessionmaker` to use those connections from the engine.
A `Base` class that inherits `DeclarativeBase` to manage the tables and metadata
and a `get_db` helper function to handle the db dependency

## models.py 
Creates the `users` table schema with the `User` class inheriting from `database.Base`
types and columns are mapped with `Mapped[type]` and `mapped_column()`
> Still needs migrations ans more entities and relationships

## schemas.py 
Stores the Entities for the crud operations like `CreateUser` and `UserResponse`.
This `model_config = ConfigDict(from_attributes=True)` it is used to create the response object, without it this would be needed:
```python
UserResponse(**{"id": 1, "name": "x", "email": "y"})
```

## main.py
Contains the handlers, the FastAPI app and a async context manager to create all the tables needed before the app starts and close the connection
after the app stops.
`SessionDep` is used o inject the db dependency on the handlers so it can use the session to make queries,
is `Annotated` because the docs recommended for better dx with IDEs and linters.
`response_model` is used by Fastapi to serialize the response
`->` is used by the handler as the actual response type, but FastAPI uses the other one
```python
@app.get("/users/{id}", response_model=UserResponse)  # ← FastAPI serializes to THIS
def read_user(user_id: int, db: SessionDep) -> User:  # ← type checker checks THIS
    return db.get(User, user_id)   
```

### ORM methods
- `db.get(select(Table)).scalars().all()` returns all the rows from a table
- `db.add()` inserts a new entity
- `db.get(Table, id)` gets the object, if exits
- `db.delete(object)` deletes from the table
- `db.commit()` applies the changes, add or delete don`t touch the db unless this is called
- `db.refresh(object)` updates the local session with the recent object and the db state 
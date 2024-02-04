from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from models import User, engine, Token, Category, Task, TaskIn, TaskInModify

SECRET_KEY = "fa4b5297f69d0096b2a11eddc84cae023fddceb919b8a828c9c9639529edc216"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = timedelta(hours=1)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/usuarios/iniciar-sesion")
app = FastAPI()


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    credentials_exception = HTTPException(status_code=401, detail="Usuario o contraseña incorrectas")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        user = session.exec(statement).one_or_none()
    if user is None:
        raise credentials_exception
    return user


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/usuarios")
def create_user(name: str, password: str):
    """ Crea un nuevo usuario para la aplicación"""
    key = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = User(username=name, password=key.decode())
    with Session(engine) as session:
        session.add(user)
        session.commit()
    return "ok"


@app.post("/usuarios/iniciar-sesion")
def start_session(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    with Session(engine) as session:
        statement = select(User).where(User.username == form_data.username)
        user = session.exec(statement).one_or_none()

    if user is None or not bcrypt.checkpw(form_data.password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Usuario erróneo")

    access_token = create_access_token({"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@app.post("/categorias")
def create_category(name: str, description: str = None) -> Category:
    """ Crea una categoría"""
    category = Category(name=name, description=description)
    try:
        with Session(engine) as session:
            session.add(category)
            session.commit()
            session.refresh(category)
            return category
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La categoría ya existe")


@app.delete("/categorias/{id}")
def delete_category(id: int):
    """ Elimina una categoría"""
    with Session(engine) as session:
        category = session.get(Category, id)
        session.delete(category)
        session.commit()

    return "Categoría eliminada"


@app.get("/categorias", response_model=list[Category])
def get_category():
    """ Obtiene una lista de las categorías """
    with Session(engine) as session:
        return session.exec(select(Category)).all()


@app.post("/tareas")
def create_task(task: TaskIn = Depends()) -> Task:
    """ Crea una tarea"""
    with Session(engine) as session:
        task = Task(**task.dict())
        session.add(task)
        session.commit()
        session.refresh(task)
        return task


@app.put("/tareas/{id}")
def update_task(id: int, task_update: TaskInModify = Depends()):
    """Actualiza una tarea"""
    with Session(engine) as session:
        task = session.get(Task, id)
        for k, v in task_update.dict(exclude_unset=True).items():
            setattr(task, k, v)

        session.add(task)
        session.commit()
    return "Tarea actualizada"


@app.delete("/tareas/{id}")
def delete_task(id: int):
    """Elimina una tarea"""
    with Session(engine) as session:
        task = session.get(Task, id)
        session.delete(task)
        session.commit()
    return "Tarea eliminada"


@app.get("/tareas", response_model=list[Task])
def get_tasks():
    """Obtiene las tareas del usuario activo"""
    with Session(engine) as session:
        return session.exec(select(Task)).all()


# start_session("yachay", "password")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, )

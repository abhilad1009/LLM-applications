from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from jose import JWTError, jwt
from datetime import datetime, timedelta
import httpx
import databases

DATABASE_URL = "postgresql://username:password@localhost/dbname"
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

database = databases.Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ChatData(Base):
    __tablename__ = "chat_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    prompt = Column(String)
    generated_data = Column(String)
    created_at = Column(DateTime, server_default=text("(now() at time zone 'utc')"))

Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get the current user from the token
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token")
async def login_for_access_token(username: str, password: str):
    # If valid, create and return an access token
    user = None  
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/generate_data")
async def generate_data(prompt: str, current_user: User = Depends(get_current_user)):
    # Call OpenAI ChatGPT to generate data
    openai_api_key = "your-openai-api-key"
    openai_endpoint = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {"Authorization": f"Bearer {openai_api_key}"}
    data = {"prompt": prompt, "max_tokens": 100}

    async with httpx.AsyncClient() as client:
        response = await client.post(openai_endpoint, json=data, headers=headers)
        generated_data = response.json()["choices"][0]["text"]

    # Process the generated data 
    processed_data = generated_data.upper()

    # Store data in PostgreSQL database
    async with database.transaction():
        db = SessionLocal()
        chat_data = ChatData(user_id=current_user.id, prompt=prompt, generated_data=processed_data)
        db.add(chat_data)
        db.commit()

    return {"message": "Data generated and stored successfully"}
from multiprocessing import synchronize
import re
import time
from turtle import pos
from fastapi import FastAPI, Response,status,HTTPException,Depends

from fastapi.params import Body
from typing import Optional, List
from sqlalchemy.orm import Session
import psycopg
from psycopg.rows import dict_row
from . import models,schemas,utilts
from . database import engine, get_db
from .routers import post, user




models.Base.metadata.create_all(bind=engine) #this will create the tables in the database if they do not exist


app = FastAPI()





while True:
    try:
        conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='password123', port=5432,row_factory=dict_row)
        cursor = conn.cursor()
        print("Database connection was successful")
        break
    except Exception as error:
        print("Database connection failed")
        print("Error:", error)
        time.sleep(2) #wait for 2 seconds before trying again


my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        

def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
        
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return { "data": posts}


app.include_router(post.router)
app.include_router(user.router)




@app.get("/")
#async is optional we can use it to make the function asynchronous, which is useful for I/O-bound operations. 
# or skip it and use def root():
async def root():
    return {"message": "welcome to FastAPI!"}






import re
import time
from fastapi import FastAPI, Response,status,HTTPException,Depends
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import psycopg
from psycopg.rows import dict_row
from . import models
from . database import engine, get_db

models.Base.metadata.create_all(bind=engine) #this will create the tables in the database if they do not exist


app = FastAPI()




class Post(BaseModel):
    title: str
    content: str
    published: bool = True  #optional, default value is True
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
        
@app.get("/")
#async is optional we can use it to make the function asynchronous, which is useful for I/O-bound operations. 
# or skip it and use def root():
async def root():
    return {"message": "welcome to FastAPI!"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    return {"status": "success"}




@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""")
    posts =cursor.fetchall()
    return {"data": posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)


def create_posts(post: Post):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}
    
@app.get("/posts/{id}")

def get_post(id: int):
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))# a tuple containing one string extra comma is needed to make it a tuple
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}




@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)


def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")


def update_post(id: int, post: Post):
    
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
                   (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    
    return {"data": updated_post}
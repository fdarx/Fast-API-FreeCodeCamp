from multiprocessing import synchronize
import re
import time
from turtle import pos
from fastapi import FastAPI, Response,status,HTTPException,Depends
from fastapi.params import Body
from typing import Optional
from sqlalchemy.orm import Session
import psycopg
from psycopg.rows import dict_row
from . import models,schemas
from . database import engine, get_db

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
        
@app.get("/")
#async is optional we can use it to make the function asynchronous, which is useful for I/O-bound operations. 
# or skip it and use def root():
async def root():
    return {"message": "welcome to FastAPI!"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return { "data": posts}




@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts""")
    # posts =cursor.fetchall()
    posts = db.query(models.Post).all()
    return {"data": posts}

@app.post("/posts",status_code=status.HTTP_201_CREATED)

def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):

    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *""",
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dump()) #**post.dict() unpacks the dictionary into keyword arguments for the Post model
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return {"data": new_post}
    
@app.get("/posts/{id}")

def get_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))# a tuple containing one string extra comma is needed to make it a tuple
    # post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first() 
    # .first instead of .all() to get the first result or None if no result is found and save resources by not fetching all results when we only need one
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}




@app.delete("/posts/{id}",status_code=status.HTTP_204_NO_CONTENT)


def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    post.delete(asynchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")


def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    updated_post = post_query.first()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"post with id: {id} does not exist")
    post_query.update(post.dump(), synchronize_session=False)
    db.commit()

    return {"data": post.first()}
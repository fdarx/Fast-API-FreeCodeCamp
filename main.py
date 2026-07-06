from fastapi import FastAPI


app = FastAPI()

#async is optional we can use it to make the function asynchronous, which is useful for I/O-bound operations. 
# or skip it and use def root():
@app.get("/")
async def root():
    return {"message": "Hello World"}

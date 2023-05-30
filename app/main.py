# to start the server we use the uvicorn main:app command
from fastapi import FastAPI
import models
import database
from routers import posts, users, auth, vote
from config import settings
#from fastapi import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

models.database.Base.metadata.create_all(bind=database.engine)

origins = [
    "*",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# to make our router objects work in the other files, we must extend the functionality of the app object by using the .include_router function
app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
async def root():
    #return {"message": "welcome to our landing page"}
    return FileResponse("htmlPages/landingPage.html")


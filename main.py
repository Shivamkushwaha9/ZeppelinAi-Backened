from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Query
from fastapi.responses import JSONResponse
app = FastAPI()
from passlib.context import CryptContext
from pymongo import MongoClient, errors
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.candidate import CandidateModel,ChangePasswordModel, CandidateLoginModel, CandidateUpdateModel
from models.job import Job, PaginatedResponse
from datetime import datetime, timedelta
from models.token import *
from src.registration.token_generation import *
from typing import Optional
import gridfs
from bson import ObjectId
from fastapi.responses import StreamingResponse


fs = gridfs.GridFS(db)
client = MongoClient("mongodb+srv://subodh:root@sub-cluster.wo2nvbg.mongodb.net/")
db = client["startup-init"]
collection = db["auth"]
job_collection = db["jobs"]
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
@app.get("/")
def hc():
    return JSONResponse({
        "message": "Auth service is up and running!"
    })

@app.post("/signup")
async def signup(user: CandidateModel):
    # Check if the email or username already exists
    if collection.find_one({"$or": [{"email": user.email}, {"username": user.username}]}):
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    hashed_password = pwd_context.hash(user.password)
    
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    result = collection.insert_one(user_dict)
    
    return JSONResponse(
        {
            "id": str(result.inserted_id), 
            "message": "User created successfully"
        })

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = collection.find_one({"username": form_data.username})
    if not user or not pwd_context.verify(form_data.password, user["password"]):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/change-password")
async def change_password(user: ChangePasswordModel, username: str = Depends(oauth2_scheme)):
    db_user = collection.find_one({"username": username})
    
    if not db_user or not pwd_context.verify(user.current_password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid current password")
    
    new_hashed_password = pwd_context.hash(user.new_password)
    
    collection.update_one({"_id": db_user["_id"]}, {"$set": {"password": new_hashed_password}})
    
    return {"message": "Password updated successfully"}

# localhost:8000/jobs?page=1&size=100
# localhost:8000/jobs?page=1&size=10&location=Work from home
@app.get("/jobs", response_model=PaginatedResponse)
async def get_jobs(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    location: Optional[str] = None,
    min_stipend: Optional[str] = None,
    max_stipend: Optional[str] = None,
    job_type: Optional[str] = None,
):
    try:
        filters = {}
        if location:
            filters["location"] = location
        if min_stipend:
            filters["stipend"] = {"$gte": min_stipend}
        if max_stipend:
            filters.setdefault("stipend", {}).update({"$lte": max_stipend})
        if job_type:
            filters["job_type"] = job_type

        total_jobs = job_collection.count_documents(filters)
        jobs_cursor = job_collection.find(filters).skip((page - 1) * size).limit(size)
        jobs = list(jobs_cursor)

        response = PaginatedResponse(
            jobs=[Job(**job) for job in jobs],
            total=total_jobs,
            page=page,
            size=size
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    try:
        file_id = fs.put(file.file, filename=file.filename, content_type=file.content_type)
        collection.update_one({"_id": current_user["_id"]}, {"$set": {"photo": str(file_id)}})
        return {"message": "Photo uploaded successfully", "file_id": str(file_id)}
    except errors.PyMongoError as e:
        raise HTTPException(status_code=500, detail="Photo upload failed")

@app.put("/update-profile")
async def update_profile(user: CandidateUpdateModel, current_user: dict = Depends(get_current_user)):
    update_data = user.dict(exclude_unset=True)
    collection.update_one({"_id": current_user["_id"]}, {"$set": update_data})
    return {"message": "Profile updated successfully"}

@app.get("/photo/{photo_id}")
async def get_photo(photo_id: str):
    try:
        photo = fs.get(ObjectId(photo_id))
        return StreamingResponse(photo, media_type=photo.content_type)
    except gridfs.errors.NoFile:
        raise HTTPException(status_code=404, detail="Photo not found")
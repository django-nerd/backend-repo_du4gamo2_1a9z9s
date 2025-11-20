import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Track, Release, Artist

app = FastAPI(title="AURCA SOUND API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "AURCA SOUND Backend Running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            collections = db.list_collection_names()
            response["collections"] = collections[:10]
        else:
            response["database"] = "❌ Not Available"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# -------- Artist Music Management (3.2) --------

class TrackCreate(Track):
    pass

class TrackOut(Track):
    id: str

class ReleaseCreate(Release):
    pass

class ReleaseOut(Release):
    id: str


def _oid(obj_id: str) -> ObjectId:
    try:
        return ObjectId(obj_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId")


@app.post("/api/artists/{artist_id}/tracks", response_model=TrackOut)
def create_track(artist_id: str, payload: TrackCreate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    data = payload.model_dump()
    data["artist_id"] = artist_id
    inserted_id = create_document("track", data)
    doc = db["track"].find_one({"_id": ObjectId(inserted_id)})
    doc["id"] = str(doc.pop("_id"))
    return TrackOut(**doc)


@app.get("/api/artists/{artist_id}/tracks", response_model=List[TrackOut])
def list_tracks(artist_id: str, status: Optional[str] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    query = {"artist_id": artist_id}
    if status:
        query["status"] = status
    rows = get_documents("track", query, limit)
    out = []
    for r in rows:
        r["id"] = str(r.pop("_id"))
        out.append(TrackOut(**r))
    return out


@app.post("/api/artists/{artist_id}/releases", response_model=ReleaseOut)
def create_release(artist_id: str, payload: ReleaseCreate):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    data = payload.model_dump()
    data["artist_id"] = artist_id
    inserted_id = create_document("release", data)
    doc = db["release"].find_one({"_id": ObjectId(inserted_id)})
    doc["id"] = str(doc.pop("_id"))
    return ReleaseOut(**doc)


@app.get("/api/artists/{artist_id}/releases", response_model=List[ReleaseOut])
def list_releases(artist_id: str, status: Optional[str] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    query = {"artist_id": artist_id}
    if status:
        query["status"] = status
    rows = get_documents("release", query, limit)
    out = []
    for r in rows:
        r["id"] = str(r.pop("_id"))
        out.append(ReleaseOut(**r))
    return out


# Minimal schema explorer for frontend to align with database viewer
class SchemaItem(BaseModel):
    name: str

@app.get("/schema", response_model=List[SchemaItem])
def get_schema():
    # Expose defined collections to the UI or admin tools
    return [
        {"name": "artist"},
        {"name": "track"},
        {"name": "release"},
    ]


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

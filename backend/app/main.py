from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid

app = FastAPI(title="Monte Carlo API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChartPosition(BaseModel):
    chartType: str
    xValue: Optional[float] = None
    yValue: Optional[float] = None
    dataIndex: Optional[int] = None
    pixelX: Optional[int] = None
    pixelY: Optional[int] = None


class AnnotationBase(BaseModel):
    content: str
    author: str
    scenarioId: str
    position: Optional[ChartPosition] = None


class Annotation(AnnotationBase):
    id: str
    createdAt: str
    updatedAt: str
    resolved: bool = False


class AnnotationUpdate(BaseModel):
    content: Optional[str] = None
    resolved: Optional[bool] = None


annotations_db: List[Annotation] = []


@app.get("/")
def root():
    return {"service": "Monte Carlo API", "status": "running"}


@app.post("/api/annotations", response_model=Annotation)
def create_annotation(ann: AnnotationBase):
    now = datetime.now().isoformat()
    new_ann = Annotation(
        id=str(uuid.uuid4()),
        content=ann.content,
        author=ann.author,
        scenarioId=ann.scenarioId,
        position=ann.position,
        createdAt=now,
        updatedAt=now
    )
    annotations_db.append(new_ann)
    return new_ann


@app.get("/api/annotations", response_model=List[Annotation])
def list_annotations(scenarioId: Optional[str] = None):
    if scenarioId:
        return [a for a in annotations_db if a.scenarioId == scenarioId]
    return annotations_db


@app.get("/api/annotations/{ann_id}", response_model=Annotation)
def get_annotation(ann_id: str):
    for a in annotations_db:
        if a.id == ann_id:
            return a
    raise HTTPException(status_code=404, detail="Annotation not found")


@app.put("/api/annotations/{ann_id}", response_model=Annotation)
def update_annotation(ann_id: str, update: AnnotationUpdate):
    for i, a in enumerate(annotations_db):
        if a.id == ann_id:
            if update.content is not None:
                annotations_db[i].content = update.content
            if update.resolved is not None:
                annotations_db[i].resolved = update.resolved
            annotations_db[i].updatedAt = datetime.now().isoformat()
            return annotations_db[i]
    raise HTTPException(status_code=404, detail="Annotation not found")


@app.delete("/api/annotations/{ann_id}")
def delete_annotation(ann_id: str):
    for i, a in enumerate(annotations_db):
        if a.id == ann_id:
            del annotations_db[i]
            return {"success": True}
    raise HTTPException(status_code=404, detail="Annotation not found")

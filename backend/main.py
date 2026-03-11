# backend/main.py
import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import init_db, get_db
from models import Meeting, Task
from stt_service import stt_service
from agent_service import agent_service
from notion_service import notion_service

app = FastAPI(title="AI Meeting Agent")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_db()
    if not os.path.exists("temp_audio"):
        os.makedirs("temp_audio")

@app.post("/upload")
async def upload_audio(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. 파일 임시 저장
    file_id = str(uuid.uuid4())
    ext = file.filename.split(".")[-1]
    temp_path = f"temp_audio/{file_id}.{ext}"
    
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 2. STT 변환
        raw_text = stt_service.transcribe(temp_path)
        
        # 3. DB 원문 저장
        meeting = Meeting(title=file.filename, raw_text=raw_text)
        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        # 4. 업무 추출 (LLM)
        extracted_tasks = await agent_service.extract_tasks(raw_text)
        
        # 5. Notion 등록
        results = []
        for t in extracted_tasks:
            title = t.get("title", "Unknown Task")
            assignee = t.get("assignee", "None")
            deadline = t.get("deadline", "None")
            
            notion_id = await notion_service.create_kanban_card(
                title=title,
                status="시작 전",
                assignee=assignee,
                deadline=deadline
            )
            
            # 태스크 정보 DB 기록 (옵션)
            db_task = Task(
                meeting_id=meeting.id,
                title=title,
                assignee=assignee,
                deadline=deadline,
                notion_page_id=notion_id
            )
            db.add(db_task)
            results.append({
                "title": title,
                "assignee": assignee,
                "deadline": deadline,
                "notion_id": notion_id
            })
        
        db.commit()

        return {
            "success": True,
            "meeting_id": meeting.id,
            "raw_text": raw_text,
            "tasks": results
        }

    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/meetings")
def get_meetings(db: Session = Depends(get_db)):
    """저장된 회의록 목록을 최신순으로 반환"""
    meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "raw_text": m.raw_text,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in meetings
    ]

@app.post("/analyze")
async def analyze_text(
    payload: dict,
    db: Session = Depends(get_db)
):
    """STT 없이 텍스트를 바로 분석하여 Notion 등록"""
    raw_text = payload.get("text", "").strip()
    meeting_id = payload.get("meeting_id")
    if not raw_text:
        return {"success": False, "error": "텍스트가 비어 있습니다."}

    # LLM 업무 추출
    extracted_tasks = await agent_service.extract_tasks(raw_text)

    results = []
    for t in extracted_tasks:
        title = t.get("title", "Unknown Task")
        content = t.get("content", "")
        assignee = t.get("assignee", "None")
        deadline = t.get("deadline", "None")

        notion_id = await notion_service.create_kanban_card(
            title=title,
            status="시작 전",
            assignee=assignee,
            deadline=deadline,
            content=content
        )

        if meeting_id:
            db_task = Task(
                meeting_id=meeting_id,
                title=title,
                assignee=assignee,
                deadline=deadline,
                notion_page_id=notion_id
            )
            db.add(db_task)

        results.append({
            "title": title,
            "assignee": assignee,
            "deadline": deadline,
            "notion_id": notion_id
        })

    db.commit()
    return {"success": True, "tasks": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

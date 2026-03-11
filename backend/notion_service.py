# backend/notion_service.py
import os
import re
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

class NotionService:
    def __init__(self):
        self.notion = AsyncClient(auth=os.getenv("NOTION_API_KEY"))
        self.database_id = os.getenv("NOTION_DB_ID")
        print(f"DEBUG: Using Database ID -> {self.database_id}") # 이 출력값이 로그의 ID와 일치하는지 확인

    async def create_kanban_card(self, title: str, status: str, assignee: str, deadline: str):
        """
        노션 칸반 보드 형식:
        이름 : 기본속성 (title)
        상태 : 시작 전 / 진행 중 / 완료 (select)
        담당자 : text (rich_text)
        마감일 : date (date)
        """
        properties = {
            "이름": {"title": [{"text": {"content": title}}]},
            "상태": {"select": {"name": status}},
            "담당자": {"rich_text": [{"text": {"content": assignee if assignee != "None" else ""}}]}
        }

        # ISO 8601 형식(YYYY-MM-DD)인 경우에만 마감일 설정
        # LLM이 "내일", "다음 주" 같은 자연어를 반환하면 무시
        if deadline and deadline != "None":
            if re.match(r"^\d{4}-\d{2}-\d{2}$", deadline.strip()):
                properties["마감일"] = {"date": {"start": deadline.strip()}}

        response = await self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
        return response.get("id")

notion_service = NotionService()

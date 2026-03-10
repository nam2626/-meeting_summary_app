# backend/notion_service.py
import os
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

class NotionService:
    def __init__(self):
        self.notion = Client(auth=os.getenv("NOTION_API_KEY"))
        self.database_id = os.getenv("NOTION_DB_ID")

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
            "담당자": {"rich_text": [{"text": {"content": assignee}}]}
        }
        
        if deadline and deadline != "None":
            # Simple date validation/formatting might be needed depending on LLM output
            properties["마감일"] = {"date": {"start": deadline}}

        response = self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties
        )
        return response.get("id")

notion_service = NotionService()

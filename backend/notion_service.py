# backend/notion_service.py
import os
import re
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv(override=True)

class NotionService:
    def __init__(self):
        api_key = os.getenv("NOTION_API_KEY")
        self.notion = AsyncClient(auth=api_key)
        self.database_id = os.getenv("NOTION_DB_ID")
        masked = f"{api_key[:10]}...{api_key[-5:]}" if api_key else "None"
        print(f"DEBUG: NOTION_API_KEY -> {masked}")
        print(f"DEBUG: NOTION_DB_ID   -> {self.database_id}")

    async def create_kanban_card(self, title: str, status: str, assignee: str, deadline: str, content: str = ""):
        """
        NEW_KANBAN DB 속성에 직접 매핑 + 본문에 상세 내용 추가:
        - 이름   : title
        - 담당자 : rich_text
        - 날짜   : date
        - 태그   : multi_select (상태 저장)
        - 본문   : 상세 내용(content)
        """
        properties = {
            "이름": {"title": [{"text": {"content": title}}]},
            "담당자": {"rich_text": [{"text": {"content": assignee if assignee != "None" else ""}}]},
            "태그": {"multi_select": [{"name": status}]},
        }

        # 날짜 포맷 확인 후 매핑 (날짜 컬럼명: '날짜')
        if deadline and deadline != "None":
            if re.match(r"^\d{4}-\d{2}-\d{2}$", deadline.strip()):
                properties["날짜"] = {"date": {"start": deadline.strip()}}

        # 본문 블록 구성
        children = []
        if content:
            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"type": "text", "text": {"content": "📝 상세 업무 내용"}}]}
            })
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]}
            })

        # 기존 안내 callout도 유지 (선택사항)
        children.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content":
                    f"📋 상태: {status} | 👤 담당자: {assignee if assignee != 'None' else '미지정'} | 📅 마감일: {deadline if deadline != 'None' else '미정'}"
                }}],
                "icon": {"emoji": "📌"},
                "color": "gray_background"
            }
        })

        response = await self.notion.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            children=children
        )
        return response.get("id")

notion_service = NotionService()

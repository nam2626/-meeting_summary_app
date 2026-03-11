# backend/agent_service.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

class AgentService:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o")

        # 프롬프트 구성 - JSON 직접 반환 방식
        self.prompt = ChatPromptTemplate.from_template(
            "당신은 회의록에서 업무를 추출하는 전문 비서입니다.\n"
            "다음 회의록 텍스트에서 '할 일(title)', '담당자(assignee)', '마감일(deadline)'을 추출하세요.\n"
            "담당자가 없으면 'None', 마감일이 없으면 'None'으로 기입하세요.\n"
            "마감일은 반드시 'YYYY-MM-DD' 형식(예: 2025-03-15)으로만 작성하세요. 오늘 날짜는 {today}입니다.\n"
            "'내일', '다음 주' 같은 자연어 표현은 실제 날짜로 변환하세요.\n"
            "반드시 아래 JSON 배열 형식으로만 응답하고, 다른 텍스트는 절대 포함하지 마세요.\n\n"
            "예시:\n"
            "```json\n"
            "[\n"
            "  {{\"title\": \"기획서 작성\", \"assignee\": \"홍길동\", \"deadline\": \"2025-03-15\"}},\n"
            "  {{\"title\": \"디자인 검토\", \"assignee\": \"None\", \"deadline\": \"None\"}}\n"
            "]\n"
            "```\n\n"
            "회의록 원문:\n{text}"
        )

    async def extract_tasks(self, text: str):
        from datetime import date
        today = date.today().strftime("%Y-%m-%d")
        chain = self.prompt | self.llm
        result = await chain.ainvoke({"text": text, "today": today})
        
        # LLM 응답에서 JSON 파싱
        content = result.content.strip()
        # 코드 블록이 있을 경우 제거
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        tasks = json.loads(content)
        return tasks

agent_service = AgentService()

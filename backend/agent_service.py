# backend/agent_service.py
import os
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv

load_dotenv()

class AgentService:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o")
        
        # 출력 스키마 정의
        response_schemas = [
            ResponseSchema(name="tasks", description="A list of tasks extracted from the text. Each task is an object with 'title', 'assignee', and 'deadline' fields. Use 'None' if information is missing."),
        ]
        self.output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        self.format_instructions = self.output_parser.get_format_instructions()

        # 프롬프트 구성
        self.prompt = ChatPromptTemplate.from_template(
            "당신은 회의록에서 업무를 추출하는 전문 비서입니다.\n"
            "다음 회의록 텍스트에서 '할 일(title)', '담당자(assignee)', '마감일(deadline)'을 추출하여 JSON 형태로 응답하세요.\n"
            "회의록 원문:\n{text}\n\n"
            "{format_instructions}"
        )

    async def extract_tasks(self, text: str):
        chain = self.prompt | self.llm | self.output_parser
        result = await chain.ainvoke({"text": text, "format_instructions": self.format_instructions})
        return result.get("tasks", [])

agent_service = AgentService()

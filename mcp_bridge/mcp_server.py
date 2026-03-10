# mcp_bridge/mcp_server.py
import sqlite3
import os
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("MeetingMinutesAnalyzer")

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "meetings.db")

@mcp.tool()
def get_latest_meeting_summary():
    """
    가장 최근에 처리된 회의록의 제목과 원문을 SQLite에서 가져옵니다.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT title, raw_text, created_at FROM meetings ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "title": row[0],
                "raw_text": row[1],
                "created_at": row[2]
            }
        return "저장된 회의록이 없습니다."
    except Exception as e:
        return f"에러 발생: {str(e)}"

if __name__ == "__main__":
    mcp.run()

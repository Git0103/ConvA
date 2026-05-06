from typing import Dict, Any
from src.orchestration.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage

class ReportingEngine:
    def __init__(self):
        pass

    def generate_markdown_report(self, analytics_results: Dict[str, Any]) -> str:
        llm = get_llm()
        system_prompt = "You are an expert data analyst for ConvA. Generate a clean, professional Markdown report summarizing the provided analytics results."
        
        user_prompt = f"Please summarize these results into a Markdown report:\n{analytics_results}"
        
        try:
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            return response.content
        except Exception as e:
            return f"**Error generating report:** {str(e)}"

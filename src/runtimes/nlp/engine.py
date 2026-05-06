import spacy
from typing import List, Dict, Any
from src.orchestration.llm import get_llm
from langchain_core.messages import HumanMessage, SystemMessage

class NLPEngine:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # Fallback if model not downloaded
            self.nlp = None

    def extract_keywords(self, text: str) -> List[str]:
        if not self.nlp:
            # simple fallback
            return list(set([word.lower() for word in text.split() if len(word) > 4]))
        
        doc = self.nlp(text)
        keywords = [chunk.text for chunk in doc.noun_chunks]
        return list(set(keywords))

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        llm = get_llm()
        prompt = f"Analyze the sentiment of the following text. Return ONLY a valid JSON object with 'score' (float from -1.0 to 1.0) and 'label' (positive, negative, neutral).\n\nText: {text}"
        
        try:
            # Note: in production, use with_structured_output. Doing simple JSON prompt for MVP robustness if pydantic missing
            response = llm.invoke([SystemMessage(content="You are a JSON-only sentiment analyzer."), HumanMessage(content=prompt)])
            import json
            content = response.content.strip().replace("```json", "").replace("```", "")
            return json.loads(content)
        except Exception as e:
            return {"error": str(e), "label": "unknown", "score": 0.0}

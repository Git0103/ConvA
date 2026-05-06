from src.orchestration.graph import app_graph
from langchain_core.messages import HumanMessage

def test():
    # Provide a mock initial state
    initial_state = {
        "messages": [HumanMessage(content="Calculate the NPS score for the attached mock_survey.csv")],
        "request_data": {},
        "execution_plan": None,
        "analytics_results": {},
        "current_step": "start"
    }
    
    print("Invoking LangGraph Workflow...")
    final_state = app_graph.invoke(initial_state)
    
    print("\nFinal State Execution Plan:")
    if final_state.get("execution_plan"):
        print(final_state["execution_plan"].model_dump_json(indent=2))
        
    print("\nFinal Analytics Results:")
    print(final_state.get("analytics_results"))
    
    print("\nBot Response:")
    print(final_state.get("messages")[-1].content)

if __name__ == "__main__":
    test()

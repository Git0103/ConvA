from langgraph.graph import StateGraph, END
from src.orchestration.state import GraphState, ExecutionPlan
from src.orchestration.prompts import INTENT_PARSING_PROMPT
from src.orchestration.llm import get_llm
from langchain_core.messages import SystemMessage, HumanMessage
import os

def parse_intent_node(state: GraphState) -> GraphState:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "mock_key" or api_key == "your-api-key-here":
        # Mock execution plan for MVP if no key
        plan = ExecutionPlan(
            plan_id="plan_mock_001",
            intent="calculate_nps",
            steps=[
                {"step_id": "step_1", "tool": "load_tabular_file", "params": {"file_id": "mock_survey.csv"}},
                {"step_id": "step_2", "tool": "calculate_nps", "params": {"score_column": "nps_score"}}
            ]
        )
        state["execution_plan"] = plan
        return state

    try:
        # LLM parsing
        llm = get_llm(provider="openai", model_name="gpt-4o-mini").with_structured_output(ExecutionPlan)
        
        # We take the latest user message
        user_message = state.get("messages", [])[-1].content if state.get("messages") else "No message provided."
        
        messages = [
            SystemMessage(content=INTENT_PARSING_PROMPT),
            HumanMessage(content=user_message)
        ]
        
        plan = llm.invoke(messages)
        state["execution_plan"] = plan
    except Exception as e:
        print(f"Failed to parse intent: {e}")
        
    return state

def validate_plan_node(state: GraphState) -> GraphState:
    plan = state.get("execution_plan")
    if not plan:
        return state
        
    valid_tools = ["load_tabular_file", "calculate_nps", "execute_t_test"]
    for step in plan.steps:
        if step.tool not in valid_tools:
            # We can flag it as invalid and halt execution
            state["analytics_results"] = {"error": f"Tool {step.tool} is not recognized by the system."}
            # Remove execution plan to prevent execution
            state["execution_plan"] = None
            break
            
    return state

def execute_tabular_node(state: GraphState) -> GraphState:
    from src.runtimes.tabular.engine import TabularEngine
    from src.runtimes.xm.engine import XMEngine
    from src.runtimes.statistical.tests import StatisticalTests
    import os
    
    plan = state.get("execution_plan")
    if not plan:
        return state
        
    results = state.get("analytics_results", {})
    tab_engine = TabularEngine()
    xm_engine = XMEngine()
    stat_engine = StatisticalTests()
    
    for step in plan.steps:
        try:
            if step.tool == "load_tabular_file":
                file_name = step.params.get("file_id")
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
                csv_path = os.path.join(data_dir, file_name)
                
                if not os.path.exists(csv_path):
                    raise FileNotFoundError(f"Requested dataset '{file_name}' does not exist.")
                    
                tab_engine.register_file(csv_path, table_name="current_table", storage_type="local")
                results["load_tabular_file"] = "Success"
                
            elif step.tool == "calculate_nps":
                score_col = step.params.get("score_column")
                df = tab_engine.execute_query("SELECT * FROM current_table")
                nps_result = xm_engine.execute_metric("nps", df, score_col)
                results["calculate_nps"] = nps_result
                
            elif step.tool == "execute_t_test":
                target_col = step.params.get("target_column")
                group_col = step.params.get("group_column")
                df = tab_engine.execute_query("SELECT * FROM current_table")
                stat_result = stat_engine.execute_t_test(df, target_col, group_col)
                results["execute_t_test"] = stat_result
                
        except Exception as e:
            results[step.tool] = {"error": str(e), "status": "failed"}
            print(f"Tool {step.tool} failed: {e}")
            # Halt further execution upon failure to maintain deterministic validity
            break
            
    state["analytics_results"] = results
    return state

def format_response_node(state: GraphState) -> GraphState:
    # Logic to synthesize results into a final response
    results = state.get("analytics_results", {})
    if "calculate_nps" in results:
        nps = results["calculate_nps"].get("score")
        from langchain_core.messages import AIMessage
        if "messages" not in state or not isinstance(state["messages"], list):
            state["messages"] = []
        state["messages"].append(AIMessage(content=f"The calculated NPS is {nps}.")) 
    return state

# Define a new graph
workflow = StateGraph(GraphState)

# Add nodes
workflow.add_node("parse_intent", parse_intent_node)
workflow.add_node("validate_plan", validate_plan_node)
workflow.add_node("execute_tabular", execute_tabular_node)
workflow.add_node("format_response", format_response_node)

# Add edges
workflow.set_entry_point("parse_intent")
workflow.add_edge("parse_intent", "validate_plan")
workflow.add_edge("validate_plan", "execute_tabular") # Simplified routing
workflow.add_edge("execute_tabular", "format_response")
workflow.add_edge("format_response", END)

# Compile graph
app_graph = workflow.compile()

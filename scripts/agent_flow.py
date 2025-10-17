from langchain_core.runnables.graph import MermaidDrawMethod

from testcaseaiagent.workflows.main_workflow import HealthcareTestCaseGenerator

# Assuming your workflow is compiled
healthcare_generator = HealthcareTestCaseGenerator()
compiled_workflow = healthcare_generator.workflow

# Get the LangGraph underlying graph
graph = compiled_workflow.get_graph()

# Render Mermaid PNG and display in Jupyter
png_bytes = graph.draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)

# Optional: save the image locally
with open("docs/healthcare_workflow.png", "wb") as f:
    f.write(png_bytes)

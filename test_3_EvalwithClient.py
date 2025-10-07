##This is same example with Azure OpenAI client instead of using hard coded actual output
    
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval import evaluate
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import AgentThreadCreationOptions
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential,AzureCliCredential
from azure.ai.agents.models import ListSortOrder, FilePurpose
import os
load_dotenv()


correctness_metric = GEval(
    name="Correctness",
    criteria="Determine whether the actual output is factually correct based on the expected output.",
    # NOTE: you can only provide either criteria or evaluation_steps, and not both
    evaluation_steps=[
        "Check whether the facts in 'actual output' contradicts any facts in 'expected output'",
        "You should also heavily penalize omission of detail",
        "Vague language, or contradicting OPINIONS, are OK"
    ],
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
)

# Create project client from connection string
# project_client is already defined in a later cell, so we do not redefine it here
project_client = AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], 
                        credential=AzureCliCredential()
                    )
# Print the list of agents
#print(project_client.inference.get_azure_openai_client)


aiEval = project_client.agents.get_agent("asst_IpYYAJDLI5qwEc2XcEe7CGkc")
# Create a thread, run it, and process until finished (simplest approach)
final_run = project_client.agents.create_thread_and_process_run(
    agent_id=aiEval.id,
    thread={
        "messages": [
            {"role": "user", "content": "The dog chased the cat up the tree, who ran up the tree?"}
        ]
    },
)

# The run is already complete, get the messages
response=""
if final_run.status == "completed":
    # Use thread_id directly from final_run
    messages = project_client.agents.messages.list(thread_id=final_run.thread_id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.run_id == final_run.id and message.text_messages:
            #print(f"{message.role}: {message.text_messages[-1].text.value}")
            response = message.text_messages[-1].text.value
            break


 

from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input="The dog chased the cat up the tree, who ran up the tree?",
    actual_output=response,
    expected_output="The cat."
)

# To run metric as a standalone
#correctness_metric.measure(test_case)
#print(correctness_metric.score, correctness_metric.reason)

evaluate(test_cases=[test_case], metrics=[correctness_metric])

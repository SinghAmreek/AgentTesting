from dotenv import load_dotenv
load_dotenv()

import csv
import os
import pytest
import pytest_asyncio
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from testinglib.copilot_client import CopilotStudioClient
from microsoft.agents.core.models import ActivityTypes

# Load test cases from CSV
def load_test_cases_from_csv():
    csv_path = os.path.join(os.path.dirname(__file__), "../input/BWEvals2.csv")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row["Conversation"]) for row in reader]

test_cases = load_test_cases_from_csv()


@pytest.mark.asyncio
@pytest.mark.parametrize("Conversation", test_cases)
async def test_answer_relevancy(Conversation, request):
    actual_output = Conversation
   

    test_case = LLMTestCase(
        input="",
        actual_output=actual_output
    )

    metric= GEval(
    name="Custom Relevency",
    evaluation_steps=[
        "Check the conversation between the bot and the user",
        "Verify that bot asked relevent questions and the final respone is relevent to the conversation",
        "Ensure the conversation has recommended product/s, If the product recommendation is missing penalise the score",
        "The recommended product should have a good reason for the resommendation",
        "Minimum one of the recommended product should be ProSafe product"    
          ],
          threshold=.5,
          evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
    )
    metric.measure(test_case)

    # Attach to pytest-html report
    request.node.input_text = ""
    request.node.expected = ""
    request.node.actual = actual_output
    request.node.reason = metric.reason
    request.node.score = f"{metric.score:.2f}"
    request.node.conversation_id = ""

    assert metric.score >= metric.threshold, f"Score: {metric.score:.2f}, Reason: {metric.reason}"

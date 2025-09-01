from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams
from deepeval import evaluate

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

from deepeval.test_case import LLMTestCase
...

test_case = LLMTestCase(
    input="The dog chased the cat up the tree, who ran up the tree?",
    actual_output="It depends, some might consider the cat, while others might argue the dog.",
    expected_output="The cat."
)

# To run metric as a standalone
#correctness_metric.measure(test_case)
#print(correctness_metric.score, correctness_metric.reason)

evaluate(test_cases=[test_case], metrics=[correctness_metric])
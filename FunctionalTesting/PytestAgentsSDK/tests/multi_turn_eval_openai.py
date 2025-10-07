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
    csv_path = os.path.join(os.path.dirname(__file__), "../input/test_cases2.csv")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [(row["input_text"], row["expected_output"]) for row in reader]

test_cases = load_test_cases_from_csv()

@pytest_asyncio.fixture(scope="session")
async def started_client():
    client = CopilotStudioClient()
    async for activity in client.client.start_conversation():
        if client.client._current_conversation_id:
            break
    client.conversation_id = client.client._current_conversation_id
    print(f"[DEBUG] Started conclearversation with ID: {client.conversation_id}")
    return client

@pytest.mark.asyncio
@pytest.mark.parametrize("input_text, expected_output", test_cases)
async def test_answer_relevancy(input_text, expected_output, started_client, request):
    actual_output = ""
    async for activity in started_client.client.ask_question(input_text):
        if activity and activity.type == ActivityTypes.message:
            actual_output += activity.text or ""

    test_case = LLMTestCase(
        input=input_text,
        actual_output=actual_output.strip(),
        #actual_output='Turn 1 - Azure AI Agent: Absolutely! Cut-resistant gloves are essential for mining operations due to the risk of handling sharp tools, heavy machinery, and jagged rocks. \n\nCould you share which specific tasks or materials your team handles most often? That way, I can recommend the right glove materials and cut-resistance levels for your environment.\n\nTurn 2 - Copilot Studio: **Cut-Resistant Gloves for Mining Operations**\n\n**Common Mining Tasks and Materials:**\n- Handling sharp tools and equipment\n- Operating heavy machinery\n- Managing jagged rocks and metal components\n\n**Recommended Glove Materials:**\n- **Polyethylene and Recycled Polyester:** Offers durability and cut resistance, suitable for tasks requiring protection against mechanical risks.\n- **Nitrile Coating:** Provides enhanced grip in wet, oily, or dry conditions, and improves breathability for comfort during extended use.\n- **Goatskin Leather:** Delivers comfort and flexibility, ideal for tasks requiring dexterity and abrasion resistance.\n\n**Performance Level Ratings (EN 388:2016):**\n- **Durashield Cut D Nitrile Foam Gloves:**\n  - Abrasion Resistance: Level 4 (8000 cycles)\n  - Blade Cut Resistance: Level 5 (20.0 index)\n  - Tear Resistance: Level 4 (75 Newtons)\n  - Puncture Resistance: Level 4 (150 Newtons)\n  - EN ISO Cut Resistance: Level D (15 Newtons)\n  - Impact Protection: Not Applicable\n  - Complies with EN 388:2016 +A1:2018 and ISO 21420 standards\n  - Suitable for mining and metal fabrication industries [1]\u200b[2]\n\n- **Mechanics Goat Palm W901 Glove:**\n  - Abrasion Resistance: Level 2 (500 cycles)\n  - Blade Cut Resistance: Level 1 (1.2 index)\n  - Tear Resistance: Level 1 (25 Newtons)\n  - Puncture Resistance: Level 1 (60 Newtons)\n  - EN ISO Cut Resistance: Not rated\n  - Impact Protection: Not Applicable\n  - Complies with EN 388:2016 standards\n  - Suitable for heavy equipment operation and general maintenance in mining [3]\n\n**Compliance Examples:**\n- EN 388:2016 +A1:2018 Protective gloves against mechanical risks\n- ISO 21420 General requirements for protective gloves\n- AS 4399:2020 UPF 50+ for sun protection [1]\u200b[2]\n\n**Selection Guidance:**\n- For high-risk tasks involving sharp or jagged materials, select gloves with higher cut resistance (Level D or above).\n- For tasks requiring dexterity and comfort, consider gloves with flexible materials and ergonomic design.\n- Always inspect gloves before use and replace if damaged to maintain safety standards.\n\nThese recommendations ensure your team is protected according to industry standards and the specific hazards present in mining operations [1]\u200b[3]\u200b[2].\n\n[1]: cite:1 "Citation-1"\n[2]: cite:2 "Citation-2"\n[3]: cite:3 "Citation-3"**Tasks and Materials Handled by Mining Teams:**\n\n- **Building and Construction:** Mining teams are often involved in tasks related to building and construction within mining sites, such as erecting structures or maintaining facilities.\n- **Forestry:** Some mining operations may intersect with forestry activities, requiring handling of wood and related materials.\n- **Metal Fabrication:** Mining teams frequently handle metal materials, including extraction, processing, and fabrication of metals.\n- **Mechanical Risks:** Tasks often involve handling materials or equipment that pose mechanical risks, necessitating protective gloves and other safety gear.\n\nThese activities require protection against mechanical risks, and suitable gloves are recommended for these tasks to ensure safety and compliance with industry standards [1].\n\n[1]: cite:1 "Citation-1"\n\nTurn 3 - Azure AI Agent: Thanks for the detailed breakdown and the EN 388 ratings—those are crucial for selecting the right gloves.\n\nGiven the variety of tasks, how do you currently train your team on glove selection and proper use? Do you have a standardized process in place, or does it vary depending on the operation or job role?\n\nTurn 4 - Copilot Studio: **Glove Selection and Training in Mining Operations**\n\n**Standardized Process vs. Role-Based Variation**\n- Training on glove selection and proper use can be standardized or tailored based on the specific operation or job role.\n- A standardized process typically involves:\n  - Educating workers on the importance of wearing the correct glove size, as poorly fitted gloves can be hazardous by restricting dexterity or affecting grip and comfort.\n  - Instructing staff to measure hand circumference 2cm up from the base of the thumb to determine the correct glove size.\n  - Providing guidelines for inspecting gloves before each use to ensure they are not torn, punctured, or otherwise compromised.\n  - Training on cleaning, storage, and disposal procedures, such as spot cleaning with a damp cloth, storing gloves in cool, dry places away from sunlight, and disposing of damaged gloves according to local regulations.\n- Role-based variation may occur, with specific gloves recommended for tasks like welding, heavy equipment operation, or metal fabrication, each requiring different performance ratings and compliance standards.\n\n**Examples of Performance Level Ratings and Compliance Levels**\n- **EN 388:2016** and **EN 388:2003** are common standards for mechanical risks, with ratings such as:\n  - **2111X**: Indicates levels for abrasion, blade cut, tear, and puncture resistance, with \'X\' meaning a test was not carried out.\n  - **4144**: For example, the WeldTECH Black Glove is rated 4144 under EN388:2003, which means:\n    - Abrasion Resistance: Level 4\n    - Blade Cut Resistance: Level 1\n    - Tear Resistance: Level 4\n    - Puncture Resistance: Level 4\n- **EN 407:2004**: For heat and flame hazards, with ratings like 414X4X, indicating performance in burning behavior, contact heat, convective heat, radiant heat, and molten metal resistance.\n- **EN 388:2016 +A1:2018** and **ISO 21420**: For gloves like Durashield Cut D, which are suitable for mining and metal fabrication, ensuring protection against mechanical risks and general requirements for protective gloves.\n\n**Practical Training Steps**\n- Workers are trained to:\n  - Inspect gloves for damage before use and replace if necessary.\n  - Select gloves based on the required performance level for the task (e.g., higher abrasion and tear resistance for heavy-duty tasks).\n  - Follow cleaning and storage instructions to maintain glove integrity.\n  - Dispose of gloves responsibly, following local regulations.\n\n**Summary**\n- Mining operations may use a combination of standardized training and role-specific guidelines for glove selection and use.\n- Performance ratings like EN388:2003 4144 and compliance with standards such as EN 388:2016, EN 407:2004, and ISO 21420 are integral to the process, ensuring workers are protected according to the risks of their specific tasks [1]\u200b[2]\u200b[3].\n\n[1]: cite:1 "Citation-1"\n[2]: cite:2 "Citation-2"\n[3]: cite:3 "Citation-3"**Glove Selection and Training in Mining Operations**\n\n**Training Approach:**\n- Teams are typically trained to select gloves based on the specific mechanical risks present in their work environment. For example, gloves like the PROSAFE Durashield Cut D are suitable for industries such as mining, metal fabrication, construction, and forestry, where protection against mechanical risks is essential.\n- Training includes understanding the standards and compliance requirements, such as EN 388:2016 +A1:2018 for mechanical risks and ISO 21420 for general requirements. Workers are instructed to inspect gloves before each use to ensure they are not torn, punctured, or otherwise ineffective.\n- Proper glove use is emphasized, including the importance of wearing the correct size for optimal dexterity and safety. Teams are taught how to measure hand circumference and select the appropriate glove size, as poorly fitted gloves can be hazardous by restricting movement or affecting grip and dexterity.\n- Instructions are provided on glove care, including washing, drying, and storage, as well as regular checks for degradation over time.\n\n**Standardization:**\n- There are standardized processes based on international and national standards (such as EN 388:2016 +A1:2018, ISO 21420, and AS 4399:2020 UPF 50+), which guide glove selection and use.\n- However, the specific training and selection process may vary by operation or job role, depending on the unique risks and requirements of each task or site. For example, some gloves are only for minimal risks and should not be used where there is a risk of entanglement.\n\n**Summary:**\n- While there are standardized guidelines and compliance requirements, the actual training and glove selection process can vary depending on the operation and job role, tailored to the specific hazards and needs of the mining environment [1]\u200b[2].\n\n[1]: cite:1 "Citation-1"\n[2]: cite:2 "Citation-2"\n\nTurn 5 - Azure AI Agent: That’s a thorough approach, especially with the emphasis on sizing and inspection. \n\nHow often do you conduct refresher training or audits to ensure ongoing compliance with glove use and maintenance procedures? Have you noticed any challenges with adoption or consistency among different teams or roles?\n\n',
        expected_output=expected_output
    )

    metric = GEval(
        name="Correctness",
        evaluation_steps=[
            "Check whether the facts in 'actual output' contradict any facts in 'expected output'",
            "You should also heavily penalize omission of detail",
            "Vague language, or contradicting OPINIONS, are OK",
            "Do not penalize disclaimers about AI-generated content being possibly incorrect",
        ],
        threshold=0.50,
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT] 
    )
    metric.measure(test_case)

    # Attach to pytest-html report
    request.node.input_text = input_text
    request.node.expected = expected_output
    request.node.actual = actual_output.strip()
    request.node.reason = metric.reason
    request.node.score = f"{metric.score:.2f}"
    request.node.conversation_id = started_client.conversation_id

    assert metric.score >= metric.threshold, f"Score: {metric.score:.2f}, Reason: {metric.reason}"

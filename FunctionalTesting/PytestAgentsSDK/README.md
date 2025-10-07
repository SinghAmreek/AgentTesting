# PytestAgentsSDK

This project provides a sample test harness for evaluating Copilot Studio agents using [**Pytest**](https://docs.pytest.org/en/stable/) and [**DeepEval**](https://github.com/confident-ai/deepeval). It uses the [Microsoft 365 Agents SDK](https://github.com/microsoft/agents) to communicate with Copilot Studio and focuses on **semantic evaluation** of agent responses using DeepEval’s `GEval` metric.

## Features

- Multi-turn conversation testing against a Copilot Studio agent
- Semantic response evaluation using DeepEval’s `GEval` metric
- Loads test cases from a CSV file
- Custom HTML reporting with detailed metadata (user input, actual and expected output, score, reason)
- Authentication via MSAL, supporting [“Authenticate with Microsoft”](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-end-user-authentication#authenticate-with-microsoft) in Copilot Studio
- Easily extensible for use with additional metrics and long-term result tracking using DeepEval and Pytest plugins

---

## Setup

### **1. Clone the repository**

```bash
git clone https://github.com/microsoft/CopilotStudioSamples.git
cd CopilotStudioSamples/FunctionalTesting/PytestAgentsSDK
```

### **2. Create and activate a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

### **3. Install required dependencies**

```bash
pip install -r requirements.txt
```

### **4. Create an app registration**

You will need to register an application in Azure for the SDK to authenticate with Copilot Studio:

- Create a **single-tenant** app registration in Azure
- Under **Authentication → Platform configurations**, click **Add a platform**, and select **Mobile and desktop applications**
- Add these redirect URIs:
  - `msal40347a26-35bb-48f3-bdc4-7f4f209aecb1://auth`  (MSAL only)
  - `http://localhost`
- Under **API permissions**, click **Add a permission**
  - Choose **APIs my organization uses**, then search for **Power Platform API**
  - Choose **Delegated permissions**, then add `CopilotStudio.Copilots.Invoke`

### **5. Authentication and Agent details**

Create a `.env` file (you can copy from `.env.template`) and populate it with your MSAL and Copilot Studio agent configuration:

```env
APP_CLIENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ENVIRONMENT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
AGENT_IDENTIFIER=cr26e_dMyAgent  # This is the schema name, found under Settings > Advanced > Metadata
```

### **6. Configure Azure AI Agent (for Agent-to-Agent Testing)**

For agent-to-agent conversation testing, you'll need to configure an Azure AI agent. Add these settings to your `.env` file:

#### Option 1: GitHub Models (Recommended for Testing)
```env
AZURE_AI_ENDPOINT=https://models.github.ai/inference
AZURE_AI_MODEL=openai/gpt-4.1-mini
GITHUB_TOKEN=your_github_token_here
```

#### Option 2: Azure AI Foundry 
```env
AZURE_AI_ENDPOINT=https://your-foundry-model-endpoint
AZURE_AI_MODEL=your-deployed-model-name
AZURE_API_KEY=your_azure_api_key_here
```

#### Optional: Custom System Prompt
```env
AZURE_AI_SYSTEM_PROMPT="Your custom system prompt for the Azure AI agent"
```

### **7. Configure Azure OpenAI or OpenAI details**

You can use either OpenAI or Azure OpenAI with DeepEval.

#### To configure Azure OpenAI using the DeepEval CLI:

```bash
deepeval set-azure-openai \
    --openai-endpoint=<endpoint> \                     # e.g. https://example-resource.openai.azure.com/
    --openai-api-key=<api_key> \
    --openai-model-name=<model_name> \                 # e.g. gpt-4o
    --deployment-name=<deployment_name> \              # e.g. Test Deployment
    --openai-api-version=<openai_api_version>          # e.g. 2025-01-01-preview
```

> These values will be stored in a local `.deepeval` configuration file.

Alternatively, if you're using OpenAI (not Azure), set the following environment variable:

```bash
export OPENAI_API_KEY=<your-openai-key>
```

### **7. Publish and set agent authentication**

Before running tests, ensure that your Copilot Studio agent is:

- **Published** in the Copilot Studio portal
- Configured to use **[Authenticate with Microsoft](https://learn.microsoft.com/en-us/microsoft-copilot-studio/configuration-end-user-authentication#authenticate-with-microsoft)** under **Settings > Security > Authentication**

### **8. Prepare Test Cases (CSV Input)**

Before running the tests, populate the CSV file at `input/test_cases.csv` with your test cases.

The CSV file must contain two columns:

- `input_text`: The message sent to the Copilot Studio agent
- `expected_output`: The ideal response you'd expect from the agent

#### Example:

```csv
input_text,expected_output
What is the capital of France?,The capital of France is Paris, which is known for its historical landmarks like the Eiffel Tower and the Louvre Museum.
Who wrote 'Hamlet'?,William Shakespeare wrote the play 'Hamlet', which is considered one of the greatest works of English literature.
What is the chemical symbol for water?,H3O is the correct chemical symbol for water.
```

---

## Running the Tests

From the `PytestAgentsSDK` directory, you can run different types of tests:

### Agent-to-Agent Conversation Testing

Run the new agent-to-agent conversation tests:

```bash
pytest tests/multi_turn_with_agent --html=reports/agent_to_agent_conversation.html --self-contained-html
```

This will:
- Initialize both Azure AI agent and Copilot Studio agent
- Start conversations on predefined topics (industrial safety equipment scenarios)
- Facilitate up to 5 turns of conversation between the agents
- Evaluate conversation quality and theme relevance
- Generate detailed HTML reports with full conversation transcripts

### Traditional CSV-Based Testing

Run the original CSV-based tests:

```bash
pytest tests/multi_turn_eval_openai.py --html=reports/multi_turn_eval_openai.html --self-contained-html
```

This will:
- Start a conversation with your Copilot Studio agent
- Send test questions from CSV and capture responses  
- Evaluate the responses using DeepEval
- Generate a self-contained HTML report in the `reports/` folder

---

## Output

### Agent-to-Agent Conversation Reports

The agent-to-agent HTML reports include:

- Pass/Fail status for conversation quality and theme relevance metrics
- Full conversation transcripts with turn-by-turn dialogue
- Conversation summaries (total turns, participant distribution)
- DeepEval scores for conversation quality and theme relevance
- Detailed explanations for evaluation results
- Initial topics and expected themes
- Conversation IDs for debugging

### Traditional CSV-Based Reports

The traditional HTML reports include:

- Pass/Fail status based on semantic threshold
- User message and expected answer
- Actual response from the agent
- DeepEval score
- Explanation for the result
- Conversation ID (for debugging)
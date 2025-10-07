# AgentTesting
# Create a python environment
    python3 -m venv .venv

# Activate the environment
    source .venv/bin/activate

# run the requirement.txt
pip install -r requirements.txt

# set the Open AI Key
deepeval set-azure-openai \
    --openai-endpoint=<endpoint> \ # e.g. https://example-resource.azure.openai.com/
    --openai-api-key=<api_key> \
    --openai-model-name=<model_name> \ # e.g. gpt-4.1
    --deployment-name=<deployment_name> \  # e.g. Test Deployment
    --openai-api-version=<openai_api_version> \ # e.g. 2025-01-01-preview

or export OPENAI_API_KEY=<your-openai-api-key>

# run the test in the terminal
deepeval test run test_1_example.py
deepeval test run test_2_example_with_evaluate.py
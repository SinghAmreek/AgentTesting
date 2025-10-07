"""
Agent-to-Agent Conversation Testing Suite

This module provides comprehensive testing for multi-turn conversations between
Azure AI Agent and Copilot Studio Agent, including quality evaluation and 
conversation flow validation.

Features:
- Multi-turn conversation orchestration
- Quality evaluation using GEval metrics
- Turn limit enforcement
- HTML report generation with detailed conversation logs
"""

# Environment setup
from dotenv import load_dotenv
load_dotenv()

# Standard library imports
import asyncio
import os

# Third-party testing imports
import pytest
import pytest_asyncio

# DeepEval imports for conversation quality assessment
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

# Local client imports
from testinglib.copilot_client import CopilotStudioClient
from testinglib.azure_ai_agent_client import AzureAIAgentClient
from testinglib.config import AzureAIAgentSettings

# Microsoft Agents framework
from microsoft.agents.core.models import ActivityTypes

# ==========================================
# CONFIGURATION CONSTANTS
# ==========================================

# Maximum number of conversation turns allowed before termination
MAX_TURNS = 20

# Test scenarios for agent-to-agent conversation evaluation
# Each scenario defines:
# - name: Descriptive name for the test case
# - initial_topic: Starting conversation topic
# - expected_themes: Keywords that should appear in quality conversation
CONVERSATION_SCENARIOS = [
    {
        "name": "Industrial Safety Equipment Inquiry",
        "initial_topic": "I need cut-resistant gloves for mining operations",
        "expected_themes": ["cut resistance", "mining", "gloves", "safety", "compliance"]
    }   
]


# ==========================================
# DATA MODELS
# ==========================================

class ConversationTurn:
    """
    Represents a single turn in the agent-to-agent conversation.
    
    This class encapsulates all information about one message exchange,
    including who sent it, what was said, and when it occurred.
    
    Attributes:
        turn_number (int): Sequential turn number in the conversation (1-based)
        sender (str): Agent identifier ("azure_ai_agent" or "copilot_studio")
        message (str): The actual message content/text
        timestamp (float): When this turn occurred (defaults to 0.0)
    """
    
    def __init__(self, turn_number: int, sender: str, message: str, timestamp: float = None):
        self.turn_number = turn_number
        self.sender = sender
        self.message = message
        self.timestamp = timestamp or 0.0
        

# ==========================================
# CONVERSATION ORCHESTRATION
# ==========================================

class AgentToAgentConversation:
    """
    Orchestrates and manages multi-turn conversations between two AI agents.
    
    This class handles the complete conversation lifecycle:
    - Initialization and state management
    - Turn-by-turn message exchange
    - Conversation termination conditions
    - Data collection and analysis
    
    The conversation alternates between Azure AI Agent and Copilot Studio,
    with proper handling of timeouts, errors, and maximum turn limits.
    """
    
    def __init__(self, azure_ai_client: AzureAIAgentClient, copilot_client: CopilotStudioClient):
        """
        Initialize conversation manager with both AI agent clients.
        
        Args:
            azure_ai_client: Client for Azure AI Agent interactions
            copilot_client: Client for Copilot Studio interactions
        """
        self.azure_ai_client = azure_ai_client
        self.copilot_client = copilot_client
        self.turns: list[ConversationTurn] = []
        self.current_turn = 0
        
    async def start_conversation(self, initial_topic: str) -> list[ConversationTurn]:
        """
        Start and manage the complete agent-to-agent conversation.
        
        This method orchestrates the entire conversation flow:
        1. Resets conversation state for a fresh start
        2. Initiates conversation with the specified topic
        3. Manages alternating turns between both agents
        4. Enforces turn limits and termination conditions
        5. Returns complete conversation history
        
        Args:
            initial_topic: The topic/question to start the conversation with
            
        Returns:
            List of ConversationTurn objects representing the complete conversation
        """
        # === INITIALIZATION PHASE ===
        # Clear any previous conversation data
        self.turns = []
        self.current_turn = 0
        
        # Start with Azure AI Agent's initial message
        # Note: Using the topic directly rather than invoking the agent for first turn
        initial_message = initial_topic
        self.current_turn += 1
        self.turns.append(ConversationTurn(self.current_turn, "azure_ai_agent", initial_message))
        
        # Brief pause to allow async cleanup of any background tasks
        await asyncio.sleep(0.1)
        
        # === MAIN CONVERSATION LOOP ===
        # Continue alternating turns until MAX_TURNS limit or natural termination
        while self.current_turn < MAX_TURNS:
            # Get the most recent message to forward to Copilot Studio
            current_message = self.turns[-1].message
            
            # --- COPILOT STUDIO TURN ---
            # Send message to Copilot Studio and collect its response
            copilot_response = ""
            async for activity in self.copilot_client.client.ask_question(current_message):
                if activity and activity.type == ActivityTypes.message:
                    copilot_response += activity.text or ""
            
            # Record Copilot Studio's response as a new turn
            self.current_turn += 1
            self.turns.append(ConversationTurn(self.current_turn, "copilot_studio", copilot_response.strip()))
            
            # --- TERMINATION CONDITIONS ---
            # Stop conversation if:
            # 1. Maximum turns reached
            # 2. Copilot Studio provides empty response
            if self.current_turn >= MAX_TURNS or not copilot_response.strip():
                break
                
            # --- AZURE AI AGENT TURN ---
            # Let Azure AI Agent respond to Copilot Studio's message
            if self.current_turn < MAX_TURNS:
                next_message = await self.azure_ai_client.continue_conversation(
                    copilot_response.strip(), 
                    self.current_turn
                )
                self.current_turn += 1
                self.turns.append(ConversationTurn(self.current_turn, "azure_ai_agent", next_message))
                
                # Brief pause for async task cleanup between turns
                await asyncio.sleep(0.1)
        
        return self.turns
    
    def get_full_conversation_text(self) -> str:
        """
        Generate a human-readable text representation of the entire conversation.
        
        Formats each turn with clear sender identification and turn numbering
        for easy reading in reports and logs.
        
        Returns:
            Formatted string containing the complete conversation transcript
        """
        conversation_text = ""
        for turn in self.turns:
            sender_label = "Azure AI Agent" if turn.sender == "azure_ai_agent" else "Copilot Studio"
            conversation_text += f"Turn {turn.turn_number} - {sender_label}: {turn.message}\n\n"
        return conversation_text
    
    def get_conversation_summary(self) -> dict:
        """
        Generate statistical summary and metadata about the conversation.
        
        Provides key metrics for analysis and reporting, including turn counts,
        participation levels, and detailed turn-by-turn breakdown.
        
        Returns:
            Dictionary containing conversation analytics and complete turn data
        """
        return {
            "total_turns": len(self.turns),
            "azure_ai_turns": len([t for t in self.turns if t.sender == "azure_ai_agent"]),
            "copilot_studio_turns": len([t for t in self.turns if t.sender == "copilot_studio"]),
            "conversation_length": len(self.get_full_conversation_text()),
            "turns": [{"turn": t.turn_number, "sender": t.sender, "message": t.message} for t in self.turns]
        }


# ==========================================
# PYTEST FIXTURES
# ==========================================

@pytest_asyncio.fixture(scope="session")
async def copilot_client():
    """
    Initialize and configure Copilot Studio client for testing.
    
    This session-scoped fixture:
    - Creates a new Copilot Studio client instance
    - Establishes a conversation session
    - Provides conversation ID for tracking
    - Shares the client across all tests in the session
    
    Returns:
        CopilotStudioClient: Ready-to-use client with active conversation
    """
    client = CopilotStudioClient()
    
    # Initialize conversation and wait for conversation ID
    async for activity in client.client.start_conversation():
        if client.client._current_conversation_id:
            break
    
    # Store conversation ID for debugging and tracking
    client.conversation_id = client.client._current_conversation_id
    print(f"[DEBUG] Started Copilot Studio conversation with ID: {client.conversation_id}")
    
    return client


@pytest_asyncio.fixture(scope="session")
async def azure_ai_client():
    """
    Initialize and configure Azure AI Agent client for testing.
    
    This session-scoped fixture:
    - Loads configuration from AzureAIAgentSettings
    - Creates authenticated Azure AI Agent client
    - Configures system prompt and model settings
    - Handles proper cleanup after all tests complete
    
    Yields:
        AzureAIAgentClient: Configured client ready for conversations
    """
    # Load configuration settings
    settings = AzureAIAgentSettings()
    
    # Create client with loaded configuration
    client = AzureAIAgentClient(
        endpoint=settings.endpoint,
        model=settings.model,
        api_key=settings.api_key,
        system_prompt=settings.system_prompt
    )
    print(f"[DEBUG] Initialized Azure AI Agent with model: {settings.model}")
    
    yield client
    
    # === CLEANUP PHASE ===
    # Properly close client connections when tests complete
    if hasattr(client.client, 'close'):
        try:
            client.client.close()
        except:
            pass  # Ignore cleanup errors to prevent test failures


# ==========================================
# MAIN TEST FUNCTIONS
# ==========================================

@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", CONVERSATION_SCENARIOS)
async def test_agent_to_agent_conversation(scenario, copilot_client, azure_ai_client, request):
    """
    Comprehensive test for agent-to-agent conversation quality and flow.
    
    This test validates the complete conversation lifecycle:
    1. Conversation initialization with specified topic
    2. Multi-turn dialogue exchange between both agents
    3. Quality assessment using GEval metrics
    4. Constraint validation (turn limits, participation)
    5. Report generation with detailed conversation logs
    
    The test ensures both agents participate meaningfully and stay on topic
    while respecting conversation limits and producing quality exchanges.
    
    Args:
        scenario: Test scenario containing topic and expected themes
        copilot_client: Copilot Studio client fixture
        azure_ai_client: Azure AI Agent client fixture
        request: Pytest request object for HTML report generation
    
    Raises:
        AssertionError: If conversation constraints or quality thresholds are not met
    """
    # === CONVERSATION EXECUTION ===
    # Initialize conversation orchestrator with both agent clients
    conversation = AgentToAgentConversation(azure_ai_client, copilot_client)
    
    # Execute the complete conversation flow
    turns = await conversation.start_conversation(scenario["initial_topic"])
    
    # Generate conversation analytics and formatted output
    summary = conversation.get_conversation_summary()
    full_conversation = conversation.get_full_conversation_text()
    
    # === CONSTRAINT VALIDATION ===
    # Verify conversation meets basic requirements
    assert len(turns) <= MAX_TURNS, f"Conversation exceeded maximum turns ({MAX_TURNS})"
    assert len(turns) >= 2, "Conversation should have at least 2 turns"
    assert summary["azure_ai_turns"] >= 1, "Azure AI Agent should participate in conversation"
    assert summary["copilot_studio_turns"] >= 1, "Copilot Studio should participate in conversation"
    
    # === QUALITY EVALUATION SETUP ===
    # Create test case for DeepEval quality assessment
    test_case = LLMTestCase(
        input=f"Initial topic: {scenario['initial_topic']}",
        actual_output=full_conversation,
        expected_output=f"A meaningful multi-turn conversation about {', '.join(scenario['expected_themes'])}"
    )
    
    # Configure conversation quality evaluation metric
    conversation_quality_metric = GEval(
        name="Conversation Quality",
        evaluation_steps=[
            "Check if the conversation flows naturally between the two agents",
            "Verify that both agents stay on topic and provide relevant responses",
            "Ensure the conversation demonstrates meaningful information exchange",
            "Check if the Copilot Studio agent provides helpful information about safety equipment",
            "Verify that the Azure AI agent asks appropriate follow-up questions"
        ],
        threshold=0.60,  # Minimum acceptable quality score (60%)
        evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT]
    )
    
    # === QUALITY MEASUREMENT ===
    # Execute the quality evaluation
    conversation_quality_metric.measure(test_case)
    
    # === HTML REPORT INTEGRATION ===
    # Attach detailed conversation data to pytest HTML report
    request.node.input_text = scenario["initial_topic"]
    request.node.expected = ""
    request.node.actual = full_conversation
    request.node.reason = conversation_quality_metric.reason
    request.node.score = f"{conversation_quality_metric.score:.2f}"
    request.node.conversation_id = copilot_client.conversation_id

    # === FINAL QUALITY ASSERTION ===
    # Ensure conversation quality meets minimum acceptable threshold
    assert conversation_quality_metric.score >= conversation_quality_metric.threshold, \
        f"Conversation Quality Score: {conversation_quality_metric.score:.2f}, Reason: {conversation_quality_metric.reason}"

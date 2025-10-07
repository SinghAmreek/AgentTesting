import asyncio
import os
from typing import AsyncGenerator, List, Dict, Any
from openai import AzureOpenAI
import httpx

class AzureAIAgentClient:
    """Client for interacting with Azure AI agents through OpenAI-compatible endpoints"""
    
    def __init__(self, endpoint: str = None, model: str = None, api_key: str = None, system_prompt: str = None):
        """
        Initialize the Azure AI Agent client
        
        Args:
            endpoint: The Azure AI endpoint URL (can be GitHub models or Azure AI Foundry)
            model: The model name to use
            api_key: API key or token for authentication
            system_prompt: System prompt to define the agent's behavior
        """
        self.endpoint = endpoint or os.environ.get("AZURE_AI_ENDPOINT", "https://models.github.ai")
        self.model = model or os.environ.get("AZURE_AI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or os.environ.get("GITHUB_TOKEN") or os.environ.get("AZURE_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key must be provided via parameter or environment variable (GITHUB_TOKEN or AZURE_API_KEY)")
        
        # Determine if this is an Azure endpoint
        is_azure_endpoint = "azure.com" in self.endpoint
        
        if is_azure_endpoint:
            # Azure OpenAI configuration
            self.client = AzureOpenAI(
                api_version="2024-12-01-preview",
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
            )
        else:
            # For non-Azure endpoints (like GitHub Models), fall back to regular OpenAI client
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.endpoint + ("/v1" if not self.endpoint.endswith("/v1") else ""),
            )
        
        # Default system prompt for an agent that initiates conversations with Copilot Studio
        self.system_prompt = system_prompt or """You are a Simulator AI Agent having a structured conversation with a Product Advisor AI Agent.
The Product Advisor will ask questions and provide numbered options (e.g., Option 1, Option 2, etc.).
Your task is to respond by selecting one of the provided options.
If the Product Advisor provides a product recommendation, end the conversation immediately and do not respond further.

Sample Interaction: 
The other agents question
  What level of cut resistance do you require for the gloves? Options:
    1. Level A (Minimal cut resistance)
    2. Level B (Low cut resistance)
    3. Level C (Moderate cut resistance)
    4. Level D (High cut resistance)
    5. Level E (Maximum cut resistance)

    
Your response can be :
5

Do not provide any explanation or commentary. Only respond with the selected option."""
        
        self.conversation_history: List[Dict[str, Any]] = []
        
    async def start_conversation(self, initial_topic: str = None) -> str:
        """
        Start a conversation with an initial message
        
        Args:
            initial_topic: Optional initial topic to start the conversation
            
        Returns:
            The first message from this agent
        """
        if not initial_topic:
            initial_topic = "Hello! I'm looking for information about industrial safety equipment. Can you help me?"
        
        # Clear previous conversation history
        self.conversation_history = []
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Start a conversation about: {initial_topic}"}
        ]
        
        try:
            # Use asyncio.to_thread to run synchronous client in async context
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            first_message = response.choices[0].message.content
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": first_message,
                "turn": 1
            })
            
            return first_message
        except Exception as e:
            # Ensure any background tasks are properly handled
            await asyncio.sleep(0)  # Give other tasks a chance to complete
            raise Exception(f"Failed to start conversation: {str(e)}")
    
    async def continue_conversation(self, other_agent_response: str, turn_number: int) -> str:
        """
        Continue the conversation based on the other agent's response
        
        Args:
            other_agent_response: The response from the other agent
            turn_number: Current turn number in the conversation
            
        Returns:
            This agent's response
        """
        # Add the other agent's response to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": other_agent_response,
            "turn": turn_number
        })
        
        # Build messages for the API call
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        for entry in self.conversation_history:
            if entry["role"] == "assistant":
                messages.append({"role": "assistant", "content": entry["content"]})
            else:
                messages.append({"role": "user", "content": entry["content"]})
        
        # Add instruction for continuation
        messages.append({
            "role": "user", 
            "content": f"Continue the conversation based on the response above. This is turn {turn_number + 1} of the conversation."
        })
        
        try:
            # Use asyncio.to_thread to run synchronous client in async context
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            next_message = response.choices[0].message.content
            
            # Store in conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": next_message,
                "turn": turn_number + 1
            })
            
            return next_message
        except Exception as e:
            # Ensure any background tasks are properly handled
            await asyncio.sleep(0)  # Give other tasks a chance to complete
            raise Exception(f"Failed to continue conversation: {str(e)}")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the full conversation history"""
        return self.conversation_history.copy()
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []
        
    def __del__(self):
        """Cleanup when the object is destroyed"""
        if hasattr(self.client, 'close'):
            try:
                self.client.close()
            except:
                pass  # Ignore errors during cleanup
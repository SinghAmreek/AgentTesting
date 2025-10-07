from os import environ
from typing import Optional

from microsoft.agents.copilotstudio.client import (
    ConnectionSettings,
    PowerPlatformCloud,
    AgentType,
)

##added the new code

class AzureAIAgentSettings:
    """Configuration settings for Azure AI Agent client"""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> None:
        self.endpoint = endpoint or environ.get("AZURE_AI_ENDPOINT", "https://models.github.ai")
        self.model = model or environ.get("AZURE_AI_MODEL", "gpt-4o-mini")
        self.api_key = api_key or environ.get("GITHUB_TOKEN") or environ.get("AZURE_API_KEY")
        
        # Default system prompt for agent-to-agent conversations
        default_system_prompt = """You are an AI agent designed to have conversations with another AI agent (Copilot Studio). 
Your role is to ask questions, seek information, and engage in meaningful dialogue about industrial safety equipment and related topics.
Be conversational, ask follow-up questions based on responses, and maintain context throughout the conversation.
Keep your messages concise and focused."""
        
        self.system_prompt = system_prompt or environ.get("AZURE_AI_SYSTEM_PROMPT", default_system_prompt)
        
        if not self.api_key:
            raise ValueError("API key must be provided via parameter or environment variable (GITHUB_TOKEN or AZURE_API_KEY)")

###end of the new code
class McsConnectionSettings(ConnectionSettings):
    def __init__(
        self,
        app_client_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        environment_id: Optional[str] = None,
        agent_identifier: Optional[str] = None,
        cloud: Optional[PowerPlatformCloud] = None,
        copilot_agent_type: Optional[AgentType] = None,
        custom_power_platform_cloud: Optional[str] = None,
    ) -> None:
        self.app_client_id = app_client_id or environ.get("APP_CLIENT_ID")
        self.tenant_id = tenant_id or environ.get("TENANT_ID")

        if not self.app_client_id:
            raise ValueError("App Client ID must be provided")
        if not self.tenant_id:
            raise ValueError("Tenant ID must be provided")

        environment_id = environment_id or environ.get("ENVIRONMENT_ID")
        agent_identifier = agent_identifier or environ.get("AGENT_IDENTIFIER")
        cloud = cloud or PowerPlatformCloud[environ.get("CLOUD", "UNKNOWN")]
        copilot_agent_type = (
            copilot_agent_type
            or AgentType[environ.get("COPILOT_agent_type", "PUBLISHED")]
        )
        custom_power_platform_cloud = custom_power_platform_cloud or environ.get(
            "CUSTOM_POWER_PLATFORM_CLOUD", None
        )

        super().__init__(
            environment_id,
            agent_identifier,
            cloud,
            copilot_agent_type,
            custom_power_platform_cloud,
        )
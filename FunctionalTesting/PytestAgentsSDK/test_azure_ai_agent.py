#!/usr/bin/env python3
"""
Simple test script to verify agent-to-agent conversation setup
Run this to test your Azure AI Agent configuration before running the full test suite
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the testinglib directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from testinglib.azure_ai_agent_client import AzureAIAgentClient
from testinglib.config import AzureAIAgentSettings

async def test_azure_ai_agent():
    """Test Azure AI Agent configuration and basic functionality"""
    print("Testing Azure AI Agent Configuration...")
    
    try:
        # Load environment variables
        load_dotenv()
        
        # Initialize settings
        settings = AzureAIAgentSettings()
        print(f"Endpoint: {settings.endpoint}")
        print(f"Model: {settings.model}")
        print(f"API Key configured: {'Yes' if settings.api_key else 'No'}")
        
        # Initialize client
        client = AzureAIAgentClient(
            endpoint=settings.endpoint,
            model=settings.model,
            api_key=settings.api_key,
            system_prompt=settings.system_prompt
        )
        
        print("\nStarting test conversation...")
        
        # Test conversation start
        initial_message = await client.start_conversation(
            "Hello! I need information about industrial safety equipment."
        )
        
        print(f"✓ Azure AI Agent Response: {initial_message}")
        
        # Test conversation continuation
        follow_up = await client.continue_conversation(
            "We specialize in cut-resistant gloves and welding equipment. What specific type are you looking for?",
            2
        )
        
        print(f"✓ Azure AI Agent Follow-up: {follow_up}")
        
        # Get conversation history
        history = client.get_conversation_history()
        print(f"✓ Conversation has {len(history)} turns")
        
        print("\n✓ Azure AI Agent test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing Azure AI Agent: {str(e)}")
        return False

async def main():
    """Main test function"""
    print("=== Azure AI Agent Configuration Test ===\n")
    
    success = await test_azure_ai_agent()
    
    if success:
        print("\n🎉 Configuration test passed! You can now run the full test suite:")
        print("   pytest tests/multi_turn_with_agent --html=reports/agent_to_agent_conversation.html --self-contained-html")
    else:
        print("\n❌ Configuration test failed. Please check your .env file and credentials.")
        print("   Make sure you have GITHUB_TOKEN or AZURE_API_KEY configured properly.")

if __name__ == "__main__":
    asyncio.run(main())
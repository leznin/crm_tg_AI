#!/usr/bin/env python3
"""Test script for chat summary functionality."""

import asyncio
import httpx
import json
from datetime import datetime

async def test_chat_summary():
    """Test the chat summary API endpoint."""

    # Configuration
    base_url = "http://localhost:8000"
    test_user_id = 1  # Assuming test user exists
    test_chat_id = 1  # Assuming test chat exists

    print("Testing Chat Summary API...")
    print(f"Base URL: {base_url}")
    print(f"Chat ID: {test_chat_id}")

    # First, check if we can get chat messages
    try:
        async with httpx.AsyncClient() as client:
            # Get messages first to verify chat exists
            messages_url = f"{base_url}/api/v1/business-accounts/chats/{test_chat_id}/messages"
            print(f"\nChecking messages endpoint: {messages_url}")

            response = await client.get(messages_url, cookies={"session": "test_session"})
            print(f"Messages response status: {response.status_code}")

            if response.status_code == 200:
                messages_data = response.json()
                print(f"Found {len(messages_data['messages'])} messages in chat")

                # Now test summary endpoint
                summary_url = f"{base_url}/api/v1/business-accounts/chats/{test_chat_id}/summary"
                print(f"\nTesting summary endpoint: {summary_url}")

                response = await client.post(summary_url, cookies={"session": "test_session"})
                print(f"Summary response status: {response.status_code}")

                if response.status_code == 200:
                    summary_data = response.json()
                    print("Summary generated successfully!")
                    print(f"Summary: {summary_data.get('summary', 'N/A')}")
                    print(f"Key points: {len(summary_data.get('key_points', []))}")
                    print(f"Sentiment: {summary_data.get('sentiment', 'N/A')}")
                else:
                    print(f"Error response: {response.text}")
            else:
                print(f"Error getting messages: {response.text}")

    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_summary())

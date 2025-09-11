#!/usr/bin/env python3
"""
Script to clean up duplicate settings entries in the database.
This script will remove inactive/duplicate API keys, OpenRouter models, and prompts.
"""
import sys
import os

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.models.settings import ApiKey, OpenRouterModel, Prompt
from sqlalchemy import and_

def cleanup_duplicates():
    """Clean up duplicate settings entries."""
    db = SessionLocal()
    try:
        print("Starting cleanup of duplicate settings...")
        
        # Clean up inactive API keys
        inactive_api_keys = db.query(ApiKey).filter(ApiKey.is_active == False).all()
        api_count = len(inactive_api_keys)
        for key in inactive_api_keys:
            db.delete(key)
        
        # Clean up inactive OpenRouter models
        inactive_models = db.query(OpenRouterModel).filter(OpenRouterModel.is_active == False).all()
        model_count = len(inactive_models)
        for model in inactive_models:
            db.delete(model)
        
        # Clean up inactive prompts
        inactive_prompts = db.query(Prompt).filter(Prompt.is_active == False).all()
        prompt_count = len(inactive_prompts)
        for prompt in inactive_prompts:
            db.delete(prompt)
        
        db.commit()
        
        print(f"Cleanup completed:")
        print(f"  - Removed {api_count} inactive API keys")
        print(f"  - Removed {model_count} inactive OpenRouter models")
        print(f"  - Removed {prompt_count} inactive prompts")
        
        # Show remaining active records
        print("\nRemaining active records:")
        active_api_keys = db.query(ApiKey).filter(ApiKey.is_active == True).all()
        print(f"  - {len(active_api_keys)} active API keys")
        for key in active_api_keys:
            print(f"    * User {key.user_id}: {key.key_type}")
        
        active_models = db.query(OpenRouterModel).filter(OpenRouterModel.is_active == True).all()
        print(f"  - {len(active_models)} active OpenRouter models")
        for model in active_models:
            print(f"    * User {model.user_id}: {model.data_type} -> {model.model_name}")
        
        active_prompts = db.query(Prompt).filter(Prompt.is_active == True).all()
        print(f"  - {len(active_prompts)} active prompts")
        for prompt in active_prompts:
            print(f"    * User {prompt.user_id}: {prompt.prompt_type}")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()

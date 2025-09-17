#!/usr/bin/env python3
"""Check user settings in database."""

import sys
import os
sys.path.append('backend')

from app.db.session import SessionLocal
from app.models.settings import ApiKey, OpenRouterModel, Prompt

db = SessionLocal()
try:
    # Check API keys
    api_keys = db.query(ApiKey).filter(ApiKey.user_id == 1).all()
    print(f'Found {len(api_keys)} API keys for user 1')
    for key in api_keys:
        print(f'  {key.key_type}: {"*" * 20} (active: {key.is_active})')

    # Check models
    models = db.query(OpenRouterModel).filter(OpenRouterModel.user_id == 1).all()
    print(f'Found {len(models)} OpenRouter models for user 1')
    for model in models:
        print(f'  {model.data_type}: {model.model_name}')

    # Check prompts
    prompts = db.query(Prompt).filter(Prompt.user_id == 1).all()
    print(f'Found {len(prompts)} prompts for user 1')
    for prompt in prompts:
        print(f'  {prompt.prompt_type}: {prompt.content[:50]}...')

finally:
    db.close()

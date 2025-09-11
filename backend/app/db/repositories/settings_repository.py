"""Repositories for settings management."""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.settings import ApiKey, OpenRouterModel, Prompt
from app.schemas.settings_schema import (
    ApiKeyCreate, ApiKeyUpdate, KeyTypeEnum,
    OpenRouterModelCreate, OpenRouterModelUpdate, DataTypeEnum,
    PromptCreate, PromptUpdate, PromptTypeEnum
)


class ApiKeyRepository:
    """Repository for API key operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_key(self, user_id: int, api_key_data: ApiKeyCreate, encrypted_value: str) -> ApiKey:
        """Create or update an API key."""
        # Check if an existing active key of the same type exists
        existing_key = self.db.query(ApiKey).filter(
            and_(
                ApiKey.user_id == user_id,
                ApiKey.key_type == api_key_data.key_type,
                ApiKey.is_active == True
            )
        ).first()
        
        if existing_key:
            # Update existing key
            existing_key.encrypted_value = encrypted_value
            self.db.commit()
            self.db.refresh(existing_key)
            return existing_key
        else:
            # Create new key
            db_api_key = ApiKey(
                user_id=user_id,
                key_type=api_key_data.key_type,
                encrypted_value=encrypted_value,
                is_active=True
            )
            
            self.db.add(db_api_key)
            self.db.commit()
            self.db.refresh(db_api_key)
            return db_api_key
    
    def get_api_key_by_type(self, user_id: int, key_type: KeyTypeEnum) -> Optional[ApiKey]:
        """Get active API key by type for a user."""
        return self.db.query(ApiKey).filter(
            and_(
                ApiKey.user_id == user_id,
                ApiKey.key_type == key_type,
                ApiKey.is_active == True
            )
        ).first()
    
    def get_user_api_keys(self, user_id: int) -> List[ApiKey]:
        """Get all active API keys for a user."""
        return self.db.query(ApiKey).filter(
            and_(
                ApiKey.user_id == user_id,
                ApiKey.is_active == True
            )
        ).all()
    
    def update_api_key(self, api_key_id: int, user_id: int, update_data: ApiKeyUpdate, encrypted_value: Optional[str] = None) -> Optional[ApiKey]:
        """Update an API key."""
        db_api_key = self.db.query(ApiKey).filter(
            and_(
                ApiKey.id == api_key_id,
                ApiKey.user_id == user_id
            )
        ).first()
        
        if not db_api_key:
            return None
        
        if encrypted_value is not None:
            db_api_key.encrypted_value = encrypted_value
        
        if update_data.is_active is not None:
            db_api_key.is_active = update_data.is_active
        
        self.db.commit()
        self.db.refresh(db_api_key)
        return db_api_key
    
    def delete_api_key(self, api_key_id: int, user_id: int) -> bool:
        """Delete an API key."""
        db_api_key = self.db.query(ApiKey).filter(
            and_(
                ApiKey.id == api_key_id,
                ApiKey.user_id == user_id
            )
        ).first()
        
        if not db_api_key:
            return False
        
        self.db.delete(db_api_key)
        self.db.commit()
        return True
    
    def cleanup_inactive_api_keys(self, user_id: int) -> int:
        """Remove inactive API keys for a user."""
        inactive_keys = self.db.query(ApiKey).filter(
            and_(
                ApiKey.user_id == user_id,
                ApiKey.is_active == False
            )
        ).all()
        
        count = len(inactive_keys)
        for key in inactive_keys:
            self.db.delete(key)
        
        self.db.commit()
        return count


class OpenRouterModelRepository:
    """Repository for OpenRouter model operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_model(self, user_id: int, model_data: OpenRouterModelCreate) -> OpenRouterModel:
        """Create or update an OpenRouter model configuration."""
        # Check if an existing active model of the same data type exists
        existing_model = self.db.query(OpenRouterModel).filter(
            and_(
                OpenRouterModel.user_id == user_id,
                OpenRouterModel.data_type == model_data.data_type,
                OpenRouterModel.is_active == True
            )
        ).first()
        
        if existing_model:
            # Update existing model
            existing_model.model_name = model_data.model_name
            existing_model.model_configuration = model_data.model_configuration
            self.db.commit()
            self.db.refresh(existing_model)
            return existing_model
        else:
            # Create new model
            db_model = OpenRouterModel(
                user_id=user_id,
                data_type=model_data.data_type,
                model_name=model_data.model_name,
                model_configuration=model_data.model_configuration,
                is_active=True
            )
            
            self.db.add(db_model)
            self.db.commit()
            self.db.refresh(db_model)
            return db_model
    
    def get_model_by_data_type(self, user_id: int, data_type: DataTypeEnum) -> Optional[OpenRouterModel]:
        """Get active model by data type for a user."""
        return self.db.query(OpenRouterModel).filter(
            and_(
                OpenRouterModel.user_id == user_id,
                OpenRouterModel.data_type == data_type,
                OpenRouterModel.is_active == True
            )
        ).first()
    
    def get_user_models(self, user_id: int) -> List[OpenRouterModel]:
        """Get all active models for a user."""
        return self.db.query(OpenRouterModel).filter(
            and_(
                OpenRouterModel.user_id == user_id,
                OpenRouterModel.is_active == True
            )
        ).all()
    
    def update_model(self, model_id: int, user_id: int, update_data: OpenRouterModelUpdate) -> Optional[OpenRouterModel]:
        """Update an OpenRouter model."""
        db_model = self.db.query(OpenRouterModel).filter(
            and_(
                OpenRouterModel.id == model_id,
                OpenRouterModel.user_id == user_id
            )
        ).first()
        
        if not db_model:
            return None
        
        if update_data.model_name is not None:
            db_model.model_name = update_data.model_name
        
        if update_data.model_configuration is not None:
            db_model.model_configuration = update_data.model_configuration
        
        if update_data.is_active is not None:
            db_model.is_active = update_data.is_active
        
        self.db.commit()
        self.db.refresh(db_model)
        return db_model
    
    def delete_model(self, model_id: int, user_id: int) -> bool:
        """Delete an OpenRouter model."""
        db_model = self.db.query(OpenRouterModel).filter(
            and_(
                OpenRouterModel.id == model_id,
                OpenRouterModel.user_id == user_id
            )
        ).first()
        
        if not db_model:
            return False
        
        self.db.delete(db_model)
        self.db.commit()
        return True


class PromptRepository:
    """Repository for prompt operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_prompt(self, user_id: int, prompt_data: PromptCreate) -> Prompt:
        """Create or update a prompt."""
        # Check if an existing active prompt of the same type exists
        existing_prompt = self.db.query(Prompt).filter(
            and_(
                Prompt.user_id == user_id,
                Prompt.prompt_type == prompt_data.prompt_type,
                Prompt.is_active == True
            )
        ).first()
        
        if existing_prompt:
            # Update existing prompt
            existing_prompt.content = prompt_data.content
            self.db.commit()
            self.db.refresh(existing_prompt)
            return existing_prompt
        else:
            # Create new prompt
            db_prompt = Prompt(
                user_id=user_id,
                prompt_type=prompt_data.prompt_type,
                content=prompt_data.content,
                is_active=True
            )
            
            self.db.add(db_prompt)
            self.db.commit()
            self.db.refresh(db_prompt)
            return db_prompt
    
    def get_prompt_by_type(self, user_id: int, prompt_type: PromptTypeEnum) -> Optional[Prompt]:
        """Get active prompt by type for a user."""
        return self.db.query(Prompt).filter(
            and_(
                Prompt.user_id == user_id,
                Prompt.prompt_type == prompt_type,
                Prompt.is_active == True
            )
        ).first()
    
    def get_user_prompts(self, user_id: int) -> List[Prompt]:
        """Get all active prompts for a user."""
        return self.db.query(Prompt).filter(
            and_(
                Prompt.user_id == user_id,
                Prompt.is_active == True
            )
        ).all()
    
    def update_prompt(self, prompt_id: int, user_id: int, update_data: PromptUpdate) -> Optional[Prompt]:
        """Update a prompt."""
        db_prompt = self.db.query(Prompt).filter(
            and_(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
        ).first()
        
        if not db_prompt:
            return None
        
        if update_data.content is not None:
            db_prompt.content = update_data.content
        
        if update_data.is_active is not None:
            db_prompt.is_active = update_data.is_active
        
        self.db.commit()
        self.db.refresh(db_prompt)
        return db_prompt
    
    def delete_prompt(self, prompt_id: int, user_id: int) -> bool:
        """Delete a prompt."""
        db_prompt = self.db.query(Prompt).filter(
            and_(
                Prompt.id == prompt_id,
                Prompt.user_id == user_id
            )
        ).first()
        
        if not db_prompt:
            return False
        
        self.db.delete(db_prompt)
        self.db.commit()
        return True

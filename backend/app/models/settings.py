"""Settings models for storing API keys, OpenRouter models, and prompts."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ApiKey(Base):
    """Model for storing encrypted API keys."""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    key_type = Column(String(50), nullable=False)  # 'telegram_bot', 'openrouter'
    encrypted_value = Column(Text, nullable=False)  # Encrypted API key
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, user_id={self.user_id}, key_type='{self.key_type}')>"


class OpenRouterModel(Base):
    """Model for storing OpenRouter model configurations."""
    __tablename__ = 'openrouter_models'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    data_type = Column(String(20), nullable=False)  # 'text', 'image', 'image_vision', 'image_generation', 'audio'
    model_name = Column(String(100), nullable=False)  # e.g., 'gpt-4', 'claude-3'
    model_configuration = Column(JSON, nullable=True)  # Additional model settings
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="openrouter_models")
    
    def __repr__(self):
        return f"<OpenRouterModel(id={self.id}, data_type='{self.data_type}', model='{self.model_name}')>"


class Prompt(Base):
    """Model for storing AI prompts."""
    __tablename__ = 'prompts'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    prompt_type = Column(String(50), nullable=False)  # 'summary', 'suggestions', 'analysis'
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="prompts")
    
    def __repr__(self):
        return f"<Prompt(id={self.id}, user_id={self.user_id}, type='{self.prompt_type}')>"

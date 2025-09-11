"""Schemas for settings management."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class KeyTypeEnum(str, Enum):
    """Enum for API key types."""
    TELEGRAM_BOT = "telegram_bot"
    OPENROUTER = "openrouter"


class DataTypeEnum(str, Enum):
    """Enum for OpenRouter model data types."""
    TEXT = "text"
    IMAGE = "image"
    IMAGE_VISION = "image_vision"
    IMAGE_GENERATION = "image_generation"
    AUDIO = "audio"


class PromptTypeEnum(str, Enum):
    """Enum for prompt types."""
    SUMMARY = "summary"
    SUGGESTIONS = "suggestions"
    ANALYSIS = "analysis"


# API Key schemas
class ApiKeyCreate(BaseModel):
    """Schema for creating API key."""
    key_type: KeyTypeEnum
    value: str = Field(..., min_length=1, max_length=1000)
    
    @validator('value')
    def validate_value(cls, v):
        if not v.strip():
            raise ValueError('API key value cannot be empty')
        return v.strip()


class ApiKeyUpdate(BaseModel):
    """Schema for updating API key."""
    value: Optional[str] = Field(None, min_length=1, max_length=1000)
    is_active: Optional[bool] = None
    
    @validator('value')
    def validate_value(cls, v):
        if v is not None and not v.strip():
            raise ValueError('API key value cannot be empty')
        return v.strip() if v else v


class ApiKeyResponse(BaseModel):
    """Schema for API key response (without actual key value)."""
    id: int
    key_type: KeyTypeEnum
    masked_value: str  # Masked version like "sk-ab***cd"
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# OpenRouter Model schemas
class OpenRouterModelCreate(BaseModel):
    """Schema for creating OpenRouter model configuration."""
    data_type: DataTypeEnum
    model_name: str = Field(..., min_length=1, max_length=100)
    model_configuration: Optional[Dict[str, Any]] = None
    
    @validator('model_name')
    def validate_model_name(cls, v):
        if not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip()


class OpenRouterModelUpdate(BaseModel):
    """Schema for updating OpenRouter model configuration."""
    model_name: Optional[str] = Field(None, min_length=1, max_length=100)
    model_configuration: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    
    @validator('model_name')
    def validate_model_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip() if v else v


class OpenRouterModelResponse(BaseModel):
    """Schema for OpenRouter model response."""
    id: int
    data_type: DataTypeEnum
    model_name: str
    model_configuration: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Prompt schemas
class PromptCreate(BaseModel):
    """Schema for creating prompt."""
    prompt_type: PromptTypeEnum
    content: str = Field(..., min_length=1, max_length=5000)
    
    @validator('content')
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError('Prompt content cannot be empty')
        return v.strip()


class PromptUpdate(BaseModel):
    """Schema for updating prompt."""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    is_active: Optional[bool] = None
    
    @validator('content')
    def validate_content(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Prompt content cannot be empty')
        return v.strip() if v else v


class PromptResponse(BaseModel):
    """Schema for prompt response."""
    id: int
    prompt_type: PromptTypeEnum
    content: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Combined settings schemas
class SettingsResponse(BaseModel):
    """Combined settings response."""
    api_keys: List[ApiKeyResponse]
    openrouter_models: List[OpenRouterModelResponse]
    prompts: List[PromptResponse]


class ApiConfigUpdate(BaseModel):
    """Schema for updating API configuration (frontend compatibility)."""
    telegram_bot_token: Optional[str] = None
    openrouter_api_key: Optional[str] = None


class PromptsUpdate(BaseModel):
    """Schema for updating prompts (frontend compatibility)."""
    summary: Optional[str] = None
    suggestions: Optional[str] = None
    analysis: Optional[str] = None


class OpenRouterModelsUpdate(BaseModel):
    """Schema for updating OpenRouter models configuration."""
    text_model: Optional[str] = None
    text_config: Optional[Dict[str, Any]] = None
    image_model: Optional[str] = None
    image_config: Optional[Dict[str, Any]] = None
    image_vision_model: Optional[str] = None
    image_vision_config: Optional[Dict[str, Any]] = None
    image_generation_model: Optional[str] = None
    image_generation_config: Optional[Dict[str, Any]] = None
    audio_model: Optional[str] = None
    audio_config: Optional[Dict[str, Any]] = None


# OpenRouter API response schemas
class OpenRouterModelInfo(BaseModel):
    """Schema for OpenRouter model information."""
    id: str
    name: str
    description: Optional[str] = None
    context_length: int
    pricing: Dict[str, Any]
    provider: str  # Changed from Dict[str, Any] to str to match actual API response
    capabilities: List[str]
    input_modalities: List[str] = []  # New field for input modalities
    output_modalities: List[str] = []  # New field for output modalities


class OpenRouterAvailableModelsResponse(BaseModel):
    """Schema for available OpenRouter models response."""
    text: List[OpenRouterModelInfo]
    image_vision: List[OpenRouterModelInfo]
    image_generation: List[OpenRouterModelInfo]
    audio: List[OpenRouterModelInfo]  # Модели транскрипции аудио (audio -> text)
    text_to_speech: List[OpenRouterModelInfo] = []  # Модели синтеза речи (text -> audio)
    multimodal: List[OpenRouterModelInfo] = []  # Сложные мультимодальные модели


class OpenRouterBalanceResponse(BaseModel):
    """Schema for OpenRouter balance response."""
    balance: float
    usage: float
    limit: Optional[float] = None
    formatted_balance: str
    formatted_usage: str
    rate_limit: Dict[str, Any]

"""Settings API router."""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.settings_service import SettingsService
from app.schemas.settings_schema import (
    SettingsResponse, ApiConfigUpdate, PromptsUpdate, OpenRouterModelsUpdate,
    ApiKeyCreate, ApiKeyResponse, OpenRouterModelCreate, OpenRouterModelResponse,
    PromptCreate, PromptResponse, KeyTypeEnum, OpenRouterAvailableModelsResponse,
    OpenRouterBalanceResponse
)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("/", response_model=SettingsResponse)
async def get_all_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all settings for the current user."""
    settings_service = SettingsService(db)
    return settings_service.get_all_settings(current_user.id)


@router.get("/api-config")
async def get_api_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get API configuration (frontend compatibility)."""
    settings_service = SettingsService(db)
    return settings_service.get_api_config_for_frontend(current_user.id)


@router.post("/api-config")
async def update_api_config(
    config: ApiConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update API configuration (frontend compatibility)."""
    settings_service = SettingsService(db)
    return settings_service.update_api_config(current_user.id, config)


@router.get("/prompts")
async def get_prompts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Get prompts (frontend compatibility)."""
    settings_service = SettingsService(db)
    return settings_service.get_prompts_for_frontend(current_user.id)


@router.post("/prompts")
async def update_prompts(
    prompts: PromptsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update prompts (frontend compatibility)."""
    settings_service = SettingsService(db)
    return settings_service.update_prompts(current_user.id, prompts)


@router.post("/openrouter-models")
async def update_openrouter_models(
    models: OpenRouterModelsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Update OpenRouter models configuration."""
    settings_service = SettingsService(db)
    return settings_service.update_openrouter_models(current_user.id, models)


@router.get("/openrouter-models", response_model=list[OpenRouterModelResponse])
async def get_openrouter_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get OpenRouter models configuration."""
    settings_service = SettingsService(db)
    return settings_service.get_user_models(current_user.id)


# Individual API key endpoints
@router.post("/api-keys", response_model=ApiKeyResponse)
async def create_api_key(
    api_key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update an API key."""
    settings_service = SettingsService(db)
    return settings_service.create_or_update_api_key(
        current_user.id, api_key_data.key_type, api_key_data.value
    )


@router.get("/api-keys", response_model=list[ApiKeyResponse])
async def get_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all API keys for the current user."""
    settings_service = SettingsService(db)
    return settings_service.get_user_api_keys(current_user.id)


# Individual OpenRouter model endpoints
@router.post("/models", response_model=OpenRouterModelResponse)
async def create_openrouter_model(
    model_data: OpenRouterModelCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update an OpenRouter model configuration."""
    settings_service = SettingsService(db)
    return settings_service.create_or_update_model(
        current_user.id, model_data.data_type, model_data.model_name, model_data.model_configuration
    )


@router.get("/models", response_model=list[OpenRouterModelResponse])
async def get_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all OpenRouter models for the current user."""
    settings_service = SettingsService(db)
    return settings_service.get_user_models(current_user.id)


# Individual prompt endpoints
@router.post("/prompts/create", response_model=PromptResponse)
async def create_prompt(
    prompt_data: PromptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update a prompt."""
    settings_service = SettingsService(db)
    return settings_service.create_or_update_prompt(
        current_user.id, prompt_data.prompt_type, prompt_data.content
    )


@router.get("/prompts/list", response_model=list[PromptResponse])
async def get_prompts_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all prompts for the current user."""
    settings_service = SettingsService(db)
    return settings_service.get_user_prompts(current_user.id)


# Test connection endpoint
@router.post("/test-connection")
async def test_api_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test API connections."""
    settings_service = SettingsService(db)
    
    # Get API keys
    telegram_key = settings_service.get_api_key(current_user.id, KeyTypeEnum.TELEGRAM_BOT, decrypt=True)
    openrouter_key = settings_service.get_api_key(current_user.id, KeyTypeEnum.OPENROUTER, decrypt=True)
    
    results = {
        "telegram_bot": {"status": "not_configured", "message": "API key not found"},
        "openrouter": {"status": "not_configured", "message": "API key not found"}
    }
    
    # Simple validation (in a real implementation, you'd test actual API calls)
    if telegram_key:
        if len(telegram_key) > 10 and ":" in telegram_key:
            results["telegram_bot"] = {"status": "success", "message": "API key format is valid"}
        else:
            results["telegram_bot"] = {"status": "error", "message": "Invalid API key format"}
    
    if openrouter_key:
        if len(openrouter_key) > 10:
            results["openrouter"] = {"status": "success", "message": "API key format is valid"}
        else:
            results["openrouter"] = {"status": "error", "message": "Invalid API key format"}
    
    return results


# OpenRouter API endpoints
@router.get("/openrouter/models", response_model=OpenRouterAvailableModelsResponse)
async def get_available_openrouter_models(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available OpenRouter models grouped by capability."""
    settings_service = SettingsService(db)
    return await settings_service.get_available_openrouter_models(current_user.id)


@router.get("/openrouter/balance", response_model=OpenRouterBalanceResponse)
async def get_openrouter_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get OpenRouter account balance and usage information."""
    settings_service = SettingsService(db)
    return await settings_service.get_openrouter_balance(current_user.id)


@router.post("/openrouter/test-connection")
async def test_openrouter_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Test OpenRouter API connection."""
    settings_service = SettingsService(db)
    success, message = await settings_service.test_openrouter_connection(current_user.id)
    
    return {
        "success": success,
        "message": message,
        "status": "success" if success else "error"
    }

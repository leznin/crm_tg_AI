"""Settings service for managing API keys, OpenRouter models, and prompts."""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.repositories.settings_repository import (
    ApiKeyRepository, OpenRouterModelRepository, PromptRepository
)
from app.schemas.settings_schema import (
    ApiKeyCreate, ApiKeyUpdate, ApiKeyResponse,
    OpenRouterModelCreate, OpenRouterModelUpdate, OpenRouterModelResponse,
    PromptCreate, PromptUpdate, PromptResponse,
    SettingsResponse, ApiConfigUpdate, PromptsUpdate, OpenRouterModelsUpdate,
    KeyTypeEnum, DataTypeEnum, PromptTypeEnum, OpenRouterAvailableModelsResponse,
    OpenRouterBalanceResponse, OpenRouterModelInfo
)
from app.utils.encryption import encrypt_sensitive_data, decrypt_sensitive_data, mask_api_key
from app.services.openrouter_service import OpenRouterModelManager

# Configure logging
logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing user settings."""
    
    def __init__(self, db: Session):
        self.db = db
        self.api_key_repo = ApiKeyRepository(db)
        self.model_repo = OpenRouterModelRepository(db)
        self.prompt_repo = PromptRepository(db)
    
    # API Key methods
    def create_or_update_api_key(self, user_id: int, key_type: KeyTypeEnum, value: str) -> ApiKeyResponse:
        """Create or update an API key."""
        try:
            # Encrypt the API key
            encrypted_value = encrypt_sensitive_data(value)
            
            # Create the API key (this will deactivate existing ones of the same type)
            api_key_data = ApiKeyCreate(key_type=key_type, value=value)
            db_api_key = self.api_key_repo.create_api_key(user_id, api_key_data, encrypted_value)
            
            # Return response with masked value
            return ApiKeyResponse(
                id=db_api_key.id,
                key_type=db_api_key.key_type,
                masked_value=mask_api_key(value),
                is_active=db_api_key.is_active,
                created_at=db_api_key.created_at,
                updated_at=db_api_key.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating/updating API key for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save API key"
            )
    
    def get_api_key(self, user_id: int, key_type: KeyTypeEnum, decrypt: bool = False) -> Optional[str]:
        """Get API key value (decrypted if requested)."""
        db_api_key = self.api_key_repo.get_api_key_by_type(user_id, key_type)
        if not db_api_key:
            return None
        
        if decrypt:
            return decrypt_sensitive_data(db_api_key.encrypted_value)
        else:
            return mask_api_key(decrypt_sensitive_data(db_api_key.encrypted_value))
    
    def get_user_api_keys(self, user_id: int) -> List[ApiKeyResponse]:
        """Get all API keys for a user (with masked values)."""
        db_api_keys = self.api_key_repo.get_user_api_keys(user_id)
        
        responses = []
        for db_api_key in db_api_keys:
            decrypted_value = decrypt_sensitive_data(db_api_key.encrypted_value)
            responses.append(ApiKeyResponse(
                id=db_api_key.id,
                key_type=db_api_key.key_type,
                masked_value=mask_api_key(decrypted_value),
                is_active=db_api_key.is_active,
                created_at=db_api_key.created_at,
                updated_at=db_api_key.updated_at
            ))
        
        return responses
    
    # OpenRouter Model methods
    def create_or_update_model(self, user_id: int, data_type: DataTypeEnum, model_name: str, 
                              model_config: Optional[Dict[str, Any]] = None) -> OpenRouterModelResponse:
        """Create or update an OpenRouter model configuration."""
        try:
            model_data = OpenRouterModelCreate(
                data_type=data_type,
                model_name=model_name,
                model_configuration=model_config
            )
            db_model = self.model_repo.create_model(user_id, model_data)
            
            return OpenRouterModelResponse(
                id=db_model.id,
                data_type=db_model.data_type,
                model_name=db_model.model_name,
                model_configuration=db_model.model_configuration,
                is_active=db_model.is_active,
                created_at=db_model.created_at,
                updated_at=db_model.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating/updating OpenRouter model for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save OpenRouter model configuration"
            )
    
    def get_user_models(self, user_id: int) -> List[OpenRouterModelResponse]:
        """Get all OpenRouter models for a user."""
        db_models = self.model_repo.get_user_models(user_id)
        
        return [OpenRouterModelResponse(
            id=db_model.id,
            data_type=db_model.data_type,
            model_name=db_model.model_name,
            model_configuration=db_model.model_configuration,
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at
        ) for db_model in db_models]
    
    def get_model_by_data_type(self, user_id: int, data_type: DataTypeEnum) -> Optional[OpenRouterModelResponse]:
        """Get OpenRouter model by data type."""
        db_model = self.model_repo.get_model_by_data_type(user_id, data_type)
        if not db_model:
            return None
        
        return OpenRouterModelResponse(
            id=db_model.id,
            data_type=db_model.data_type,
            model_name=db_model.model_name,
            model_configuration=db_model.model_configuration,
            is_active=db_model.is_active,
            created_at=db_model.created_at,
            updated_at=db_model.updated_at
        )
    
    # Prompt methods
    def create_or_update_prompt(self, user_id: int, prompt_type: PromptTypeEnum, content: str) -> PromptResponse:
        """Create or update a prompt."""
        try:
            prompt_data = PromptCreate(prompt_type=prompt_type, content=content)
            db_prompt = self.prompt_repo.create_prompt(user_id, prompt_data)
            
            return PromptResponse(
                id=db_prompt.id,
                prompt_type=db_prompt.prompt_type,
                content=db_prompt.content,
                is_active=db_prompt.is_active,
                created_at=db_prompt.created_at,
                updated_at=db_prompt.updated_at
            )
        except Exception as e:
            logger.error(f"Error creating/updating prompt for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save prompt"
            )
    
    def get_user_prompts(self, user_id: int) -> List[PromptResponse]:
        """Get all prompts for a user."""
        db_prompts = self.prompt_repo.get_user_prompts(user_id)
        
        return [PromptResponse(
            id=db_prompt.id,
            prompt_type=db_prompt.prompt_type,
            content=db_prompt.content,
            is_active=db_prompt.is_active,
            created_at=db_prompt.created_at,
            updated_at=db_prompt.updated_at
        ) for db_prompt in db_prompts]
    
    def get_prompt_by_type(self, user_id: int, prompt_type: PromptTypeEnum) -> Optional[str]:
        """Get prompt content by type."""
        db_prompt = self.prompt_repo.get_prompt_by_type(user_id, prompt_type)
        return db_prompt.content if db_prompt else None
    
    # Combined methods for frontend compatibility
    def get_all_settings(self, user_id: int) -> SettingsResponse:
        """Get all settings for a user."""
        return SettingsResponse(
            api_keys=self.get_user_api_keys(user_id),
            openrouter_models=self.get_user_models(user_id),
            prompts=self.get_user_prompts(user_id)
        )
    
    def update_api_config(self, user_id: int, config: ApiConfigUpdate) -> Dict[str, str]:
        """Update API configuration (frontend compatibility)."""
        results = {}
        
        if config.telegram_bot_token:
            api_key = self.create_or_update_api_key(
                user_id, KeyTypeEnum.TELEGRAM_BOT, config.telegram_bot_token
            )
            results['telegram_bot_token'] = api_key.masked_value
        
        if config.openrouter_api_key:
            api_key = self.create_or_update_api_key(
                user_id, KeyTypeEnum.OPENROUTER, config.openrouter_api_key
            )
            results['openrouter_api_key'] = api_key.masked_value
        
        return results
    
    def update_prompts(self, user_id: int, prompts: PromptsUpdate) -> Dict[str, str]:
        """Update prompts (frontend compatibility)."""
        results = {}
        
        if prompts.summary:
            prompt = self.create_or_update_prompt(
                user_id, PromptTypeEnum.SUMMARY, prompts.summary
            )
            results['summary'] = 'updated'
        
        if prompts.suggestions:
            prompt = self.create_or_update_prompt(
                user_id, PromptTypeEnum.SUGGESTIONS, prompts.suggestions
            )
            results['suggestions'] = 'updated'
        
        if prompts.analysis:
            prompt = self.create_or_update_prompt(
                user_id, PromptTypeEnum.ANALYSIS, prompts.analysis
            )
            results['analysis'] = 'updated'
        
        return results
    
    def update_openrouter_models(self, user_id: int, models: OpenRouterModelsUpdate) -> Dict[str, str]:
        """Update OpenRouter models configuration."""
        results = {}

        if models.text_model:
            model = self.create_or_update_model(
                user_id, DataTypeEnum.TEXT, models.text_model, models.text_config
            )
            results['text_model'] = 'updated'

        if models.image_model:
            model = self.create_or_update_model(
                user_id, DataTypeEnum.IMAGE, models.image_model, models.image_config
            )
            results['image_model'] = 'updated'

        if models.image_vision_model:
            model = self.create_or_update_model(
                user_id, DataTypeEnum.IMAGE_VISION, models.image_vision_model, models.image_vision_config
            )
            results['image_vision_model'] = 'updated'

        if models.image_generation_model:
            model = self.create_or_update_model(
                user_id, DataTypeEnum.IMAGE_GENERATION, models.image_generation_model, models.image_generation_config
            )
            results['image_generation_model'] = 'updated'

        if models.audio_model:
            model = self.create_or_update_model(
                user_id, DataTypeEnum.AUDIO, models.audio_model, models.audio_config
            )
            results['audio_model'] = 'updated'

        return results
    
    def get_api_config_for_frontend(self, user_id: int) -> Dict[str, Optional[str]]:
        """Get API configuration in frontend format."""
        telegram_key = self.get_api_key(user_id, KeyTypeEnum.TELEGRAM_BOT, decrypt=False)
        openrouter_key = self.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=False)
        
        return {
            'telegram_bot_token': telegram_key,
            'openrouter_api_key': openrouter_key
        }
    
    def get_prompts_for_frontend(self, user_id: int) -> Dict[str, str]:
        """Get prompts in frontend format."""
        summary = self.get_prompt_by_type(user_id, PromptTypeEnum.SUMMARY)
        suggestions = self.get_prompt_by_type(user_id, PromptTypeEnum.SUGGESTIONS)
        analysis = self.get_prompt_by_type(user_id, PromptTypeEnum.ANALYSIS)
        
        # Default prompts if none exist
        default_prompts = {
            'summary': """Проанализируй этот диалог и создай краткое, но информативное резюме.

Требования к резюме:
- Пиши на русском языке
- Будь кратким, но содержательным (3-5 предложений)
- Выдели основные темы и цели разговора
- Укажи достигнутые договоренности или решения
- Опиши общий тон общения

Извлеки ключевые моменты:
- Важные решения, договоренности или обещания
- Конкретные даты, сроки, суммы
- Запросы информации или помощи
- Выраженные мнения или предпочтения

Определи настроение диалога:
- positive: дружелюбный, продуктивный, позитивный разговор
- negative: конфликтный, негативный, раздраженный тон
- neutral: деловой, нейтральный, информационный обмен""",
            'suggestions': """Проанализируй историю чата и предложи 3-4 варианта ответа от лица бизнес-аккаунта.

В истории чата:
- "Вы (бизнес-аккаунт)" - это ваши предыдущие сообщения
- Имена клиентов - это входящие сообщения от клиентов

Требования к ответам:
- Пиши на русском языке
- Будь кратким и по существу
- Учитывай контекст и предыдущие сообщения
- Предлагай профессиональные и уместные варианты ответа
- Каждый ответ должен быть естественным продолжением разговора

Учитывай роль бизнес-аккаунта и специфику общения с клиентами.""",
            'analysis': 'Проанализируй настроение собеседника и дай рекомендации по дальнейшему общению.'
        }
        
        return {
            'summary': summary or default_prompts['summary'],
            'suggestions': suggestions or default_prompts['suggestions'],
            'analysis': analysis or default_prompts['analysis']
        }
    
    # OpenRouter API methods
    async def get_available_openrouter_models(self, user_id: int) -> OpenRouterAvailableModelsResponse:
        """Get available OpenRouter models grouped by capability."""
        # Get OpenRouter API key
        openrouter_key = self.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
        if not openrouter_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenRouter API key not configured"
            )
        
        try:
            manager = OpenRouterModelManager(openrouter_key)
            models_data = await manager.get_available_models_by_type()
            await manager.close()
            
            # Convert to schema format - обрабатываем все новые группы
            def create_model_info(model):
                return OpenRouterModelInfo(
                    id=model["id"],
                    name=model["name"],
                    description=model.get("description"),
                    context_length=model["context_length"],
                    pricing=model["pricing"],
                    provider=model["provider"],
                    capabilities=model.get("capabilities", []),  # Теперь может быть пустым
                    input_modalities=model.get("input_modalities", []),
                    output_modalities=model.get("output_modalities", [])
                )
            
            response_data = {
                "text": [create_model_info(model) for model in models_data.get("text", [])],
                "image_vision": [create_model_info(model) for model in models_data.get("image_vision", [])],
                "image_generation": [create_model_info(model) for model in models_data.get("image_generation", [])],
                "audio": [create_model_info(model) for model in models_data.get("audio", [])],
                "text_to_speech": [create_model_info(model) for model in models_data.get("text_to_speech", [])],
                "multimodal": [create_model_info(model) for model in models_data.get("multimodal", [])]
            }
            
            return OpenRouterAvailableModelsResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Error getting OpenRouter models for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get OpenRouter models: {str(e)}"
            )
    
    async def get_openrouter_balance(self, user_id: int) -> OpenRouterBalanceResponse:
        """Get OpenRouter account balance and usage information."""
        logger.info(f"Getting OpenRouter balance for user {user_id}")

        # Get OpenRouter API key
        openrouter_key = self.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
        logger.info(f"OpenRouter API key found: {bool(openrouter_key)}")

        if not openrouter_key:
            logger.warning(f"No OpenRouter API key configured for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenRouter API key not configured"
            )

        try:
            logger.info("Creating OpenRouterModelManager")
            manager = OpenRouterModelManager(openrouter_key)
            logger.info("Calling manager.get_account_info()")
            balance_data = await manager.get_account_info()
            logger.info(f"Balance data received: {balance_data}")
            await manager.close()

            logger.info("Creating OpenRouterBalanceResponse")
            return OpenRouterBalanceResponse(
                balance=balance_data["balance"],
                usage=balance_data["usage"],
                limit=balance_data.get("limit"),
                formatted_balance=balance_data["formatted_balance"],
                formatted_usage=balance_data["formatted_usage"],
                rate_limit=balance_data["rate_limit"]
            )

        except Exception as e:
            logger.error(f"Error getting OpenRouter balance for user {user_id}: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")

            # Return placeholder data instead of raising error
            logger.warning("OpenRouter balance API is not accessible - likely requires paid plan")
            logger.info("To check your actual balance, visit: https://openrouter.ai/")

            return OpenRouterBalanceResponse(
                balance=0.0,
                usage=0.0,
                limit=None,
                formatted_balance="$0.00",
                formatted_usage="$0.00",
                rate_limit={}
            )
    
    async def test_openrouter_connection(self, user_id: int) -> tuple[bool, str]:
        """Test OpenRouter API connection."""
        # Get OpenRouter API key
        openrouter_key = self.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
        if not openrouter_key:
            return False, "OpenRouter API key not configured"
        
        try:
            manager = OpenRouterModelManager(openrouter_key)
            service = await manager.get_service()
            success, message = await service.test_connection()
            await manager.close()
            
            return success, message
            
        except Exception as e:
            logger.error(f"Error testing OpenRouter connection for user {user_id}: {e}")
            return False, f"Connection test failed: {str(e)}"

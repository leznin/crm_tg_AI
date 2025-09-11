"""OpenRouter API service for managing AI models and interactions."""
import logging
import httpx
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """Enum for model capabilities."""
    TEXT = "text"
    IMAGE_VISION = "image_vision"  # Модели для анализа изображений
    IMAGE_GENERATION = "image_generation"  # Модели для генерации изображений
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


@dataclass
class OpenRouterModel:
    """Data class for OpenRouter model information."""
    id: str
    name: str
    description: Optional[str]
    pricing: Dict[str, Any]
    context_length: int
    architecture: Dict[str, Any]
    top_provider: Dict[str, Any]
    per_request_limits: Optional[Dict[str, Any]]
    capabilities: List[str]
    input_modalities: List[str] = None  # New field for input modalities
    output_modalities: List[str] = None  # New field for output modalities

    def __post_init__(self):
        """Initialize output_modalities as empty list if None."""
        if self.input_modalities is None:
            self.input_modalities = []
        if self.output_modalities is None:
            self.output_modalities = []

    # Новая логика классификации моделей согласно OpenRouter документации
    
    @property
    def is_text_model(self) -> bool:
        """Text-only models: input text -> output text."""
        return (
            "text" in self.input_modalities and
            "text" in self.output_modalities and
            len(self.input_modalities) == 1  # Only text input
        )
    
    @property 
    def is_vision_model(self) -> bool:
        """Vision models: input text+image -> output text."""
        return (
            "text" in self.input_modalities and
            "image" in self.input_modalities and
            "text" in self.output_modalities
        )
    
    @property
    def is_image_generation_model(self) -> bool:
        """Image generation models: input text -> output image."""
        return (
            "text" in self.input_modalities and
            "image" in self.output_modalities
        )
    
    @property
    def is_audio_to_text_model(self) -> bool:
        """Audio transcription models: input audio -> output text."""
        return (
            "audio" in self.input_modalities and
            "text" in self.output_modalities
        )
    
    @property
    def is_text_to_audio_model(self) -> bool:
        """Text-to-speech models: input text -> output audio."""
        return (
            "text" in self.input_modalities and
            "audio" in self.output_modalities
        )
    
    def get_model_category(self) -> str:
        """Определяет основную категорию модели по её модальностям."""
        # Приоритет определения категорий
        if self.is_audio_to_text_model:
            return "audio_transcription"
        elif self.is_text_to_audio_model:
            return "text_to_speech"  
        elif self.is_image_generation_model:
            return "image_generation"
        elif self.is_vision_model:
            return "vision"
        elif self.is_text_model:
            return "text"
        else:
            # Для моделей с нестандартными комбинациями модальностей
            return "multimodal"


@dataclass
class OpenRouterBalance:
    """Data class for OpenRouter account balance."""
    balance: float
    usage: float
    limit: Optional[float]
    rate_limit: Dict[str, Any]


class OpenRouterAPIError(Exception):
    """Custom exception for OpenRouter API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str):
        """Initialize OpenRouter service with API key.
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://your-app.com",  # Required by OpenRouter
                "X-Title": "CRM TG Project"  # Optional but recommended
            },
            timeout=30.0
        )
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to OpenRouter API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx request
            
        Returns:
            Response data as dictionary
            
        Raises:
            OpenRouterAPIError: If API request fails
        """
        try:
            response = await self.client.request(method, endpoint, **kwargs)
            
            # Log request details for debugging
            logger.debug(f"OpenRouter API {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 401:
                raise OpenRouterAPIError(
                    "Invalid API key or unauthorized access",
                    status_code=response.status_code
                )
            elif response.status_code == 429:
                raise OpenRouterAPIError(
                    "Rate limit exceeded. Please try again later.",
                    status_code=response.status_code
                )
            elif response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                
                raise OpenRouterAPIError(
                    f"API request failed: {response.status_code}",
                    status_code=response.status_code,
                    response_data=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"OpenRouter API request error: {e}")
            raise OpenRouterAPIError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenRouter API request: {e}")
            raise OpenRouterAPIError(f"Unexpected error: {str(e)}")
    
    async def get_models(self) -> List[OpenRouterModel]:
        """Get list of available models from OpenRouter.

        Returns:
            List of OpenRouterModel objects

        Raises:
            OpenRouterAPIError: If API request fails
        """
        try:
            data = await self._make_request("GET", "/models")

            models = []
            for model_data in data.get("data", []):
                try:
                    # Извлекаем модальности из OpenRouter API
                    input_modalities = model_data.get("input_modalities", [])
                    output_modalities = model_data.get("output_modalities", [])
                    arch = model_data.get("architecture", {})
                    
                    # ВАЖНО: Проверяем модальности в architecture - там может быть более точная информация
                    arch_input_modalities = arch.get("input_modalities", [])
                    arch_output_modalities = arch.get("output_modalities", [])
                    
                    # Используем модальности из architecture если они есть и более подробные
                    if arch_input_modalities and len(arch_input_modalities) > len(input_modalities):
                        input_modalities = arch_input_modalities
                        logger.debug(f"Using input_modalities from architecture for {model_data.get('id', 'unknown')}: {arch_input_modalities}")
                    
                    if arch_output_modalities and len(arch_output_modalities) > len(output_modalities):
                        output_modalities = arch_output_modalities
                        logger.debug(f"Using output_modalities from architecture for {model_data.get('id', 'unknown')}: {arch_output_modalities}")
                    
                    # Если модальности всё ещё не указаны, используем fallback логику
                    if not input_modalities and not output_modalities:
                        logger.debug(f"Model {model_data.get('id', 'unknown')} has no modalities, using fallback detection")
                        
                        model_id = model_data.get("id", "").lower()
                        
                        # Определяем по architecture.modality
                        arch_modality = arch.get("modality", "")
                        if arch_modality == "text->text":
                            input_modalities = ["text"]
                            output_modalities = ["text"]
                        elif arch_modality == "text+image->text":
                            input_modalities = ["text", "image"]
                            output_modalities = ["text"]
                        elif arch_modality == "text->image":
                            input_modalities = ["text"]
                            output_modalities = ["image"]
                        elif arch_modality == "audio->text":
                            input_modalities = ["audio"]
                            output_modalities = ["text"]
                        elif arch_modality == "text->audio":
                            input_modalities = ["text"]
                            output_modalities = ["audio"]
                        else:
                            # Последний fallback по ключевым словам в ID
                            if any(keyword in model_id for keyword in ["whisper", "speech-to-text"]):
                                input_modalities = ["audio"]
                                output_modalities = ["text"]
                            elif any(keyword in model_id for keyword in ["tts", "text-to-speech"]):
                                input_modalities = ["text"]
                                output_modalities = ["audio"]
                            elif any(keyword in model_id for keyword in ["dall-e", "midjourney", "stable-diffusion", "imagen", "flux"]):
                                input_modalities = ["text"]
                                output_modalities = ["image"]
                            elif any(keyword in model_id for keyword in ["vision", "gpt-4v", "claude-3-5", "gemini-pro-vision"]):
                                input_modalities = ["text", "image"]
                                output_modalities = ["text"]
                            else:
                                # По умолчанию считаем текстовой моделью
                                input_modalities = ["text"]
                                output_modalities = ["text"]

                    # Создаём модель с определёнными модальностями
                    model = OpenRouterModel(
                        id=model_data["id"],
                        name=model_data.get("name", model_data["id"]),
                        description=model_data.get("description"),
                        pricing=model_data.get("pricing", {}),
                        context_length=model_data.get("context_length", 0),
                        architecture=model_data.get("architecture", {}),
                        top_provider=model_data.get("top_provider", {}),
                        per_request_limits=model_data.get("per_request_limits"),
                        capabilities=[],  # Больше не используем capabilities, только модальности
                        input_modalities=input_modalities,
                        output_modalities=output_modalities
                    )
                    models.append(model)

                except KeyError as e:
                    logger.warning(f"Skipping model due to missing key {e}: {model_data.get('id', 'unknown')}")
                    continue

            logger.info(f"Retrieved {len(models)} models from OpenRouter")
            
            # Логируем статистику по категориям моделей
            categories_count = {}
            for model in models:
                category = model.get_model_category()
                categories_count[category] = categories_count.get(category, 0) + 1
            
            logger.info(f"Models by category: {categories_count}")
            return models

        except OpenRouterAPIError:
            raise
        except Exception as e:
            logger.error(f"Error parsing models response: {e}")
            raise OpenRouterAPIError(f"Error parsing models: {str(e)}")
    
    async def get_models_by_category(self, category: str) -> List[OpenRouterModel]:
        """Получить модели по категории.
        
        Args:
            category: Категория модели (text, vision, image_generation, audio_transcription, text_to_speech, multimodal)
            
        Returns:
            Список моделей указанной категории
        """
        models = await self.get_models()
        
        filtered_models = []
        for model in models:
            if model.get_model_category() == category:
                filtered_models.append(model)
        
        return filtered_models
    
    async def get_balance(self) -> OpenRouterBalance:
        """Get account balance and usage information.

        Returns:
            OpenRouterBalance object with balance information

        Raises:
            OpenRouterAPIError: If API request fails
        """
        try:
            logger.info("Attempting to get balance from OpenRouter API")
            # Try the credits endpoint first
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        "https://openrouter.ai/api/v1/credits",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://your-app.com",
                            "X-Title": "CRM TG Project"
                        }
                    )

                    if response.status_code == 200:
                        data = response.json()
                        balance_info = data.get("data", {})

                        total_credits = float(balance_info.get("total_credits", 0.0))
                        total_usage = float(balance_info.get("total_usage", 0.0))
                        current_balance = total_credits - total_usage

                        logger.info(f"Successfully retrieved balance: ${current_balance:.4f}")

                        return OpenRouterBalance(
                            balance=current_balance,
                            usage=total_usage,
                            limit=total_credits,
                            rate_limit=balance_info.get("rate_limit", {})
                        )
                    else:
                        logger.warning(f"Credits endpoint returned {response.status_code}, trying alternative method")

            except Exception as e:
                logger.warning(f"Credits endpoint failed: {e}, trying alternative method")

            # Fallback: Try to get balance from auth/key endpoint
            try:
                auth_data = await self._make_request("GET", "/auth/key")
                logger.debug(f"Auth data: {auth_data}")

                # Some OpenRouter plans might include balance info in auth response
                if "data" in auth_data:
                    auth_info = auth_data["data"]
                    balance = float(auth_info.get("balance", 0.0))
                    usage = float(auth_info.get("usage", 0.0))

                    logger.info(f"Retrieved balance from auth endpoint: ${balance:.4f}")

                    return OpenRouterBalance(
                        balance=balance,
                        usage=usage,
                        limit=None,
                        rate_limit={}
                    )

            except Exception as e:
                logger.warning(f"Auth endpoint also failed: {e}")

            # Last resort: Return placeholder data with a note about API limitations
            logger.warning("All balance endpoints failed, returning placeholder data")
            logger.info("Note: Balance endpoint may require a paid OpenRouter plan")
            return OpenRouterBalance(
                balance=0.0,
                usage=0.0,
                limit=None,
                rate_limit={}
            )

        except Exception as e:
            logger.error(f"Unexpected error in get_balance: {e}")
            # Return placeholder data instead of raising error
            return OpenRouterBalance(
                balance=0.0,
                usage=0.0,
                limit=None,
                rate_limit={}
            )
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test connection to OpenRouter API.
        
        Returns:
            Tuple of (success, message)
        """
        try:
            await self.get_balance()
            return True, "Connection successful"
        except OpenRouterAPIError as e:
            return False, f"Connection failed: {e.message}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    async def chat_completion(self, 
                             model: str, 
                             messages: List[Dict[str, str]], 
                             **kwargs) -> Dict[str, Any]:
        """Send chat completion request to OpenRouter.
        
        Args:
            model: Model ID to use
            messages: List of message objects
            **kwargs: Additional parameters for the request
            
        Returns:
            Chat completion response
            
        Raises:
            OpenRouterAPIError: If API request fails
        """
        try:
            payload = {
                "model": model,
                "messages": messages,
                **kwargs
            }
            
            data = await self._make_request("POST", "/chat/completions", json=payload)
            logger.info(f"Chat completion successful with model {model}")
            return data
            
        except OpenRouterAPIError:
            raise
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise OpenRouterAPIError(f"Chat completion error: {str(e)}")
    
    def get_model_pricing_info(self, model: OpenRouterModel) -> Dict[str, str]:
        """Get formatted pricing information for a model.
        
        Args:
            model: OpenRouterModel object
            
        Returns:
            Dictionary with formatted pricing information
        """
        pricing = model.pricing
        
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")
        
        # Convert to more readable format
        try:
            prompt_cost = float(prompt_price) * 1000000  # Convert to cost per 1M tokens
            completion_cost = float(completion_price) * 1000000
            
            return {
                "prompt_cost": f"${prompt_cost:.2f}/1M tokens",
                "completion_cost": f"${completion_cost:.2f}/1M tokens",
                "raw_prompt": prompt_price,
                "raw_completion": completion_price
            }
        except (ValueError, TypeError):
            return {
                "prompt_cost": "N/A",
                "completion_cost": "N/A", 
                "raw_prompt": prompt_price,
                "raw_completion": completion_price
            }


class OpenRouterModelManager:
    """Manager class for OpenRouter model operations with database integration."""
    
    def __init__(self, api_key: str):
        """Initialize model manager.
        
        Args:
            api_key: OpenRouter API key
        """
        self.api_key = api_key
        self._service: Optional[OpenRouterService] = None
    
    async def get_service(self) -> OpenRouterService:
        """Get or create OpenRouter service instance.
        
        Returns:
            OpenRouterService instance
        """
        if self._service is None:
            self._service = OpenRouterService(self.api_key)
        return self._service
    
    async def close(self):
        """Close the service connection."""
        if self._service:
            await self._service.close()
            self._service = None
    
    async def get_available_models_by_type(self) -> Dict[str, List[Dict[str, Any]]]:
        """Получить доступные модели, сгруппированные по типам согласно OpenRouter модальностям.
        
        Returns:
            Словарь с моделями, сгруппированными по категориям
        """
        service = await self.get_service()
        
        try:
            all_models = await service.get_models()
            
            # Новая группировка согласно OpenRouter документации
            grouped_models = {
                "text": [],                    # Только текстовые модели
                "image_vision": [],           # Модели анализа изображений (text+image -> text)
                "image_generation": [],       # Модели генерации изображений (text -> image)  
                "audio": [],                  # Модели транскрипции аудио (audio -> text)
                "text_to_speech": [],         # Модели синтеза речи (text -> audio)
                "multimodal": []              # Сложные мультимодальные модели
            }
            
            for model in all_models:
                model_info = {
                    "id": model.id,
                    "name": model.name,
                    "description": model.description,
                    "context_length": model.context_length,
                    "pricing": service.get_model_pricing_info(model),
                    "provider": model.top_provider.get("name", "Unknown"),
                    "input_modalities": model.input_modalities,
                    "output_modalities": model.output_modalities,
                    "category": model.get_model_category()
                }
                
                # Группировка по категориям на основе модальностей
                category = model.get_model_category()
                
                if category == "text":
                    grouped_models["text"].append(model_info)
                elif category == "vision":
                    grouped_models["image_vision"].append(model_info)
                elif category == "image_generation":
                    grouped_models["image_generation"].append(model_info)
                elif category == "audio_transcription":
                    grouped_models["audio"].append(model_info)
                elif category == "text_to_speech":
                    grouped_models["text_to_speech"].append(model_info)
                elif category == "multimodal":
                    grouped_models["multimodal"].append(model_info)
            
            # Логируем статистику
            for group_name, models_list in grouped_models.items():
                if models_list:
                    logger.info(f"{group_name}: {len(models_list)} models")
            
            return grouped_models
            
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get account balance and usage information.

        Returns:
            Dictionary with account information formatted for frontend
        """
        service = await self.get_service()

        try:
            balance = await service.get_balance()

            return {
                "balance": balance.balance,
                "usage": balance.usage,
                "limit": balance.limit,
                "formatted_balance": f"${balance.balance:.4f}",
                "formatted_usage": f"${balance.usage:.4f}",
                "rate_limit": balance.rate_limit
            }

        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise

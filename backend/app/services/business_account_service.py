import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
import httpx
import json

from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage
from app.services.settings_service import SettingsService
from app.services.openrouter_service import OpenRouterService
from app.schemas.business_account_schema import ChatSummaryResponse, ChatSuggestionsResponse
from app.schemas.settings_schema import KeyTypeEnum, DataTypeEnum, PromptTypeEnum


logger = logging.getLogger(__name__)


class BusinessAccountService:
    """Service for managing Telegram Business Accounts"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = BusinessAccountRepository(db)
        self.settings_service = SettingsService(db)

    async def get_telegram_bot_token(self, user_id: int) -> Optional[str]:
        """Get Telegram bot token for user"""
        return self.settings_service.get_api_key(user_id, "telegram_bot", decrypt=True)

    async def send_telegram_request(self, user_id: int, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to Telegram Bot API"""
        bot_token = await self.get_telegram_bot_token(user_id)
        if not bot_token:
            raise ValueError("Telegram bot token not configured")

        url = f"https://api.telegram.org/bot{bot_token}/{method}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=params)
                response.raise_for_status()
                result = response.json()
                
                if not result.get('ok'):
                    logger.error(f"Telegram API error: {result}")
                    raise ValueError(f"Telegram API error: {result.get('description', 'Unknown error')}")
                
                return result.get('result', {})
                
            except httpx.HTTPError as e:
                logger.error(f"HTTP error when calling Telegram API: {e}")
                raise ValueError(f"Failed to call Telegram API: {str(e)}")

    # Business Account management
    def get_all_business_accounts(self, app_user_id: int) -> List[BusinessAccount]:
        """Get all business accounts for user - either their own or all active ones"""
        return self.repository.get_all_business_accounts(app_user_id)

    def get_business_account_by_connection_id(self, connection_id: str) -> Optional[BusinessAccount]:
        """Get business account by connection ID"""
        return self.repository.get_business_account_by_connection_id(connection_id)

    def create_or_update_business_account(
        self, 
        business_connection_id: str,
        user_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        is_enabled: bool = True,
        can_reply: bool = False
    ) -> BusinessAccount:
        """Create or update business account"""
        existing = self.repository.get_business_account_by_connection_id(business_connection_id)
        
        if existing:
            return self.repository.update_business_account(
                existing.id,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                is_enabled=is_enabled,
                can_reply=can_reply
            )
        else:
            return self.repository.create_business_account(
                business_connection_id=business_connection_id,
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
                is_enabled=is_enabled,
                can_reply=can_reply
            )

    def disable_business_account(self, connection_id: str) -> Optional[BusinessAccount]:
        """Disable business account when bot is removed"""
        account = self.repository.get_business_account_by_connection_id(connection_id)
        if account:
            return self.repository.update_business_account(account.id, is_enabled=False)
        return None

    # Chat management
    def get_chats_for_business_account(self, business_account_id: int) -> List[BusinessChat]:
        """Get all chats for a business account"""
        return self.repository.get_chats_for_business_account(business_account_id)

    def create_or_update_chat(
        self,
        business_account_id: int,
        chat_id: int,
        chat_type: str,
        title: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        username: Optional[str] = None
    ) -> BusinessChat:
        """Create or update business chat"""
        existing = self.repository.get_chat_by_telegram_id(chat_id, business_account_id)
        
        if existing:
            return self.repository.update_business_chat(
                existing.id,
                title=title,
                first_name=first_name,
                last_name=last_name,
                username=username,
                chat_type=chat_type
            )
        else:
            return self.repository.create_business_chat(
                business_account_id=business_account_id,
                chat_id=chat_id,
                chat_type=chat_type,
                title=title,
                first_name=first_name,
                last_name=last_name,
                username=username
            )

    # Message management
    def get_chat_messages(self, chat_id: int, limit: int = 50, offset: int = 0) -> List[BusinessMessage]:
        """Get messages for a chat"""
        return self.repository.get_messages_for_chat(chat_id, limit, offset)

    def save_incoming_message(
        self,
        business_account: BusinessAccount,
        message_data: Dict[str, Any]
    ) -> BusinessMessage:
        """Save incoming message from Telegram webhook"""
        # Extract chat information
        chat_data = message_data.get('chat', {})
        chat_id = chat_data.get('id')
        chat_type = chat_data.get('type', 'private')
        
        # Create or update chat
        chat = self.create_or_update_chat(
            business_account_id=business_account.id,
            chat_id=chat_id,
            chat_type=chat_type,
            title=chat_data.get('title'),
            first_name=chat_data.get('first_name'),
            last_name=chat_data.get('last_name'),
            username=chat_data.get('username')
        )

        # Extract message information
        from_user = message_data.get('from', {})
        message_id = message_data.get('message_id')
        text = message_data.get('text', '')
        date = datetime.fromtimestamp(message_data.get('date', 0))

        # Handle different message types
        message_type = 'text'
        file_id = None
        file_unique_id = None
        file_name = None
        file_size = None
        mime_type = None

        if message_data.get('photo'):
            message_type = 'photo'
            # Get the largest photo
            photos = message_data['photo']
            largest_photo = max(photos, key=lambda x: x.get('file_size', 0))
            file_id = largest_photo.get('file_id')
            file_unique_id = largest_photo.get('file_unique_id')
            file_size = largest_photo.get('file_size')
            text = message_data.get('caption', '')
        elif message_data.get('document'):
            message_type = 'document'
            doc = message_data['document']
            file_id = doc.get('file_id')
            file_unique_id = doc.get('file_unique_id')
            file_name = doc.get('file_name')
            file_size = doc.get('file_size')
            mime_type = doc.get('mime_type')
            text = message_data.get('caption', '')
        elif message_data.get('voice'):
            message_type = 'voice'
            voice = message_data['voice']
            file_id = voice.get('file_id')
            file_unique_id = voice.get('file_unique_id')
            file_size = voice.get('file_size')
            mime_type = voice.get('mime_type', 'audio/ogg')
        elif message_data.get('video'):
            message_type = 'video'
            video = message_data['video']
            file_id = video.get('file_id')
            file_unique_id = video.get('file_unique_id')
            file_size = video.get('file_size')
            mime_type = video.get('mime_type')
            text = message_data.get('caption', '')

        # Determine if message is outgoing (from business account) or incoming
        sender_id = from_user.get('id')
        is_outgoing = sender_id == business_account.user_id

        # Create message
        message = self.repository.create_business_message(
            message_id=message_id,
            chat_id=chat.id,
            sender_id=sender_id,
            sender_first_name=from_user.get('first_name'),
            sender_last_name=from_user.get('last_name'),
            sender_username=from_user.get('username'),
            text=text,
            message_type=message_type,
            file_id=file_id,
            file_unique_id=file_unique_id,
            file_name=file_name,
            file_size=file_size,
            mime_type=mime_type,
            is_outgoing=is_outgoing,
            telegram_date=date
        )

        # Increment unread count
        self.repository.increment_unread_count(chat.id)

        return message

    async def send_message(
        self,
        user_id: int,
        business_connection_id: str,
        chat_id: int,
        text: str,
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send text message through Telegram Bot API"""
        # Validate that business account exists and is enabled
        business_account = self.repository.get_business_account_by_connection_id(business_connection_id)
        if not business_account:
            logger.error(f"Business account not found for connection_id: {business_connection_id}")
            raise ValueError(f"Business account not found for connection_id: {business_connection_id}")

        if not business_account.is_enabled:
            logger.error(f"Business account {business_account.first_name} is disabled")
            raise ValueError(f"Business account {business_account.first_name} is disabled. Please enable it first.")

        if not business_account.can_reply:
            logger.error(f"Business account {business_account.first_name} cannot reply")
            raise ValueError(f"Business account {business_account.first_name} does not have reply permissions. This usually means the business connection needs to be initialized by sending the first message manually through Telegram Business app.")

        # Validate that chat belongs to this business account
        chat = self.repository.get_chat_by_telegram_id(chat_id, business_account.id)
        if not chat:
            logger.error(f"Chat {chat_id} not found for business account {business_account.id}")
            raise ValueError(f"Chat {chat_id} does not belong to business account {business_account.first_name}. Please initiate conversation manually through Telegram Business first.")

        params = {
            'business_connection_id': business_connection_id,
            'chat_id': chat_id,
            'text': text,
        }

        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id

        result = await self.send_telegram_request(user_id, 'sendMessage', params)

        # Save outgoing message to database
        if result:
            message = self.repository.create_business_message(
                message_id=result.get('message_id'),
                chat_id=chat.id,
                sender_id=business_account.user_id,
                sender_first_name=business_account.first_name,
                sender_last_name=business_account.last_name,
                sender_username=business_account.username,
                text=text,
                message_type='text',
                is_outgoing=True,
                telegram_date=datetime.fromtimestamp(result.get('date', 0))
            )
            logger.info(f"Message saved to database with ID: {message.id}")

        return result

    async def send_photo(
        self,
        user_id: int,
        business_connection_id: str,
        chat_id: int,
        photo_file_id: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send photo through Telegram Bot API"""
        params = {
            'business_connection_id': business_connection_id,
            'chat_id': chat_id,
            'photo': photo_file_id,
        }
        
        if caption:
            params['caption'] = caption
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id

        result = await self.send_telegram_request(user_id, 'sendPhoto', params)
        
        # Save outgoing message to database
        if result:
            business_account = self.repository.get_business_account_by_connection_id(business_connection_id)
            if business_account:
                chat = self.repository.get_chat_by_telegram_id(chat_id, business_account.id)
                if chat:
                    message = self.repository.create_business_message(
                        message_id=result.get('message_id'),
                        chat_id=chat.id,
                        sender_id=business_account.user_id,
                        sender_first_name=business_account.first_name,
                        sender_last_name=business_account.last_name,
                        sender_username=business_account.username,
                        text=caption or '',
                        message_type='photo',
                        file_id=photo_file_id,
                        is_outgoing=True,
                        telegram_date=datetime.fromtimestamp(result.get('date', 0))
                    )

        return result

    async def send_document(
        self,
        user_id: int,
        business_connection_id: str,
        chat_id: int,
        document_file_id: str,
        caption: Optional[str] = None,
        reply_to_message_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Send document through Telegram Bot API"""
        params = {
            'business_connection_id': business_connection_id,
            'chat_id': chat_id,
            'document': document_file_id,
        }
        
        if caption:
            params['caption'] = caption
        if reply_to_message_id:
            params['reply_to_message_id'] = reply_to_message_id

        result = await self.send_telegram_request(user_id, 'sendDocument', params)
        
        # Save outgoing message to database
        if result:
            business_account = self.repository.get_business_account_by_connection_id(business_connection_id)
            if business_account:
                chat = self.repository.get_chat_by_telegram_id(chat_id, business_account.id)
                if chat:
                    message = self.repository.create_business_message(
                        message_id=result.get('message_id'),
                        chat_id=chat.id,
                        sender_id=business_account.user_id,
                        sender_first_name=business_account.first_name,
                        sender_last_name=business_account.last_name,
                        sender_username=business_account.username,
                        text=caption or '',
                        message_type='document',
                        file_id=document_file_id,
                        is_outgoing=True,
                        telegram_date=datetime.fromtimestamp(result.get('date', 0))
                    )

        return result

    def mark_chat_as_read(self, chat_id: int) -> None:
        """Mark chat messages as read"""
        self.repository.mark_messages_as_read(chat_id)

    def get_business_account_stats(self, business_account_id: int) -> Dict[str, Any]:
        """Get statistics for business account"""
        return self.repository.get_business_account_stats(business_account_id)

    def search_messages(self, business_account_id: int, query: str, limit: int = 20) -> List[BusinessMessage]:
        """Search messages by text content"""
        return self.repository.search_messages(business_account_id, query, limit)

    async def generate_chat_summary(self, user_id: int, chat_id: int) -> ChatSummaryResponse:
        """Generate AI summary for a chat using OpenRouter"""
        try:
            # Get chat messages (last 100 messages for summary)
            # Note: get_messages_for_chat returns messages in desc order (newest first), so we reverse it
            messages = self.repository.get_messages_for_chat(chat_id, limit=100)
            messages.reverse()  # Reverse to get chronological order (oldest first)

            if not messages:
                raise ValueError("No messages found in chat")

            # Get OpenRouter API key
            openrouter_key = self.settings_service.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
            logger.info(f"OpenRouter key found: {bool(openrouter_key)}")
            if not openrouter_key:
                raise ValueError("OpenRouter API key not configured")

            # Get text model for summary generation
            text_model = self.settings_service.get_model_by_data_type(user_id, DataTypeEnum.TEXT)
            if not text_model:
                raise ValueError("Text model not configured in settings")

            # Get summary prompt from settings
            summary_prompt = self.settings_service.get_prompt_by_type(user_id, PromptTypeEnum.SUMMARY)
            if not summary_prompt:
                summary_prompt = """Проанализируй этот диалог и создай краткое, но информативное резюме.

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
- neutral: деловой, нейтральный, информационный обмен"""

            # Format messages for AI
            formatted_messages = []
            for msg in messages:
                if msg.is_outgoing:
                    # Исходящее сообщение от бизнес-аккаунта
                    sender_label = "Вы (бизнес-аккаунт)"
                else:
                    # Входящее сообщение от клиента
                    sender_name = f"{msg.sender_first_name or ''} {msg.sender_last_name or ''}".strip()
                    if not sender_name and msg.sender_username:
                        sender_name = f"@{msg.sender_username}"
                    if not sender_name:
                        sender_name = "Клиент"
                    sender_label = sender_name

                formatted_messages.append(f"{sender_label}: {msg.text}")

            chat_history = "\n".join(formatted_messages)

            # Create AI prompt
            full_prompt = f"""{summary_prompt}

История чата:
{chat_history}

ВАЖНО: Отвечай ТОЛЬКО в формате JSON. Не добавляй никакого дополнительного текста, объяснений, markdown formatting (```json) или других символов.

Формат ответа (ТОЛЬКО чистый JSON, без markdown):
{{
  "summary": "Краткое резюме диалога на русском языке (3-5 предложений)",
  "key_points": [
    "Первый ключевой момент",
    "Второй ключевой момент",
    "Третий ключевой момент"
  ],
  "sentiment": "positive|negative|neutral"
}}"""

            # Call OpenRouter API
            async with OpenRouterService(openrouter_key) as openrouter:
                response = await openrouter.chat_completion(
                    model=text_model.model_name,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )

            # Parse AI response
            ai_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            try:
                # Clean the response from markdown formatting
                cleaned_response = ai_response.strip()

                # Remove markdown code blocks (```json ... ```)
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```

                cleaned_response = cleaned_response.strip()

                # Try to parse JSON response
                import json
                parsed_response = json.loads(cleaned_response)

                summary = parsed_response.get("summary", ai_response)
                key_points = parsed_response.get("key_points", [])
                sentiment = parsed_response.get("sentiment", "neutral")

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                logger.warning(f"Raw AI response: {ai_response}")
                # Fallback if AI didn't return valid JSON
                summary = ai_response
                key_points = []
                sentiment = "neutral"

            return ChatSummaryResponse(
                summary=summary,
                key_points=key_points,
                sentiment=sentiment,
                last_updated=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Error generating chat summary for chat {chat_id}: {e}")
            raise

    async def generate_chat_suggestions(self, user_id: int, chat_id: int) -> ChatSuggestionsResponse:
        """Generate AI suggestions for chat replies using OpenRouter"""
        try:
            # Get chat messages (last 50 messages for suggestions)
            messages = self.repository.get_messages_for_chat(chat_id, limit=50)
            messages.reverse()  # Reverse to get chronological order (oldest first)

            if not messages:
                raise ValueError("No messages found in chat")

            # Get OpenRouter API key
            openrouter_key = self.settings_service.get_api_key(user_id, KeyTypeEnum.OPENROUTER, decrypt=True)
            if not openrouter_key:
                raise ValueError("OpenRouter API key not configured")

            # Get text model for suggestions generation
            text_model = self.settings_service.get_model_by_data_type(user_id, DataTypeEnum.TEXT)
            if not text_model:
                raise ValueError("Text model not configured in settings")

            # Get suggestions prompt from settings
            suggestions_prompt = self.settings_service.get_prompt_by_type(user_id, PromptTypeEnum.SUGGESTIONS)
            if not suggestions_prompt:
                suggestions_prompt = """Проанализируй историю чата и предложи 3-4 варианта ответа от лица бизнес-аккаунта.

В истории чата:
- "Вы (бизнес-аккаунт)" - это ваши предыдущие сообщения
- Имена клиентов - это входящие сообщения от клиентов

Требования к ответам:
- Пиши на русском языке
- Будь кратким и по существу
- Учитывай контекст и предыдущие сообщения
- Предлагай профессиональные и уместные варианты ответа
- Каждый ответ должен быть естественным продолжением разговора

Учитывай роль бизнес-аккаунта и специфику общения с клиентами."""

            # Format messages for AI
            formatted_messages = []
            for msg in messages:
                if msg.is_outgoing:
                    # Исходящее сообщение от бизнес-аккаунта
                    sender_label = "Вы (бизнес-аккаунт)"
                else:
                    # Входящее сообщение от клиента
                    sender_name = f"{msg.sender_first_name or ''} {msg.sender_last_name or ''}".strip()
                    if not sender_name and msg.sender_username:
                        sender_name = f"@{msg.sender_username}"
                    if not sender_name:
                        sender_name = "Клиент"
                    sender_label = sender_name

                formatted_messages.append(f"{sender_label}: {msg.text}")

            chat_history = "\n".join(formatted_messages)

            # Create AI prompt
            full_prompt = f"""{suggestions_prompt}

История чата:
{chat_history}

ВАЖНО: Отвечай ТОЛЬКО в формате JSON. Не добавляй никакого дополнительного текста или объяснений.

Формат ответа (ТОЛЬКО чистый JSON, без markdown):
{{
  "suggestions": [
    "Первый вариант ответа",
    "Второй вариант ответа",
    "Третий вариант ответа",
    "Четвертый вариант ответа"
  ]
}}"""

            # Call OpenRouter API
            async with OpenRouterService(openrouter_key) as openrouter:
                response = await openrouter.chat_completion(
                    model=text_model.model_name,
                    messages=[
                        {"role": "user", "content": full_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )

            # Parse AI response
            ai_response = response.get("choices", [{}])[0].get("message", {}).get("content", "")

            try:
                # Clean the response from markdown formatting
                cleaned_response = ai_response.strip()

                # Remove markdown code blocks
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]

                cleaned_response = cleaned_response.strip()

                # Try to parse JSON response
                import json
                parsed_response = json.loads(cleaned_response)

                suggestions = parsed_response.get("suggestions", [])

                # Ensure we have a list of strings
                if not isinstance(suggestions, list):
                    suggestions = []

                # Filter out non-string suggestions and limit to 4
                suggestions = [str(s) for s in suggestions if s][:4]

            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response for suggestions: {e}")
                logger.warning(f"Raw AI response: {ai_response}")
                # Fallback: try to extract suggestions from text
                suggestions = []
                lines = ai_response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 10 and not line.startswith(('Формат', 'ВАЖНО', 'История', '{', '}')):
                        suggestions.append(line[:200])  # Limit length
                        if len(suggestions) >= 4:
                            break

            return ChatSuggestionsResponse(suggestions=suggestions)

        except Exception as e:
            logger.error(f"Error generating chat suggestions for chat {chat_id}: {e}")
            raise



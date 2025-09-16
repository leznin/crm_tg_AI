import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
import httpx
import json

from app.db.repositories.business_account_repository import BusinessAccountRepository
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage
from app.services.settings_service import SettingsService


logger = logging.getLogger(__name__)


class BusinessAccountService:
    """Service for managing Telegram Business Accounts"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = BusinessAccountRepository(db)
        self.settings_service = SettingsService(db)

    async def get_telegram_bot_token(self, user_id: int) -> Optional[str]:
        """Get Telegram bot token for user"""
        return await self.settings_service.get_api_key(user_id, "telegram_bot")

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
    def get_all_business_accounts(self, user_id: int) -> List[BusinessAccount]:
        """Get all business accounts for user"""
        return self.repository.get_all_business_accounts()

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
        business_account_id: int,
        message_data: Dict[str, Any]
    ) -> BusinessMessage:
        """Save incoming message from Telegram webhook"""
        # Extract chat information
        chat_data = message_data.get('chat', {})
        chat_id = chat_data.get('id')
        chat_type = chat_data.get('type', 'private')
        
        # Create or update chat
        chat = self.create_or_update_chat(
            business_account_id=business_account_id,
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

        # Create message
        message = self.repository.create_business_message(
            message_id=message_id,
            chat_id=chat.id,
            sender_id=from_user.get('id'),
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
            is_outgoing=False,
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
                        text=text,
                        message_type='text',
                        is_outgoing=True,
                        telegram_date=datetime.fromtimestamp(result.get('date', 0))
                    )

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



from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage


class BusinessAccountRepository:
    """Repository for managing Business Account data"""

    def __init__(self, db: Session):
        self.db = db

    # Business Account CRUD
    def get_business_account_by_connection_id(self, connection_id: str) -> Optional[BusinessAccount]:
        """Get business account by connection ID"""
        return self.db.query(BusinessAccount).filter(
            BusinessAccount.business_connection_id == connection_id
        ).first()

    def get_business_account_by_user_id(self, user_id: int) -> Optional[BusinessAccount]:
        """Get business account by Telegram user ID"""
        return self.db.query(BusinessAccount).filter(
            BusinessAccount.user_id == user_id
        ).first()

    def get_all_business_accounts(self) -> List[BusinessAccount]:
        """Get all business accounts with their chats"""
        return self.db.query(BusinessAccount).options(
            joinedload(BusinessAccount.chats)
        ).all()

    def create_business_account(self, **kwargs) -> BusinessAccount:
        """Create a new business account"""
        account = BusinessAccount(**kwargs)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_business_account(self, account_id: int, **kwargs) -> Optional[BusinessAccount]:
        """Update business account"""
        account = self.db.query(BusinessAccount).filter(
            BusinessAccount.id == account_id
        ).first()
        if account:
            for key, value in kwargs.items():
                setattr(account, key, value)
            self.db.commit()
            self.db.refresh(account)
        return account

    def delete_business_account(self, account_id: int) -> bool:
        """Delete business account and all related data"""
        account = self.db.query(BusinessAccount).filter(
            BusinessAccount.id == account_id
        ).first()
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False

    # Business Chat CRUD
    def get_chat_by_telegram_id(self, chat_id: int, business_account_id: int) -> Optional[BusinessChat]:
        """Get chat by Telegram chat ID and business account ID"""
        return self.db.query(BusinessChat).filter(
            and_(
                BusinessChat.chat_id == chat_id,
                BusinessChat.business_account_id == business_account_id
            )
        ).first()

    def get_chats_for_business_account(self, business_account_id: int) -> List[BusinessChat]:
        """Get all chats for a business account, ordered by last message"""
        return self.db.query(BusinessChat).filter(
            BusinessChat.business_account_id == business_account_id
        ).order_by(desc(BusinessChat.last_message_at)).all()

    def create_business_chat(self, **kwargs) -> BusinessChat:
        """Create a new business chat"""
        chat = BusinessChat(**kwargs)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def update_business_chat(self, chat_id: int, **kwargs) -> Optional[BusinessChat]:
        """Update business chat"""
        chat = self.db.query(BusinessChat).filter(
            BusinessChat.id == chat_id
        ).first()
        if chat:
            for key, value in kwargs.items():
                setattr(chat, key, value)
            self.db.commit()
            self.db.refresh(chat)
        return chat

    def update_chat_last_message_time(self, chat_id: int, timestamp) -> None:
        """Update the last message timestamp for a chat"""
        chat = self.db.query(BusinessChat).filter(
            BusinessChat.id == chat_id
        ).first()
        if chat:
            chat.last_message_at = timestamp
            self.db.commit()

    # Business Message CRUD
    def get_messages_for_chat(self, chat_id: int, limit: int = 50, offset: int = 0) -> List[BusinessMessage]:
        """Get messages for a chat, ordered by creation time"""
        return self.db.query(BusinessMessage).filter(
            BusinessMessage.chat_id == chat_id
        ).order_by(desc(BusinessMessage.created_at)).offset(offset).limit(limit).all()

    def get_message_by_telegram_id(self, message_id: int, chat_id: int) -> Optional[BusinessMessage]:
        """Get message by Telegram message ID and chat ID"""
        return self.db.query(BusinessMessage).filter(
            and_(
                BusinessMessage.message_id == message_id,
                BusinessMessage.chat_id == chat_id
            )
        ).first()

    def create_business_message(self, **kwargs) -> BusinessMessage:
        """Create a new business message"""
        message = BusinessMessage(**kwargs)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update chat's message count and last message time
        chat = self.db.query(BusinessChat).filter(
            BusinessChat.id == message.chat_id
        ).first()
        if chat:
            chat.message_count += 1
            chat.last_message_at = message.created_at
            self.db.commit()
        
        return message

    def mark_messages_as_read(self, chat_id: int) -> None:
        """Mark all messages in a chat as read (reset unread count)"""
        chat = self.db.query(BusinessChat).filter(
            BusinessChat.id == chat_id
        ).first()
        if chat:
            chat.unread_count = 0
            self.db.commit()

    def increment_unread_count(self, chat_id: int) -> None:
        """Increment unread count for a chat"""
        chat = self.db.query(BusinessChat).filter(
            BusinessChat.id == chat_id
        ).first()
        if chat:
            chat.unread_count += 1
            self.db.commit()

    # Statistics and analytics
    def get_business_account_stats(self, business_account_id: int) -> Dict[str, Any]:
        """Get statistics for a business account"""
        account = self.db.query(BusinessAccount).filter(
            BusinessAccount.id == business_account_id
        ).first()
        
        if not account:
            return {}

        chats_count = self.db.query(BusinessChat).filter(
            BusinessChat.business_account_id == business_account_id
        ).count()

        messages_count = self.db.query(BusinessMessage).join(BusinessChat).filter(
            BusinessChat.business_account_id == business_account_id
        ).count()

        unread_count = self.db.query(BusinessChat).filter(
            and_(
                BusinessChat.business_account_id == business_account_id,
                BusinessChat.unread_count > 0
            )
        ).count()

        return {
            "chats_count": chats_count,
            "messages_count": messages_count,
            "unread_chats_count": unread_count,
            "account_name": f"{account.first_name} {account.last_name or ''}".strip(),
            "username": account.username,
            "is_enabled": account.is_enabled
        }

    def search_messages(self, business_account_id: int, query: str, limit: int = 20) -> List[BusinessMessage]:
        """Search messages by text content"""
        return self.db.query(BusinessMessage).join(BusinessChat).filter(
            and_(
                BusinessChat.business_account_id == business_account_id,
                BusinessMessage.text.contains(query)
            )
        ).order_by(desc(BusinessMessage.created_at)).limit(limit).all()



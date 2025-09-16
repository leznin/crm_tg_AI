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

    def get_all_business_accounts(self, app_user_id: int) -> List[BusinessAccount]:
        """Get all active business accounts grouped by telegram user"""
        return self.get_all_active_business_accounts()

    def get_user_business_accounts_with_chat_merging(self, telegram_user_id: int) -> List[BusinessAccount]:
        """Get business accounts for a specific telegram user with chat merging"""
        # Get all accounts for this telegram_user_id (both enabled and disabled)
        accounts = self.db.query(BusinessAccount).filter(
            BusinessAccount.user_id == telegram_user_id
        ).order_by(BusinessAccount.created_at.desc()).all()

        if not accounts:
            return []

        # Create a single "virtual" business account representing all accounts for this user
        # Use the most recent account's data as the base
        most_recent = accounts[0]

        # Create a copy of the most recent account to avoid modifying the original
        virtual_account = BusinessAccount(
            id=most_recent.id,
            business_connection_id=most_recent.business_connection_id,
            user_id=most_recent.user_id,
            first_name=most_recent.first_name,
            last_name=most_recent.last_name,
            username=most_recent.username,
            is_enabled=most_recent.is_enabled,
            can_reply=most_recent.can_reply,
            created_at=most_recent.created_at,
            updated_at=most_recent.updated_at
        )

        # Get ALL business account IDs for this telegram user
        business_account_ids = [acc.id for acc in accounts]

        # Get ALL chats from ALL business accounts for this user
        from app.models.business_account import BusinessChat
        all_chats = self.db.query(BusinessChat).filter(
            BusinessChat.business_account_id.in_(business_account_ids)
        ).order_by(BusinessChat.last_message_at.desc()).all()

        # Group chats by telegram chat_id and merge them
        chats_by_telegram_id = {}
        for chat in all_chats:
            telegram_chat_id = chat.chat_id
            if telegram_chat_id not in chats_by_telegram_id:
                chats_by_telegram_id[telegram_chat_id] = chat
            else:
                # If we already have this chat, keep the one with more recent activity
                existing = chats_by_telegram_id[telegram_chat_id]
                if (chat.last_message_at and (not existing.last_message_at or chat.last_message_at > existing.last_message_at)) or \
                   (not chat.last_message_at and existing.last_message_at):
                    chats_by_telegram_id[telegram_chat_id] = chat
                # Merge unread counts and message counts
                existing.unread_count = max(existing.unread_count, chat.unread_count)
                existing.message_count = max(existing.message_count, chat.message_count)

        # Convert to list and assign to virtual account
        merged_chats = list(chats_by_telegram_id.values())
        virtual_account.chats = merged_chats

        return [virtual_account]

    def get_all_active_business_accounts(self) -> List[BusinessAccount]:
        """Get all active business accounts grouped by telegram user"""
        # Get all active business accounts
        active_accounts = self.db.query(BusinessAccount).filter(
            BusinessAccount.is_enabled == True
        ).order_by(BusinessAccount.user_id, BusinessAccount.created_at.desc()).all()

        if not active_accounts:
            return []

        # Get all business account user IDs to filter out business-to-business chats
        business_user_ids = {acc.user_id for acc in active_accounts}

        # Group by telegram user_id and create virtual accounts
        from collections import defaultdict
        accounts_by_user = defaultdict(list)

        for account in active_accounts:
            accounts_by_user[account.user_id].append(account)

        virtual_accounts = []

        for telegram_user_id, accounts in accounts_by_user.items():
            # Use the most recent account for this user as base
            most_recent = accounts[0]

            # Create virtual account
            virtual_account = BusinessAccount(
                id=most_recent.id,
                business_connection_id=most_recent.business_connection_id,
                user_id=most_recent.user_id,
                first_name=most_recent.first_name,
                last_name=most_recent.last_name,
                username=most_recent.username,
                is_enabled=most_recent.is_enabled,
                can_reply=most_recent.can_reply,
                created_at=most_recent.created_at,
                updated_at=most_recent.updated_at
            )

            # Get ALL business account IDs for this telegram user
            business_account_ids = [acc.id for acc in accounts]

            # Get ALL chats from ALL business accounts for this user
            from app.models.business_account import BusinessChat
            all_chats = self.db.query(BusinessChat).filter(
                BusinessChat.business_account_id.in_(business_account_ids)
            ).order_by(BusinessChat.last_message_at.desc()).all()

            # Filter out business-to-business chats (where chat_id is another business account's user_id)
            filtered_chats = []
            for chat in all_chats:
                if chat.chat_id not in business_user_ids:
                    filtered_chats.append(chat)

            # Now group the filtered chats by telegram chat_id and merge them
            chats_by_telegram_id = {}
            for chat in filtered_chats:
                telegram_chat_id = chat.chat_id
                if telegram_chat_id not in chats_by_telegram_id:
                    chats_by_telegram_id[telegram_chat_id] = chat
                else:
                    # If we already have this chat, keep the one with more recent activity
                    existing = chats_by_telegram_id[telegram_chat_id]
                    if (chat.last_message_at and (not existing.last_message_at or chat.last_message_at > existing.last_message_at)) or \
                       (not chat.last_message_at and existing.last_message_at):
                        chats_by_telegram_id[telegram_chat_id] = chat
                    # Merge unread counts and message counts
                    existing.unread_count = max(existing.unread_count, chat.unread_count)
                    existing.message_count = max(existing.message_count, chat.message_count)

            # Convert to list and assign to virtual account
            merged_chats = list(chats_by_telegram_id.values())
            virtual_account.chats = merged_chats

            virtual_accounts.append(virtual_account)

        return virtual_accounts

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
        """Get messages for a specific chat, ordered by telegram date"""
        # Get messages only for the specific business_chat.id
        # This ensures we only get messages for this specific business account's conversation
        return self.db.query(BusinessMessage).filter(
            BusinessMessage.chat_id == chat_id
        ).order_by(desc(BusinessMessage.telegram_date)).offset(offset).limit(limit).all()

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



import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.repositories.contact_repository import ContactRepository
from app.models.contact import Contact, ContactBusinessInteraction
from app.schemas.contact_schema import (
    ContactCreate, ContactUpdate, ContactBusinessInteractionCreate,
    ContactBusinessInteractionUpdate, ContactWithBusinessAccount
)

logger = logging.getLogger(__name__)


class ContactService:
    """Сервис для работы с контактами"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ContactRepository(db)

    # CRUD операции для контактов
    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Получить контакт по ID"""
        return self.repository.get_contact_by_id(contact_id)

    def get_contact_by_telegram_id(self, telegram_user_id: int) -> Optional[Contact]:
        """Получить контакт по Telegram ID"""
        return self.repository.get_contact_by_telegram_id(telegram_user_id)

    def create_contact(self, contact_data: ContactCreate) -> Contact:
        """Создать новый контакт"""
        contact_dict = contact_data.dict()
        
        # Преобразуем теги в JSON
        if contact_dict.get('tags'):
            contact_dict['tags'] = contact_dict['tags']
        
        logger.info(f"Creating new contact for telegram_user_id: {contact_dict['telegram_user_id']}")
        return self.repository.create_contact(**contact_dict)

    def update_contact(self, contact_id: int, contact_data: ContactUpdate) -> Optional[Contact]:
        """Обновить контакт"""
        update_dict = contact_data.dict(exclude_unset=True)
        
        # Преобразуем теги в JSON если они есть
        if 'tags' in update_dict and update_dict['tags'] is not None:
            update_dict['tags'] = update_dict['tags']
        
        logger.info(f"Updating contact {contact_id}")
        return self.repository.update_contact(contact_id, **update_dict)

    def delete_contact(self, contact_id: int) -> bool:
        """Удалить контакт"""
        logger.info(f"Deleting contact {contact_id}")
        return self.repository.delete_contact(contact_id)

    # Операции с взаимодействиями
    def create_business_interaction(
        self, 
        interaction_data: ContactBusinessInteractionCreate
    ) -> ContactBusinessInteraction:
        """Создать новое взаимодействие между контактом и бизнес-аккаунтом"""
        interaction_dict = interaction_data.dict()
        logger.info(f"Creating business interaction: contact {interaction_dict['contact_id']} <-> business {interaction_dict['business_account_id']}")
        return self.repository.create_interaction(**interaction_dict)

    def update_business_interaction(
        self, 
        interaction_id: int, 
        interaction_data: ContactBusinessInteractionUpdate
    ) -> Optional[ContactBusinessInteraction]:
        """Обновить взаимодействие"""
        update_dict = interaction_data.dict(exclude_unset=True)
        logger.info(f"Updating business interaction {interaction_id}")
        return self.repository.update_interaction(interaction_id, **update_dict)

    def get_business_interaction(
        self, 
        contact_id: int, 
        business_account_id: int
    ) -> Optional[ContactBusinessInteraction]:
        """Получить взаимодействие между контактом и бизнес-аккаунтом"""
        return self.repository.get_interaction(contact_id, business_account_id)

    # Поиск и фильтрация
    def search_contacts(
        self,
        query: Optional[str] = None,
        business_account_id: Optional[int] = None,
        category: Optional[str] = None,
        rating: Optional[int] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Поиск контактов с пагинацией"""
        
        offset = (page - 1) * per_page
        contacts, total = self.repository.search_contacts(
            query=query,
            business_account_id=business_account_id,
            category=category,
            rating=rating,
            tags=tags,
            limit=per_page,
            offset=offset
        )

        # Преобразуем в схемы с информацией о бизнес-аккаунтах
        contacts_with_business = []
        for contact in contacts:
            for interaction in contact.business_interactions:
                # Получаем информацию о бизнес-аккаунте
                from app.models.business_account import BusinessAccount
                business_account = self.db.query(BusinessAccount).filter(
                    BusinessAccount.id == interaction.business_account_id
                ).first()
                
                if business_account:
                    contact_with_business = ContactWithBusinessAccount(
                        contact=contact,
                        business_account_name=f"{business_account.first_name} {business_account.last_name or ''}".strip(),
                        business_account_username=business_account.username,
                        interaction=interaction
                    )
                    contacts_with_business.append(contact_with_business)

        return {
            'contacts': contacts_with_business,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

    def get_contacts_by_business_account(
        self,
        business_account_id: int,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Получить все контакты для определенного бизнес-аккаунта"""
        
        offset = (page - 1) * per_page
        contacts, total = self.repository.get_contacts_by_business_account(
            business_account_id=business_account_id,
            limit=per_page,
            offset=offset
        )

        return {
            'contacts': contacts,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }

    # Статистика
    def get_contact_stats(self, business_account_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить статистику по контактам"""
        return self.repository.get_contact_stats(business_account_id)

    def get_recent_contacts(
        self, 
        business_account_id: Optional[int] = None, 
        limit: int = 10
    ) -> List[Contact]:
        """Получить недавно добавленные контакты"""
        return self.repository.get_recent_contacts(business_account_id, limit)

    # Обработка сообщений
    def process_message_for_contact(
        self,
        telegram_user_id: int,
        business_account_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        chat_type: str = 'private'
    ) -> Contact:
        """
        Обработать сообщение для создания/обновления контакта
        Этот метод вызывается из webhook обработчика
        """
        logger.info(f"Processing message for contact: telegram_user_id={telegram_user_id}, business_account_id={business_account_id}")
        
        return self.repository.create_or_update_contact_from_message(
            telegram_user_id=telegram_user_id,
            business_account_id=business_account_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
            chat_type=chat_type
        )

    # Дополнительные методы
    def get_contact_interactions(self, contact_id: int) -> List[ContactBusinessInteraction]:
        """Получить все взаимодействия контакта с бизнес-аккаунтами"""
        contact = self.get_contact_by_id(contact_id)
        return contact.business_interactions if contact else []

    def get_top_contacts_by_messages(
        self, 
        business_account_id: Optional[int] = None, 
        limit: int = 10
    ) -> List[Contact]:
        """Получить топ контактов по количеству сообщений"""
        query = self.db.query(Contact)
        
        if business_account_id:
            query = query.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )
        
        return query.order_by(Contact.total_messages.desc()).limit(limit).all()

    def update_contact_rating(self, contact_id: int, rating: int) -> Optional[Contact]:
        """Обновить рейтинг контакта"""
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        return self.repository.update_contact(contact_id, rating=rating)

    def add_contact_tag(self, contact_id: int, tag: str) -> Optional[Contact]:
        """Добавить тег к контакту"""
        contact = self.get_contact_by_id(contact_id)
        if contact:
            tags = contact.tags or []
            if tag not in tags:
                tags.append(tag)
                return self.repository.update_contact(contact_id, tags=tags)
        return contact

    def remove_contact_tag(self, contact_id: int, tag: str) -> Optional[Contact]:
        """Удалить тег у контакта"""
        contact = self.get_contact_by_id(contact_id)
        if contact and contact.tags:
            tags = [t for t in contact.tags if t != tag]
            return self.repository.update_contact(contact_id, tags=tags)
        return contact

    def block_contact_for_business(
        self, 
        contact_id: int, 
        business_account_id: int, 
        reason: Optional[str] = None
    ) -> Optional[ContactBusinessInteraction]:
        """Заблокировать контакт для определенного бизнес-аккаунта"""
        interaction = self.get_business_interaction(contact_id, business_account_id)
        if interaction:
            update_data = ContactBusinessInteractionUpdate(
                status='blocked',
                notes=f"Blocked. Reason: {reason}" if reason else "Blocked"
            )
            return self.update_business_interaction(interaction.id, update_data)
        return None

    def unblock_contact_for_business(
        self, 
        contact_id: int, 
        business_account_id: int
    ) -> Optional[ContactBusinessInteraction]:
        """Разблокировать контакт для определенного бизнес-аккаунта"""
        interaction = self.get_business_interaction(contact_id, business_account_id)
        if interaction:
            update_data = ContactBusinessInteractionUpdate(status='active')
            return self.update_business_interaction(interaction.id, update_data)
        return None

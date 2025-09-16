from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, and_, func, or_, case
from datetime import datetime, timedelta
from app.models.contact import Contact, ContactBusinessInteraction
from app.models.business_account import BusinessAccount


class ContactRepository:
    """Репозиторий для работы с контактами"""

    def __init__(self, db: Session):
        self.db = db

    # CRUD операции для контактов
    def get_contact_by_telegram_id(self, telegram_user_id: int) -> Optional[Contact]:
        """Получить контакт по Telegram ID"""
        return self.db.query(Contact).filter(
            Contact.telegram_user_id == telegram_user_id
        ).first()

    def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        """Получить контакт по ID"""
        return self.db.query(Contact).options(
            joinedload(Contact.business_interactions)
        ).filter(Contact.id == contact_id).first()

    def create_contact(self, **kwargs) -> Contact:
        """Создать новый контакт"""
        contact = Contact(**kwargs)
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def update_contact(self, contact_id: int, **kwargs) -> Optional[Contact]:
        """Обновить контакт"""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            # Обработка изменения username
            if 'username' in kwargs and kwargs['username'] != contact.username:
                if contact.username:  # Если был старый username
                    if not contact.username_history:
                        contact.username_history = []
                    contact.username_history.append({
                        "username": contact.username,
                        "changed_at": datetime.now().isoformat()
                    })

            for key, value in kwargs.items():
                setattr(contact, key, value)
            
            self.db.commit()
            self.db.refresh(contact)
        return contact

    def delete_contact(self, contact_id: int) -> bool:
        """Удалить контакт"""
        contact = self.db.query(Contact).filter(Contact.id == contact_id).first()
        if contact:
            self.db.delete(contact)
            self.db.commit()
            return True
        return False

    # CRUD операции для взаимодействий
    def get_interaction(self, contact_id: int, business_account_id: int) -> Optional[ContactBusinessInteraction]:
        """Получить взаимодействие между контактом и бизнес-аккаунтом"""
        return self.db.query(ContactBusinessInteraction).filter(
            and_(
                ContactBusinessInteraction.contact_id == contact_id,
                ContactBusinessInteraction.business_account_id == business_account_id
            )
        ).first()

    def create_interaction(self, **kwargs) -> ContactBusinessInteraction:
        """Создать новое взаимодействие"""
        interaction = ContactBusinessInteraction(**kwargs)
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def update_interaction(self, interaction_id: int, **kwargs) -> Optional[ContactBusinessInteraction]:
        """Обновить взаимодействие"""
        interaction = self.db.query(ContactBusinessInteraction).filter(
            ContactBusinessInteraction.id == interaction_id
        ).first()
        if interaction:
            for key, value in kwargs.items():
                setattr(interaction, key, value)
            self.db.commit()
            self.db.refresh(interaction)
        return interaction

    def increment_interaction_messages(self, contact_id: int, business_account_id: int) -> None:
        """Увеличить счетчик сообщений для взаимодействия"""
        interaction = self.get_interaction(contact_id, business_account_id)
        if interaction:
            interaction.messages_count += 1
            interaction.last_interaction = datetime.now()
            self.db.commit()

    # Поиск и фильтрация
    def search_contacts(
        self,
        query: Optional[str] = None,
        business_account_id: Optional[int] = None,
        category: Optional[str] = None,
        rating: Optional[int] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Contact], int]:
        """Поиск контактов с фильтрацией"""
        
        # Базовый запрос
        query_base = self.db.query(Contact).options(
            joinedload(Contact.business_interactions)
        )

        # Фильтрация по бизнес-аккаунту
        if business_account_id:
            query_base = query_base.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )

        # Текстовый поиск
        if query:
            search_filter = or_(
                Contact.first_name.ilike(f'%{query}%'),
                Contact.last_name.ilike(f'%{query}%'),
                Contact.username.ilike(f'%{query}%'),
                Contact.brand_name.ilike(f'%{query}%'),
                Contact.position.ilike(f'%{query}%'),
                Contact.notes.ilike(f'%{query}%')
            )
            query_base = query_base.filter(search_filter)

        # Фильтр по категории
        if category:
            query_base = query_base.filter(Contact.category == category)

        # Фильтр по рейтингу
        if rating:
            query_base = query_base.filter(Contact.rating == rating)

        # Фильтр по тегам
        if tags:
            for tag in tags:
                query_base = query_base.filter(Contact.tags.contains([tag]))

        # Подсчет общего количества
        total = query_base.count()

        # Применение пагинации и сортировки
        contacts = query_base.order_by(desc(Contact.last_contact)).offset(offset).limit(limit).all()

        return contacts, total

    def get_contacts_by_business_account(
        self,
        business_account_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[Contact], int]:
        """Получить все контакты для определенного бизнес-аккаунта"""
        
        query_base = self.db.query(Contact).join(ContactBusinessInteraction).filter(
            ContactBusinessInteraction.business_account_id == business_account_id
        ).options(joinedload(Contact.business_interactions))

        total = query_base.count()
        contacts = query_base.order_by(desc(ContactBusinessInteraction.last_interaction)).offset(offset).limit(limit).all()

        return contacts, total

    # Статистика
    def get_contact_stats(self, business_account_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить статистику по контактам"""
        
        # Базовый запрос
        base_query = self.db.query(Contact)
        
        if business_account_id:
            base_query = base_query.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )

        # Общее количество контактов
        total_contacts = base_query.count()

        # Новые контакты за сегодня
        today = datetime.now().date()
        new_today = base_query.filter(
            func.date(Contact.created_at) == today
        ).count()

        # Новые контакты за неделю
        week_ago = datetime.now() - timedelta(days=7)
        new_week = base_query.filter(
            Contact.created_at >= week_ago
        ).count()

        # Распределение по категориям
        category_stats = self.db.query(
            Contact.category,
            func.count(Contact.id).label('count')
        )
        
        if business_account_id:
            category_stats = category_stats.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )
            
        category_stats = category_stats.group_by(Contact.category).all()
        contacts_by_category = {stat.category: stat.count for stat in category_stats}

        # Распределение по рейтингу
        rating_stats = self.db.query(
            Contact.rating,
            func.count(Contact.id).label('count')
        )
        
        if business_account_id:
            rating_stats = rating_stats.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )
            
        rating_stats = rating_stats.group_by(Contact.rating).all()
        contacts_by_rating = {stat.rating: stat.count for stat in rating_stats}

        # Топ бизнес-аккаунтов по количеству контактов
        top_business_accounts = []
        if not business_account_id:  # Только если не фильтруем по конкретному аккаунту
            top_accounts = self.db.query(
                BusinessAccount.id,
                BusinessAccount.first_name,
                BusinessAccount.last_name,
                BusinessAccount.username,
                func.count(ContactBusinessInteraction.contact_id).label('contacts_count')
            ).join(ContactBusinessInteraction).group_by(
                BusinessAccount.id,
                BusinessAccount.first_name,
                BusinessAccount.last_name,
                BusinessAccount.username
            ).order_by(desc('contacts_count')).limit(5).all()

            top_business_accounts = [
                {
                    'id': account.id,
                    'name': f"{account.first_name} {account.last_name or ''}".strip(),
                    'username': account.username,
                    'contacts_count': account.contacts_count
                }
                for account in top_accounts
            ]

        return {
            'total_contacts': total_contacts,
            'new_contacts_today': new_today,
            'new_contacts_week': new_week,
            'contacts_by_category': contacts_by_category,
            'contacts_by_rating': contacts_by_rating,
            'top_business_accounts': top_business_accounts
        }

    def get_recent_contacts(self, business_account_id: Optional[int] = None, limit: int = 10) -> List[Contact]:
        """Получить недавно добавленные контакты"""
        query = self.db.query(Contact).options(joinedload(Contact.business_interactions))
        
        if business_account_id:
            query = query.join(ContactBusinessInteraction).filter(
                ContactBusinessInteraction.business_account_id == business_account_id
            )
        
        return query.order_by(desc(Contact.created_at)).limit(limit).all()

    def create_or_update_contact_from_message(
        self,
        telegram_user_id: int,
        business_account_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None,
        chat_type: str = 'private'
    ) -> Contact:
        """Создать или обновить контакт на основе сообщения"""
        
        # Поиск существующего контакта
        contact = self.get_contact_by_telegram_id(telegram_user_id)
        
        now = datetime.now()
        
        if contact:
            # Обновляем существующий контакт
            updates = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'last_contact': now,
                'total_messages': contact.total_messages + 1
            }
            contact = self.update_contact(contact.id, **updates)
        else:
            # Создаем новый контакт
            contact_data = {
                'telegram_user_id': telegram_user_id,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'source': 'private' if chat_type == 'private' else 'group',
                'last_contact': now,
                'total_messages': 1
            }
            contact = self.create_contact(**contact_data)

        # Создаем или обновляем взаимодействие с бизнес-аккаунтом
        interaction = self.get_interaction(contact.id, business_account_id)
        if interaction:
            self.increment_interaction_messages(contact.id, business_account_id)
        else:
            interaction_data = {
                'contact_id': contact.id,
                'business_account_id': business_account_id,
                'messages_count': 1,
                'first_interaction': now,
                'last_interaction': now
            }
            self.create_interaction(**interaction_data)

        return contact

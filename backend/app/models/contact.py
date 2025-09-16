from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class Contact(Base):
    """Модель для хранения контактов пользователей, которые пишут в бизнес-аккаунты"""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram данные пользователя
    telegram_user_id = Column(BigInteger, index=True, nullable=False)  # ID пользователя в Telegram
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    
    # История изменения username
    username_history = Column(JSON, nullable=True)  # [{"username": "old_name", "changed_at": "2024-01-01T00:00:00"}]
    
    # CRM данные
    rating = Column(Integer, default=1, nullable=False)  # 1-5 звезд
    category = Column(String(50), default='lead', nullable=False)  # lead, client, partner, spam, other
    source = Column(String(50), default='private', nullable=False)  # private, group
    tags = Column(JSON, nullable=True)  # Список тегов: ["vip", "important"]
    notes = Column(Text, nullable=True)
    
    # Бизнес информация
    registration_date = Column(DateTime, nullable=True)  # Дата регистрации аккаунта пользователя
    brand_name = Column(String(255), nullable=True)
    position = Column(String(255), nullable=True)
    years_in_market = Column(Integer, nullable=True)
    
    # Статистика
    total_messages = Column(Integer, default=0, nullable=False)
    last_contact = Column(DateTime, nullable=True)
    
    # Системные поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи с бизнес-аккаунтами (один контакт может писать в несколько бизнес-аккаунтов)
    business_interactions = relationship("ContactBusinessInteraction", back_populates="contact", cascade="all, delete-orphan")


class ContactBusinessInteraction(Base):
    """Модель для связи контактов с бизнес-аккаунтами (многие-ко-многим)"""
    __tablename__ = "contact_business_interactions"

    id = Column(Integer, primary_key=True, index=True)
    
    # Связи
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    business_account_id = Column(Integer, ForeignKey("business_accounts.id"), nullable=False)
    
    # Статистика взаимодействия для каждого бизнес-аккаунта
    messages_count = Column(Integer, default=0, nullable=False)
    first_interaction = Column(DateTime, nullable=False)
    last_interaction = Column(DateTime, nullable=False)
    
    # Дополнительные метаданные для этого взаимодействия
    notes = Column(Text, nullable=True)  # Заметки специфичные для этого бизнес-аккаунта
    status = Column(String(50), default='active', nullable=False)  # active, blocked, archived
    
    # Системные поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    contact = relationship("Contact", back_populates="business_interactions")
    business_account = relationship("BusinessAccount")
    
    # Уникальное ограничение
    __table_args__ = (
        # Один контакт может иметь только одну запись взаимодействия с каждым бизнес-аккаунтом
        {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}
    )

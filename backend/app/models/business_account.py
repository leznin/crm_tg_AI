from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class BusinessAccount(Base):
    """Модель для хранения данных о Telegram Business Accounts"""
    __tablename__ = "business_accounts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram Business Account данные
    business_connection_id = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(BigInteger, index=True, nullable=False)  # ID пользователя Telegram Business Account
    is_enabled = Column(Boolean, default=True, nullable=False)  # Активен ли бот для этого аккаунта
    can_reply = Column(Boolean, default=False, nullable=False)  # Может ли бот отвечать
    
    # Информация о пользователе (кешируется из Telegram API)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    
    # Системные поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    chats = relationship("BusinessChat", back_populates="business_account", cascade="all, delete-orphan")


class BusinessChat(Base):
    """Модель для хранения диалогов Business Account"""
    __tablename__ = "business_chats"

    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram данные
    chat_id = Column(BigInteger, index=True, nullable=False)  # ID чата в Telegram
    business_account_id = Column(Integer, ForeignKey("business_accounts.id"), nullable=False)
    
    # Тип чата
    chat_type = Column(String(50), nullable=False)  # private, group, supergroup, channel
    
    # Информация о чате/пользователе
    title = Column(String(255), nullable=True)  # Для групп
    first_name = Column(String(255), nullable=True)  # Для приватных чатов
    last_name = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    
    # Статистика
    unread_count = Column(Integer, default=0, nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    
    # Системные поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_message_at = Column(DateTime, nullable=True)
    
    # Связи
    business_account = relationship("BusinessAccount", back_populates="chats")
    messages = relationship("BusinessMessage", back_populates="chat", cascade="all, delete-orphan")


class BusinessMessage(Base):
    """Модель для хранения сообщений Business Account"""
    __tablename__ = "business_messages"

    id = Column(Integer, primary_key=True, index=True)
    
    # Telegram данные
    message_id = Column(BigInteger, nullable=False)  # ID сообщения в Telegram
    chat_id = Column(Integer, ForeignKey("business_chats.id"), nullable=False)
    
    # Отправитель
    sender_id = Column(BigInteger, nullable=False)  # ID отправителя в Telegram
    sender_first_name = Column(String(255), nullable=True)
    sender_last_name = Column(String(255), nullable=True)
    sender_username = Column(String(255), nullable=True)
    
    # Содержимое сообщения
    text = Column(Text, nullable=True)
    message_type = Column(String(50), default="text", nullable=False)  # text, photo, document, etc.
    
    # Файлы (если есть)
    file_id = Column(String(255), nullable=True)  # Telegram file_id
    file_unique_id = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)
    file_size = Column(Integer, nullable=True)
    mime_type = Column(String(100), nullable=True)
    
    # Направление сообщения
    is_outgoing = Column(Boolean, default=False, nullable=False)  # True если от бизнес-аккаунта
    
    # Системные поля
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    telegram_date = Column(DateTime, nullable=False)  # Дата из Telegram
    
    # Связи
    chat = relationship("BusinessChat", back_populates="messages")



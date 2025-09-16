from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContactBase(BaseModel):
    """Базовая схема контакта"""
    telegram_user_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    rating: int = Field(default=1, ge=1, le=5)
    category: str = Field(default='lead')  # lead, client, partner, spam, other
    source: str = Field(default='private')  # private, group
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    registration_date: Optional[datetime] = None
    brand_name: Optional[str] = None
    position: Optional[str] = None
    years_in_market: Optional[int] = None


class ContactCreate(ContactBase):
    """Схема для создания контакта"""
    pass


class ContactUpdate(BaseModel):
    """Схема для обновления контакта"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    category: Optional[str] = None
    source: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    registration_date: Optional[datetime] = None
    brand_name: Optional[str] = None
    position: Optional[str] = None
    years_in_market: Optional[int] = None


class UsernameHistory(BaseModel):
    """Схема для истории username"""
    username: str
    changed_at: datetime


class ContactBusinessInteractionBase(BaseModel):
    """Базовая схема взаимодействия контакта с бизнес-аккаунтом"""
    contact_id: int
    business_account_id: int
    messages_count: int = 0
    notes: Optional[str] = None
    status: str = Field(default='active')  # active, blocked, archived


class ContactBusinessInteractionCreate(ContactBusinessInteractionBase):
    """Схема для создания взаимодействия"""
    first_interaction: datetime
    last_interaction: datetime


class ContactBusinessInteractionUpdate(BaseModel):
    """Схема для обновления взаимодействия"""
    messages_count: Optional[int] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    last_interaction: Optional[datetime] = None


class ContactBusinessInteraction(ContactBusinessInteractionBase):
    """Полная схема взаимодействия"""
    id: int
    first_interaction: datetime
    last_interaction: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Contact(ContactBase):
    """Полная схема контакта"""
    id: int
    username_history: Optional[List[UsernameHistory]] = None
    total_messages: int = 0
    last_contact: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    business_interactions: Optional[List[ContactBusinessInteraction]] = None

    class Config:
        from_attributes = True


class ContactWithBusinessAccount(BaseModel):
    """Схема контакта с информацией о бизнес-аккаунте"""
    contact: Contact
    business_account_name: str
    business_account_username: Optional[str] = None
    interaction: ContactBusinessInteraction

    class Config:
        from_attributes = True


class ContactListResponse(BaseModel):
    """Схема ответа со списком контактов"""
    contacts: List[ContactWithBusinessAccount]
    total: int
    page: int
    per_page: int

    class Config:
        from_attributes = True


class ContactStats(BaseModel):
    """Статистика по контактам"""
    total_contacts: int
    new_contacts_today: int
    new_contacts_week: int
    contacts_by_category: Dict[str, int]
    contacts_by_rating: Dict[int, int]
    top_business_accounts: List[Dict[str, Any]]

    class Config:
        from_attributes = True

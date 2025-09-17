from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Business Account schemas
class BusinessAccountBase(BaseModel):
    business_connection_id: str
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_enabled: bool = True
    can_reply: bool = False


class BusinessAccountCreate(BusinessAccountBase):
    pass


class BusinessAccountUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    is_enabled: Optional[bool] = None
    can_reply: Optional[bool] = None


class BusinessAccountResponse(BusinessAccountBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Business Chat schemas
class BusinessChatBase(BaseModel):
    chat_id: int
    chat_type: str
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class BusinessChatResponse(BusinessChatBase):
    id: int
    business_account_id: int
    unread_count: int = 0
    message_count: int = 0
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BusinessChatWithLastMessage(BusinessChatResponse):
    last_message: Optional['BusinessMessageResponse'] = None


# Business Message schemas
class BusinessMessageBase(BaseModel):
    text: Optional[str] = None
    message_type: str = "text"
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    mime_type: Optional[str] = None


class BusinessMessageCreate(BusinessMessageBase):
    message_id: int
    chat_id: int
    sender_id: int
    sender_first_name: Optional[str] = None
    sender_last_name: Optional[str] = None
    sender_username: Optional[str] = None
    is_outgoing: bool = False
    telegram_date: datetime


class BusinessMessageResponse(BusinessMessageBase):
    id: int
    message_id: int
    chat_id: int
    sender_id: int
    sender_first_name: Optional[str] = None
    sender_last_name: Optional[str] = None
    sender_username: Optional[str] = None
    is_outgoing: bool
    created_at: datetime
    telegram_date: datetime
    file_unique_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# Request schemas for API endpoints
class SendMessageRequest(BaseModel):
    business_connection_id: str
    chat_id: int
    text: str
    reply_to_message_id: Optional[int] = None


class SendPhotoRequest(BaseModel):
    business_connection_id: str
    chat_id: int
    photo_file_id: str
    caption: Optional[str] = None
    reply_to_message_id: Optional[int] = None


class SendDocumentRequest(BaseModel):
    business_connection_id: str
    chat_id: int
    document_file_id: str
    caption: Optional[str] = None
    reply_to_message_id: Optional[int] = None


# Response schemas
class BusinessAccountListResponse(BaseModel):
    accounts: List[BusinessAccountResponse]
    total: int


class BusinessChatListResponse(BaseModel):
    chats: List[BusinessChatWithLastMessage]
    total: int


class BusinessMessageListResponse(BaseModel):
    messages: List[BusinessMessageResponse]
    total: int
    has_more: bool


class BusinessAccountStatsResponse(BaseModel):
    chats_count: int
    messages_count: int
    unread_chats_count: int
    account_name: str
    username: Optional[str] = None
    is_enabled: bool


# Webhook schemas
class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None
    business_connection: Optional[Dict[str, Any]] = None
    business_message: Optional[Dict[str, Any]] = None
    edited_business_message: Optional[Dict[str, Any]] = None
    deleted_business_messages: Optional[Dict[str, Any]] = None


# Chat Summary schemas
class ChatSummaryRequest(BaseModel):
    chat_id: int


class ChatSummaryResponse(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str
    last_updated: str


# Chat Suggestions schemas
class ChatSuggestionsRequest(BaseModel):
    chat_id: int


class ChatSuggestionsResponse(BaseModel):
    suggestions: List[str]


# Update forward references
BusinessChatWithLastMessage.model_rebuild()



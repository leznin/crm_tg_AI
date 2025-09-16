from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.business_account_service import BusinessAccountService
from app.schemas.business_account_schema import (
    BusinessAccountListResponse,
    BusinessAccountResponse,
    BusinessChatListResponse,
    BusinessChatWithLastMessage,
    BusinessMessageListResponse,
    BusinessMessageResponse,
    SendMessageRequest,
    SendPhotoRequest,
    SendDocumentRequest,
    BusinessAccountStatsResponse
)

router = APIRouter(prefix="/business-accounts", tags=["business-accounts"])


@router.get("/", response_model=BusinessAccountListResponse)
async def get_business_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all business accounts for the current user"""
    service = BusinessAccountService(db)
    accounts = service.get_all_business_accounts(current_user.id)
    
    return BusinessAccountListResponse(
        accounts=[BusinessAccountResponse.from_orm(acc) for acc in accounts],
        total=len(accounts)
    )


@router.get("/{business_account_id}/stats", response_model=BusinessAccountStatsResponse)
async def get_business_account_stats(
    business_account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for a business account"""
    service = BusinessAccountService(db)
    stats = service.get_business_account_stats(business_account_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Business account not found")
    
    return BusinessAccountStatsResponse(**stats)


@router.get("/{business_account_id}/chats", response_model=BusinessChatListResponse)
async def get_business_account_chats(
    business_account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chats for a business account"""
    service = BusinessAccountService(db)
    chats = service.get_chats_for_business_account(business_account_id)
    
    # Get last message for each chat
    chats_with_messages = []
    for chat in chats:
        messages = service.get_chat_messages(chat.id, limit=1)
        last_message = messages[0] if messages else None
        
        chat_data = BusinessChatWithLastMessage.from_orm(chat)
        if last_message:
            chat_data.last_message = BusinessMessageResponse.from_orm(last_message)
        
        chats_with_messages.append(chat_data)
    
    return BusinessChatListResponse(
        chats=chats_with_messages,
        total=len(chats)
    )


@router.get("/chats/{chat_id}/messages", response_model=BusinessMessageListResponse)
async def get_chat_messages(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat"""
    service = BusinessAccountService(db)
    messages = service.get_chat_messages(chat_id, limit + 1, offset)  # +1 to check if there are more
    
    has_more = len(messages) > limit
    if has_more:
        messages = messages[:limit]
    
    return BusinessMessageListResponse(
        messages=[BusinessMessageResponse.from_orm(msg) for msg in messages],
        total=len(messages),
        has_more=has_more
    )


@router.post("/chats/{chat_id}/mark-read")
async def mark_chat_as_read(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark chat messages as read"""
    service = BusinessAccountService(db)
    service.mark_chat_as_read(chat_id)
    
    return {"success": True, "message": "Chat marked as read"}


@router.post("/send-message")
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a text message to a business chat"""
    service = BusinessAccountService(db)
    
    try:
        result = await service.send_message(
            user_id=current_user.id,
            business_connection_id=request.business_connection_id,
            chat_id=request.chat_id,
            text=request.text,
            reply_to_message_id=request.reply_to_message_id
        )
        
        return {"success": True, "message": "Message sent", "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.post("/send-photo")
async def send_photo(
    request: SendPhotoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a photo to a business chat"""
    service = BusinessAccountService(db)
    
    try:
        result = await service.send_photo(
            user_id=current_user.id,
            business_connection_id=request.business_connection_id,
            chat_id=request.chat_id,
            photo_file_id=request.photo_file_id,
            caption=request.caption,
            reply_to_message_id=request.reply_to_message_id
        )
        
        return {"success": True, "message": "Photo sent", "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send photo: {str(e)}")


@router.post("/send-document")
async def send_document(
    request: SendDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a document to a business chat"""
    service = BusinessAccountService(db)
    
    try:
        result = await service.send_document(
            user_id=current_user.id,
            business_connection_id=request.business_connection_id,
            chat_id=request.chat_id,
            document_file_id=request.document_file_id,
            caption=request.caption,
            reply_to_message_id=request.reply_to_message_id
        )
        
        return {"success": True, "message": "Document sent", "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send document: {str(e)}")


@router.get("/search-messages")
async def search_messages(
    business_account_id: int = Query(...),
    query: str = Query(..., min_length=3),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search messages by text content"""
    service = BusinessAccountService(db)
    messages = service.search_messages(business_account_id, query, limit)
    
    return {
        "messages": [BusinessMessageResponse.from_orm(msg) for msg in messages],
        "total": len(messages),
        "query": query
    }

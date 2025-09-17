import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.business_account_service import BusinessAccountService
from app.services.contact_service import ContactService
from app.schemas.business_account_schema import TelegramUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telegram", tags=["telegram-webhook"])

# Additional router without API prefix for direct webhook access
webhook_router = APIRouter(tags=["telegram-webhook-direct"])


@router.post("/webhook")
async def telegram_webhook(
    update: TelegramUpdate,
    db: Session = Depends(get_db)
):
    """Handle Telegram webhook updates for Business Accounts"""
    logger.info(f"Received webhook update: {update.update_id}")
    service = BusinessAccountService(db)
    contact_service = ContactService(db)
    
    try:
        # Handle business connection events
        if update.business_connection:
            await handle_business_connection(service, update.business_connection)
        
        # Handle business messages
        elif update.business_message:
            await handle_business_message(service, contact_service, update.business_message)
        
        # Handle edited business messages
        elif update.edited_business_message:
            await handle_edited_business_message(service, contact_service, update.edited_business_message)
        
        # Handle deleted business messages
        elif update.deleted_business_messages:
            await handle_deleted_business_messages(service, update.deleted_business_messages)
        
        # Handle regular messages (for bot chats)
        elif update.message:
            await handle_regular_message(service, update.message)
        
        # Handle edited messages
        elif update.edited_message:
            await handle_edited_message(service, update.edited_message)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}", exc_info=True)
        # Don't return error to Telegram to avoid webhook being disabled
        return {"status": "error", "message": str(e)}


async def handle_business_connection(service: BusinessAccountService, connection_data: Dict[str, Any]):
    """Handle business connection events"""
    connection_id = connection_data.get('id')
    user_data = connection_data.get('user', {})
    is_enabled = connection_data.get('is_enabled', True)
    can_reply = connection_data.get('can_reply', True)  # Default to True for new connections
    
    logger.info(f"Business connection event: {connection_id}, enabled: {is_enabled}")
    
    # Always create or update the business account with current status
    service.create_or_update_business_account(
        business_connection_id=connection_id,
        user_id=user_data.get('id'),
        first_name=user_data.get('first_name', ''),
        last_name=user_data.get('last_name'),
        username=user_data.get('username'),
        is_enabled=is_enabled,
        can_reply=can_reply
    )
    
    status_text = "connected" if is_enabled else "disconnected"
    logger.info(f"Business account {connection_id} {status_text}")


async def handle_business_message(service: BusinessAccountService, contact_service: ContactService, message_data: Dict[str, Any]):
    """Handle incoming business messages"""
    business_connection_id = message_data.get('business_connection_id')
    
    if not business_connection_id:
        logger.warning("Received business message without business_connection_id")
        return
    
    # Get business account
    business_account = service.get_business_account_by_connection_id(business_connection_id)
    if not business_account:
        logger.warning(f"Business account not found for connection_id: {business_connection_id}")
        return
    
    # Save message
    message = service.save_incoming_message(business_account, message_data)
    logger.info(f"Saved business message {message.id} from chat {message_data.get('chat', {}).get('id')}")
    
    # Process contact from message data
    try:
        from_user = message_data.get('from', {})
        chat_data = message_data.get('chat', {})
        
        if from_user and from_user.get('id'):
            contact = contact_service.process_message_for_contact(
                telegram_user_id=from_user.get('id'),
                business_account_id=business_account.id,
                first_name=from_user.get('first_name', ''),
                last_name=from_user.get('last_name'),
                username=from_user.get('username'),
                chat_type=chat_data.get('type', 'private')
            )
            logger.info(f"Processed contact {contact.id} for business message")
    except Exception as e:
        logger.error(f"Error processing contact for business message: {e}", exc_info=True)


async def handle_edited_business_message(service: BusinessAccountService, contact_service: ContactService, message_data: Dict[str, Any]):
    """Handle edited business messages"""
    business_connection_id = message_data.get('business_connection_id')
    
    if not business_connection_id:
        logger.warning("Received edited business message without business_connection_id")
        return
    
    # Get business account
    business_account = service.get_business_account_by_connection_id(business_connection_id)
    if not business_account:
        logger.warning(f"Business account not found for connection_id: {business_connection_id}")
        return
    
    # For now, we'll treat edited messages as new messages
    # In a more sophisticated implementation, you might want to update the existing message
    message = service.save_incoming_message(business_account, message_data)
    logger.info(f"Saved edited business message {message.id}")
    
    # Process contact from edited message data (same as regular message)
    try:
        from_user = message_data.get('from', {})
        chat_data = message_data.get('chat', {})
        
        if from_user and from_user.get('id'):
            contact = contact_service.process_message_for_contact(
                telegram_user_id=from_user.get('id'),
                business_account_id=business_account.id,
                first_name=from_user.get('first_name', ''),
                last_name=from_user.get('last_name'),
                username=from_user.get('username'),
                chat_type=chat_data.get('type', 'private')
            )
            logger.info(f"Processed contact {contact.id} for edited business message")
    except Exception as e:
        logger.error(f"Error processing contact for edited business message: {e}", exc_info=True)


async def handle_deleted_business_messages(service: BusinessAccountService, deleted_data: Dict[str, Any]):
    """Handle deleted business messages"""
    business_connection_id = deleted_data.get('business_connection_id')
    message_ids = deleted_data.get('message_ids', [])
    
    logger.info(f"Business messages deleted: {message_ids} from connection {business_connection_id}")
    
    # For now, we'll just log this event
    # In a more sophisticated implementation, you might want to mark messages as deleted
    # or remove them from the database


async def handle_regular_message(service: BusinessAccountService, message_data: Dict[str, Any]):
    """Handle regular bot messages (non-business)"""
    # This is for regular bot chats, not business accounts
    # You might want to handle these differently or ignore them
    logger.info(f"Received regular message: {message_data.get('message_id')}")


async def handle_edited_message(service: BusinessAccountService, message_data: Dict[str, Any]):
    """Handle edited regular messages"""
    # This is for regular bot chats, not business accounts
    logger.info(f"Received edited message: {message_data.get('message_id')}")


# Health check endpoint for webhook
@router.get("/webhook/health")
async def webhook_health():
    """Health check endpoint for webhook"""
    return {"status": "healthy", "message": "Webhook is ready to receive updates"}


# Direct webhook endpoint (without /api/v1 prefix)
@webhook_router.post("/webhook")
async def telegram_webhook_direct(
    update: TelegramUpdate,
    db: Session = Depends(get_db)
):
    """Handle Telegram webhook updates for Business Accounts (direct endpoint)"""
    return await telegram_webhook(update, db)


@webhook_router.get("/webhook/health")
async def webhook_health_direct():
    """Health check endpoint for webhook (direct)"""
    return {"status": "healthy", "message": "Direct webhook is ready to receive updates"}

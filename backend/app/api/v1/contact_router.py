import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.contact_service import ContactService
from app.schemas.contact_schema import (
    Contact, ContactCreate, ContactUpdate, ContactListResponse,
    ContactStats, ContactBusinessInteractionCreate, ContactBusinessInteractionUpdate,
    ContactBusinessInteraction
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=ContactListResponse)
async def get_contacts(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, description="Search query"),
    business_account_id: Optional[int] = Query(None, description="Filter by business account"),
    category: Optional[str] = Query(None, description="Filter by category"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    """Получить список контактов с фильтрацией и пагинацией"""
    service = ContactService(db)
    
    try:
        result = service.search_contacts(
            query=query,
            business_account_id=business_account_id,
            category=category,
            rating=rating,
            tags=tags,
            page=page,
            per_page=per_page
        )
        
        return ContactListResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting contacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/business-account/{business_account_id}")
async def get_contacts_by_business_account(
    business_account_id: int,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Items per page")
):
    """Получить все контакты для определенного бизнес-аккаунта"""
    service = ContactService(db)
    
    try:
        result = service.get_contacts_by_business_account(
            business_account_id=business_account_id,
            page=page,
            per_page=per_page
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting contacts for business account {business_account_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=ContactStats)
async def get_contact_stats(
    db: Session = Depends(get_db),
    business_account_id: Optional[int] = Query(None, description="Filter stats by business account")
):
    """Получить статистику по контактам"""
    service = ContactService(db)
    
    try:
        stats = service.get_contact_stats(business_account_id)
        return ContactStats(**stats)
        
    except Exception as e:
        logger.error(f"Error getting contact stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_contacts(
    db: Session = Depends(get_db),
    business_account_id: Optional[int] = Query(None, description="Filter by business account"),
    limit: int = Query(10, ge=1, le=50, description="Number of contacts to return")
):
    """Получить недавно добавленные контакты"""
    service = ContactService(db)
    
    try:
        contacts = service.get_recent_contacts(business_account_id, limit)
        return {"contacts": contacts}
        
    except Exception as e:
        logger.error(f"Error getting recent contacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-by-messages")
async def get_top_contacts_by_messages(
    db: Session = Depends(get_db),
    business_account_id: Optional[int] = Query(None, description="Filter by business account"),
    limit: int = Query(10, ge=1, le=50, description="Number of contacts to return")
):
    """Получить топ контактов по количеству сообщений"""
    service = ContactService(db)
    
    try:
        contacts = service.get_top_contacts_by_messages(business_account_id, limit)
        return {"contacts": contacts}
        
    except Exception as e:
        logger.error(f"Error getting top contacts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}", response_model=Contact)
async def get_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Получить контакт по ID"""
    service = ContactService(db)
    
    contact = service.get_contact_by_id(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


@router.get("/telegram/{telegram_user_id}", response_model=Contact)
async def get_contact_by_telegram_id(
    telegram_user_id: int,
    db: Session = Depends(get_db)
):
    """Получить контакт по Telegram ID"""
    service = ContactService(db)
    
    contact = service.get_contact_by_telegram_id(telegram_user_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


@router.post("/", response_model=Contact)
async def create_contact(
    contact_data: ContactCreate,
    db: Session = Depends(get_db)
):
    """Создать новый контакт"""
    service = ContactService(db)
    
    try:
        # Проверяем, что контакт с таким telegram_user_id еще не существует
        existing = service.get_contact_by_telegram_id(contact_data.telegram_user_id)
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Contact with telegram_user_id {contact_data.telegram_user_id} already exists"
            )
        
        contact = service.create_contact(contact_data)
        logger.info(f"Created new contact {contact.id}")
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating contact: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{contact_id}", response_model=Contact)
async def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db)
):
    """Обновить контакт"""
    service = ContactService(db)
    
    try:
        contact = service.update_contact(contact_id, contact_data)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Updated contact {contact_id}")
        return contact
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Удалить контакт"""
    service = ContactService(db)
    
    try:
        success = service.delete_contact(contact_id)
        if not success:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Deleted contact {contact_id}")
        return {"message": "Contact deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Операции с взаимодействиями
@router.post("/interactions/", response_model=ContactBusinessInteraction)
async def create_business_interaction(
    interaction_data: ContactBusinessInteractionCreate,
    db: Session = Depends(get_db)
):
    """Создать взаимодействие между контактом и бизнес-аккаунтом"""
    service = ContactService(db)
    
    try:
        # Проверяем, что такое взаимодействие еще не существует
        existing = service.get_business_interaction(
            interaction_data.contact_id,
            interaction_data.business_account_id
        )
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Interaction between this contact and business account already exists"
            )
        
        interaction = service.create_business_interaction(interaction_data)
        logger.info(f"Created business interaction {interaction.id}")
        return interaction
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating business interaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{contact_id}/interactions")
async def get_contact_interactions(
    contact_id: int,
    db: Session = Depends(get_db)
):
    """Получить все взаимодействия контакта с бизнес-аккаунтами"""
    service = ContactService(db)
    
    try:
        interactions = service.get_contact_interactions(contact_id)
        return {"interactions": interactions}
        
    except Exception as e:
        logger.error(f"Error getting contact interactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Операции с тегами
@router.post("/{contact_id}/tags/{tag}")
async def add_contact_tag(
    contact_id: int,
    tag: str,
    db: Session = Depends(get_db)
):
    """Добавить тег к контакту"""
    service = ContactService(db)
    
    try:
        contact = service.add_contact_tag(contact_id, tag)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Added tag '{tag}' to contact {contact_id}")
        return {"message": f"Tag '{tag}' added successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding tag to contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{contact_id}/tags/{tag}")
async def remove_contact_tag(
    contact_id: int,
    tag: str,
    db: Session = Depends(get_db)
):
    """Удалить тег у контакта"""
    service = ContactService(db)
    
    try:
        contact = service.remove_contact_tag(contact_id, tag)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Removed tag '{tag}' from contact {contact_id}")
        return {"message": f"Tag '{tag}' removed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing tag from contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Операции с рейтингом
@router.put("/{contact_id}/rating/{rating}")
async def update_contact_rating(
    contact_id: int,
    rating: int,
    db: Session = Depends(get_db)
):
    """Обновить рейтинг контакта"""
    service = ContactService(db)
    
    try:
        contact = service.update_contact_rating(contact_id, rating)
        if not contact:
            raise HTTPException(status_code=404, detail="Contact not found")
        
        logger.info(f"Updated rating for contact {contact_id} to {rating}")
        return {"message": f"Rating updated to {rating}"}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rating for contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Операции блокировки
@router.post("/{contact_id}/block/{business_account_id}")
async def block_contact_for_business(
    contact_id: int,
    business_account_id: int,
    reason: Optional[str] = Query(None, description="Reason for blocking"),
    db: Session = Depends(get_db)
):
    """Заблокировать контакт для определенного бизнес-аккаунта"""
    service = ContactService(db)
    
    try:
        interaction = service.block_contact_for_business(contact_id, business_account_id, reason)
        if not interaction:
            raise HTTPException(
                status_code=404,
                detail="Interaction between contact and business account not found"
            )
        
        logger.info(f"Blocked contact {contact_id} for business account {business_account_id}")
        return {"message": "Contact blocked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error blocking contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{contact_id}/unblock/{business_account_id}")
async def unblock_contact_for_business(
    contact_id: int,
    business_account_id: int,
    db: Session = Depends(get_db)
):
    """Разблокировать контакт для определенного бизнес-аккаунта"""
    service = ContactService(db)
    
    try:
        interaction = service.unblock_contact_for_business(contact_id, business_account_id)
        if not interaction:
            raise HTTPException(
                status_code=404,
                detail="Interaction between contact and business account not found"
            )
        
        logger.info(f"Unblocked contact {contact_id} for business account {business_account_id}")
        return {"message": "Contact unblocked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unblocking contact {contact_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

import os
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import httpx

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.services.business_account_service import BusinessAccountService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["file-upload"])


@router.post("/upload-to-telegram")
async def upload_file_to_telegram(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload file to Telegram and return file_id for sending"""
    service = BusinessAccountService(db)
    
    try:
        # Get bot token
        bot_token = await service.get_telegram_bot_token(current_user.id)
        if not bot_token:
            raise HTTPException(status_code=400, detail="Telegram bot token not configured")
        
        # Read file content
        file_content = await file.read()
        
        # Determine upload method based on file type
        if file.content_type and file.content_type.startswith('image/'):
            method = 'sendPhoto'
            file_param = 'photo'
        else:
            method = 'sendDocument'
            file_param = 'document'
        
        # Create a temporary chat with the bot to upload the file
        # We'll use the bot's own user_id as chat_id (this is a common pattern)
        url = f"https://api.telegram.org/bot{bot_token}/{method}"
        
        # Prepare multipart form data
        files = {
            file_param: (file.filename, file_content, file.content_type)
        }
        
        # Use a dummy chat_id - we'll get the file_id from the response
        # and then delete the message
        data = {
            'chat_id': '@' + bot_token.split(':')[0]  # Use bot's own id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, files=files, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            
            if not result.get('ok'):
                logger.error(f"Telegram file upload error: {result}")
                raise HTTPException(status_code=400, detail=f"Telegram API error: {result.get('description')}")
            
            message = result.get('result', {})
            
            # Extract file_id based on message type
            file_id = None
            file_unique_id = None
            file_size = None
            
            if message.get('photo'):
                # Get the largest photo
                photos = message['photo']
                largest_photo = max(photos, key=lambda x: x.get('file_size', 0))
                file_id = largest_photo.get('file_id')
                file_unique_id = largest_photo.get('file_unique_id')
                file_size = largest_photo.get('file_size')
            elif message.get('document'):
                doc = message['document']
                file_id = doc.get('file_id')
                file_unique_id = doc.get('file_unique_id')
                file_size = doc.get('file_size')
            
            # Try to delete the temporary message
            try:
                delete_url = f"https://api.telegram.org/bot{bot_token}/deleteMessage"
                await client.post(delete_url, json={
                    'chat_id': data['chat_id'],
                    'message_id': message.get('message_id')
                })
            except:
                # Ignore deletion errors
                pass
            
            return {
                'success': True,
                'file_id': file_id,
                'file_unique_id': file_unique_id,
                'file_name': file.filename,
                'file_size': file_size,
                'content_type': file.content_type,
                'message_type': 'photo' if file.content_type and file.content_type.startswith('image/') else 'document'
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during file upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during file upload: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/send-uploaded-file")
async def send_uploaded_file(
    business_connection_id: str = Form(...),
    chat_id: int = Form(...),
    file_id: str = Form(...),
    message_type: str = Form(...),  # 'photo' or 'document'
    caption: str = Form(None),
    reply_to_message_id: int = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send previously uploaded file to a business chat"""
    service = BusinessAccountService(db)
    
    try:
        if message_type == 'photo':
            result = await service.send_photo(
                user_id=current_user.id,
                business_connection_id=business_connection_id,
                chat_id=chat_id,
                photo_file_id=file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        elif message_type == 'document':
            result = await service.send_document(
                user_id=current_user.id,
                business_connection_id=business_connection_id,
                chat_id=chat_id,
                document_file_id=file_id,
                caption=caption,
                reply_to_message_id=reply_to_message_id
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid message type")
        
        return {
            'success': True,
            'message': f'{message_type.title()} sent successfully',
            'result': result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send {message_type}: {str(e)}")


@router.get("/download-from-telegram")
async def download_file_from_telegram(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for a file from Telegram"""
    service = BusinessAccountService(db)
    
    try:
        # Get bot token
        bot_token = await service.get_telegram_bot_token(current_user.id)
        if not bot_token:
            raise HTTPException(status_code=400, detail="Telegram bot token not configured")
        
        # Get file info from Telegram
        url = f"https://api.telegram.org/bot{bot_token}/getFile"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={'file_id': file_id})
            response.raise_for_status()
            result = response.json()
            
            if not result.get('ok'):
                logger.error(f"Telegram getFile error: {result}")
                raise HTTPException(status_code=400, detail=f"Telegram API error: {result.get('description')}")
            
            file_info = result.get('result', {})
            file_path = file_info.get('file_path')
            
            if not file_path:
                raise HTTPException(status_code=404, detail="File not found or expired")
            
            download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
            
            return {
                'success': True,
                'download_url': download_url,
                'file_path': file_path,
                'file_size': file_info.get('file_size')
            }
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error during file info request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during file info request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get file info: {str(e)}")



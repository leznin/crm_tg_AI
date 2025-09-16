from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models here to ensure they are registered with SQLAlchemy
from app.models.user import User
from app.models.settings import ApiKey, OpenRouterModel, Prompt
from app.models.business_account import BusinessAccount, BusinessChat, BusinessMessage
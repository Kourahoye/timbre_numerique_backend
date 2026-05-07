import json
import strawberry
import strawberry_django
from timbre.models import Notification, PriceAssignation, Session, Timbre, Transaction, TypeTimbre
from users.models import User

@strawberry_django.type(User)
class UserTypeMIN:
    id: strawberry.ID
    username: str
    email: str | None = None


@strawberry.type
class AuthPermType:#retrun user permissions
    id: strawberry.ID
    name: str
    
@strawberry.type
class Message:
    success: bool
    message: str

@strawberry_django.type(Session)
class SessionTyoe:
    id:strawberry.ID
    name:str
    
@strawberry_django.type(Session)
class SessionTypeDetail:
    id:strawberry.ID
    name:str
    active:bool
    start_date:str
    end_date:str
    created_at:str
    updated_at:str
    created_by:UserTypeMIN
    updated_by:UserTypeMIN
    

@strawberry_django.type(TypeTimbre)
class TypeTimbreType:
    id:strawberry.ID
    name:str 
    
@strawberry_django.type(TypeTimbre)
class TypeTimbreDetailsType:
    id:strawberry.ID
    name:str
    created_at:str
    updated_at:str
    created_by:UserTypeMIN
    updated_by:UserTypeMIN
    
@strawberry_django.type(PriceAssignation)
class PriceAssignationType:
    id:strawberry.ID
    session: SessionTyoe
    type:TypeTimbreType
    price:float
    created_at:str
    updated_at:str
    created_by:UserTypeMIN
    updated_by:UserTypeMIN
    
@strawberry_django.type(Timbre)
class TimbreType:
    id:strawberry.ID
    reference:str
    price:PriceAssignationType
    type:TypeTimbreType
    used:bool
    qrCode:str
    owned_by:UserTypeMIN
    
@strawberry_django.type(Notification)
class NotificationType:
    id:strawberry.ID
    content:str
    user:UserTypeMIN
    read:bool
    link:strawberry.auto
    created_at:str
    updated_at:str
    
@strawberry_django.type(Transaction)
class TransactionType:
    id:strawberry.ID
    timbre:TimbreType
    status:str
    created_at:str
    updated_at:str
    controller:UserTypeMIN
    updated_by:UserTypeMIN

@strawberry.type
class TransactionTypeDetails:
    id:strawberry.ID
    timbre:TimbreType
    status:str
    created_at:str
    updated_at:str
    controller:UserTypeMIN
    updated_by:UserTypeMIN
    

@strawberry_django.type(Notification)
class NotificationType:
    id:strawberry.ID
    content:str
    read:bool
    link:strawberry.auto
    created_at:str
    

@strawberry.type
class DashboardStats:
    total_timbres: int
    used_timbres: int
    unused_timbres: int
    total_revenue: float             # somme price.price des timbres vendus

    pending_transactions: int
    accepted_transactions: int
    rejected_transactions: int

    active_session: SessionTyoe
    unread_notifications: int        # pour l'utilisateur connecté
    total_users: int
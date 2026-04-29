import strawberry
import strawberry_django
from timbre.models import PriceAssignation, Session, Timbre, TypeTimbre
from users.models import User

@strawberry_django.type(User)
class UserTypeMIN:
    id: strawberry.ID
    username: str
    email: str | None = None


@strawberry.type
class Message:
    success: bool
    message: str

@strawberry_django.type(Session)
class SessionTyoe:
    id:strawberry.ID
    name:str

    

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
    
@strawberry_django.type(Timbre)
class TimbreType:
    id:strawberry.ID
    reference:str
    type:TypeTimbreType
    used:bool
    qrCode:str
    owned_by:strawberry.auto
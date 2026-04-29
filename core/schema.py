from random import randint
from sqlite3 import Date
from django.forms import ValidationError
import strawberry
from core.permissions import IsAuthenticated
from gqlauth.core.middlewares import JwtSchema
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from gqlauth.user import arg_mutations as mutations
from gqlauth.user.queries import UserQueries
from timbre.models import PriceAssignation, Session, Timbre, TypeTimbre
from timbre.types import Message, PriceAssignationType, SessionTyoe, TimbreType, TypeTimbreDetailsType, TypeTimbreType
from users.models import User



# @strawberry.django.type(model=get_user_model())
# class MyQueries:
#     me: UserType = UserQueries.me
#     public: UserType = UserQueries.public_user
 
 
@strawberry.type
class Query(UserQueries):
    sessions:list[SessionTyoe]
    timbreType:list[TypeTimbreType]
    getTimbresType:list[TypeTimbreDetailsType]
    prices:list[PriceAssignationType]
    scan:TimbreType
    myTimbres:list[TimbreType]
    
    
    @strawberry.field()
    def sessions(self):
        sessions = Session.objects.all()
        return sessions
    
    @strawberry.field()
    def timbreType(self):
        timbreType = TypeTimbre.objects.all()
        return timbreType
    
    @strawberry.field()
    def getTimbresType(self):
        timbreType = TypeTimbre.objects.all()
        return timbreType
    
    @strawberry.field()
    def prices(self):
        prices = PriceAssignation.objects.all()
        return prices
    
    @strawberry.field()
    def scan(self,code:str):
        ref,owner,secret = code.split("|")
        usr = User.objects.get(username=owner)
        timbre = Timbre.objects.get(reference=ref,owned_by=usr,secret=secret)
        return timbre
    
    @strawberry.field()
    def myTimbres(self,info:strawberry.types.Info):
        user = info.context.request.user
        timbres = Timbre.objects.filter(owned_by=user).order_by("-created_at")
        return timbres
    
@strawberry.type
class Mutation:
    register = mutations.Register.field
    verify_account = mutations.VerifyAccount.field
    token_auth = mutations.ObtainJSONWebToken.field
    refresh_token = mutations.RefreshToken.field
    
    @strawberry.mutation()
    def add_session(self,name:str,start:Date,end:Date) ->SessionTyoe:
        user = User.objects.get(pk=1)
        if start > end:
            raise ValidationError(message="Start date must be before end date")
        session =  Session.objects.create(name=name,start_date=start,end_date=end,created_by=user,updated_by=user)
        return session
    
    @strawberry.mutation()
    def change_session_name(self,id:int,name:str) ->SessionTyoe:
        user = User.objects.get(pk=1)
        session =  Session.objects.get(pk=id)
        session.name = name
        session.updated_by = user
        session.save()
        return session
    
    @strawberry.mutation()
    def change_session_date(self,id:int,start:Date,end:Date) ->SessionTyoe:
        user = User.objects.get(pk=1)
        session = Session.objects.get(pk=id)
        session.start_date = start
        session.end_date = end
        session.updated_by = user
        session.save()
        return session
    
    @strawberry.mutation()
    def delete_session(self,id:int) -> Message:
        try:
            session = Session.objects.get(pk=id)
            session.delete()
            return Message(success=True,message="Session deleted")
        except Session.DoesNotExist:
            return Message(success=False,message="Session not found") 
    
    @strawberry.mutation()
    def add_timre_type(self,name:str) -> TypeTimbreType:
        user = User.objects.get(pk=1)
        timbre_type = TypeTimbre.objects.create(name = name,created_by=user,updated_by=user)
        return timbre_type
    
    @strawberry.mutation()
    def change_timbre_type_name(self,id:int,name:str) -> TypeTimbreType:
        user = User.objects.get(pk=1)
        timbre_type = TypeTimbre.objects.get(pk=id)
        timbre_type.updated_by=user
        timbre_type.save()
        return timbre_type

    @strawberry.mutation()
    def delete_type_timbre(self,id:int) -> Message:
        try:
            typeTimbre = TypeTimbre.objects.get(pk=id)
            typeTimbre.delete()
            return Message(success=True,message="Type timbre deleted")
        except TypeTimbre.DoesNotExist:
            return Message(success=False,message="Type timbre not found")
    
    @strawberry.mutation()
    def assign_price(self,type_id:int,session_id:int,price:int) -> PriceAssignationType:
        type= TypeTimbre.objects.get(id=type_id)
        session = Session.objects.get(id=session_id)
        user = User.objects.get(pk=1)
        price_assignation = PriceAssignation.objects.create(type=type,session=session,price=price,created_by=user,updated_by=user)
        return price_assignation
    
    @strawberry.mutation()
    def change_price(self,id:int,price:int) ->PriceAssignationType:
        user = User.objects.get(pk=1)
        price_assignation = PriceAssignation.objects.get(pk=id)
        price_assignation.price = price
        price_assignation.updated_by = user
        price_assignation.save()
        return price_assignation
    
    @strawberry.mutation()
    def delete_price(self,id:int) ->Message:
        try:
            price_assignation = PriceAssignation.objects.get(pk=id)
            price_assignation.delete()
            return Message(success=True,message="Assignation supprimer")
        except PriceAssignation.DoesNotExist:
            return Message(success=False,message="Assignation introuvable")
    
    @strawberry.mutation()
    def generate_timbre(self,type_id:int)-> TimbreType:
        type = TypeTimbre.objects.get(pk=type_id)
        user = User.objects.get(pk=1)
        nb= Timbre.objects.all().count()+1
        reference = f"TMB-0000{nb}"
        secret = randint(500,nb*500)
        qrcode= f"{reference}|{user}|{secret}"
        timbre = Timbre.objects.create(reference=reference,type=type,qrCode=qrcode,secret=secret,owned_by=user)
        return timbre
    
    @strawberry.mutation()
    def desactivate(self,id:int) -> Message:
        try:
            timbre = Timbre.objects.get(pk=id) 
            timbre.used = True
            timbre.save()
            return Message(success=True,message="Timbre Used")
        except Timbre.DoesNotExist:
            return Message(success=False,message="Timbre not found")
            
    @strawberry.mutation()
    def delete_timbre(self,id:int) -> Message:
        try:
            timbre = Timbre.objects.get(pk=id)
            timbre.adelete()
            return Message(success=True,message="Timbre supprimer")
        except Timbre.DoesNotExist:
            return Message(success=False,message="Timbre Not found")
    
    
    
        
    

schema = JwtSchema(query=Query, mutation=Mutation)
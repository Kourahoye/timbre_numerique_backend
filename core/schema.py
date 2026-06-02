from random import randint
from sqlite3 import Date
from django.forms import ValidationError
from django.utils import translation
import strawberry
from core.middleware import LanguageExtension
from core.models import Achat
from core.permissions import IsAuthenticated
from gqlauth.core.middlewares import JwtSchema
from gqlauth.user import arg_mutations as mutations
from gqlauth.user.queries import UserQueries
from timbre.models import Notification, PriceAssignation, Session, Timbre, Transaction, TypeTimbre
from timbre.services.djomy import create_payment
from timbre.types import AuthPermType, DashboardStats, Message, NotificationType, PaymentResponse, PriceAssignationType, SessionTyoe, SessionTypeDetail, TimbreType, TransactionType, TransactionTypeDetails, TypeTimbreDetailsType, TypeTimbreType, UserTypeMIN
from users.models import User
from django.db.models import F
from django.db import connection
from django.utils.translation import gettext as _
from strawberry.types import Info
 
@strawberry.type
class Query(UserQueries):
    sessions:list[SessionTyoe]
    timbreType:list[TypeTimbreType]
    getTimbresType:list[TypeTimbreDetailsType]
    prices:list[PriceAssignationType]
    active_session_price=list[PriceAssignationType]
    scan:TimbreType
    myTimbres:list[TimbreType]
    perms:list[AuthPermType]
    users:list[UserTypeMIN]
    sessionInfos:list[SessionTypeDetail]
    get_timbre_price:PriceAssignationType
    notifications:list[NotificationType]
    all_notifications:list[NotificationType]
    new_notis_count:int
    find_transaction:TransactionTypeDetails
    my_transactions:list[TransactionTypeDetails]
    timbres : list[TimbreType]
    transactions:list[TransactionTypeDetails]
    
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def users(self,info:strawberry.types.Info):
        users = User.objects.all()
        return users
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def perms(self,info:strawberry.types.Info):
        user = info.context.request.user
        perms = user.get_all_permissions()
        return [AuthPermType(id=i,name=perm) for i,perm in enumerate(perms)]
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def sessionInfos(self,info:strawberry.types.Info):
        sessions = Session.objects.all().order_by("created_at")
        return sessions
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def sessions(self,info:strawberry.types.Info):
        sessions = Session.objects.all()
        return sessions
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def timbreType(self,info:strawberry.types.Info):
        timbreType = TypeTimbre.objects.all()
        return timbreType
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def timbres(self,info:strawberry.types.Info):
        user = info.context.request.user
        timbre = Timbre.objects.all()
        return timbre
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def getTimbresType(self,info:strawberry.types.Info):
        timbreType = TypeTimbre.objects.all()
        return timbreType
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def prices(self,info:strawberry.types.Info):
        prices = PriceAssignation.objects.all().order_by("-created_at")
        return prices
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def scan(self,code:str,info:strawberry.types.Info):
        # lang = translation.get_language()
        # print(f">>> Langue active: {lang}")  
        try:
            ref,owner,secret = code.split("|")
            usr = User.objects.get(username=owner)
            timbre = Timbre.objects.get(reference=ref,owned_by=usr,secret=secret)
            return timbre
        except Timbre.DoesNotExist:
            raise ValidationError(message=_("timbre.unknown"))
        except User.DoesNotExist:
            raise ValidationError(message=_("user.unknown"))         
        except Exception :#excepted for split error
            raise ValidationError(message=_("qrcode.wrong_format"))
        
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def myTimbres(self,info:strawberry.types.Info):
        user = info.context.request.user
        timbres = Timbre.objects.filter(owned_by=user).order_by("-created_at")
        return timbres
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def get_timbre_price(self,id:int,info:strawberry.types.Info):
        session = Session.objects.get(active=True)
        if not session:
            raise ValidationError(message=_("session.none_active"))
        price = PriceAssignation.objects.get(type_id=id,session=session)
        return price
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def active_session_price(self,info:strawberry.types.Info) -> list[PriceAssignationType]:
        prices_current = PriceAssignation.objects.filter(session__active=True)
        return prices_current
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def notifications(self,info:strawberry.types.Info):
        user = info.context.request.user
        notifications = Notification.objects.filter(read=False,user=user)
        return notifications 
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def new_notis_count(self,info:strawberry.types.Info):
        user = info.context.request.user
        notifications = Notification.objects.filter(read=False,user=user).count()
        return notifications
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def all_notifications(self,info:strawberry.types.Info):
        user = info.context.request.user
        notifications = Notification.objects.filter(user=user)
        return notifications
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def find_transaction(self,id:int,info:strawberry.types.Info):
        transaction = Transaction.objects.get(id=id)
        return transaction
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def my_transactions(self,info:strawberry.types.Info):
        user = info.context.request.user
        transaction = Transaction.objects.filter(timbre__owned_by=user)
        return transaction
    
    @strawberry.field(permission_classes=[IsAuthenticated])
    def transactions(self,info:strawberry.types.Info):
        transaction = Transaction.objects.all()
        return transaction
    
    from django.db import connection

    @strawberry.field
    def dashboard_stats(self, info:strawberry.types.Info) -> DashboardStats:
        user = info.context.request.user

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    -- timbres
                    COUNT(t.id)                                         AS total_timbres,
                    COUNT(t.id) FILTER (WHERE t.used = TRUE)            AS used_timbres,
                    COUNT(t.id) FILTER (WHERE t.used = FALSE)           AS unused_timbres,
                    COALESCE(SUM(pa.price) FILTER (WHERE t.used=TRUE), 0) AS total_revenue,

                    -- transactions
                    (SELECT COUNT(*) FROM timbre_transaction
                    WHERE status = 'pending')                          AS pending_transactions,
                    (SELECT COUNT(*) FROM timbre_transaction
                    WHERE status = 'accepted')                         AS accepted_transactions,
                    (SELECT COUNT(*) FROM timbre_transaction
                    WHERE status = 'rejected')                         AS rejected_transactions,

                    -- notifications non lues
                    (SELECT COUNT(*) FROM timbre_notification
                    WHERE user_id = %s AND read = FALSE)               AS unread_notifications,

                    -- total users
                    (SELECT COUNT(*) FROM users_user)                   AS total_users

                FROM timbre_timbre t
                LEFT JOIN timbre_priceassignation pa ON pa.id = t.price_id
            """, [user.pk])

            row = cursor.fetchone()
            (
                total, used, unused, revenue,
                pending, accepted, rejected,
                unread, total_users
            ) = row

        active_session = Session.objects.filter(active=True).first()

        return DashboardStats(
            total_timbres=total,
            used_timbres=used,
            unused_timbres=unused,
            total_revenue=float(revenue),
            pending_transactions=pending,
            accepted_transactions=accepted,
            rejected_transactions=rejected,
            active_session=active_session,
            unread_notifications=unread,
            total_users=total_users,
        )
    
    
@strawberry.type
class Mutation:
    register = mutations.Register.field
    verify_account = mutations.VerifyAccount.field
    token_auth = mutations.ObtainJSONWebToken.field
    refresh_token = mutations.RefreshToken.field
    logout = mutations.RevokeToken.field
    change_password = mutations.PasswordChange.field
    verify_account = mutations.VerifyAccount.field
    
    @strawberry.mutation()
    def assign_role(self,user_id:int,role:str,info:strawberry.types.Info) -> Message:
        try:
            if role not in ["admin","controller","user"]:
                return Message(success=False,message=_("roles.invalid"))       
            user = User.objects.get(pk=user_id)
            me = User.objects.get(pk=info.context.request.user.id)
            if me.role == user.role:
                return Message(success=False,message=_("roles.same_role"))
            if me.role == "controller":
                if role == "admin":
                    return Message(success=False,message=_("roles.controller_cannot_give_admin"))
                elif user.role == "controller":
                    return Message(success=False,message=_("roles.controller_cannot_change_controller"))
                elif user.role == "admin":
                    return Message(success=False,message=_("roles.controller_cannot_change_admin"))   
            if me == user:
                return Message(success=False,message=_("roles.cannot_change_own_role"))   
            user.role = role
            user.save()
            return Message(success=True,message=_("roles.assigned") % {"role": role, "username": user.username})
        except User.DoesNotExist:
            return Message(success=False,message=_("roles.user_not_found"))
    
    @strawberry.mutation()
    def changeFirstName(self,nom:str,info:strawberry.types.Info)->Message:
        try:
            user = info.context.request.user
            user.first_name = nom
            user.save()
            return Message(success=True,message=_("user.first_name_changed"))
        except Exception:
            return Message(success=False,message=_("user.first_name_change_failed"))
    
    @strawberry.mutation()
    def changeLastName(self,nom:str,info:strawberry.types.Info)->Message:
        try:
            user = info.context.request.user
            user.last_name = nom
            user.save()
            return Message(success=True,message=_("user.last_name_changed"))
        except Exception:
            return Message(success=False,message=_("user.last_name_change_failed"))
        
    @strawberry.mutation()
    def add_session(self,name:str,start:Date,end:Date,info:strawberry.types.Info) ->SessionTyoe:
        user = info.context.request.user
        if start > end:
            raise ValidationError(message=_("session.start_after_end"))
        session =  Session.objects.create(name=name,start_date=start,end_date=end,created_by=user,updated_by=user)
        return session
    
    @strawberry.mutation()
    def change_session_name(self,id:int,name:str,info:strawberry.types.Info) ->SessionTyoe:
        user = info.context.request.user
        session =  Session.objects.get(pk=id)
        session.name = name
        session.updated_by = user
        session.save()
        return session
    
    @strawberry.mutation()
    def change_session_date(self,id:int,start:Date,end:Date,info:strawberry.types.Info) ->SessionTyoe:
        user = info.context.request.user
        session = Session.objects.get(pk=id)
        session.start_date = start
        session.end_date = end
        session.updated_by = user
        session.save()
        return session
    
    @strawberry.mutation()
    def toogle_active_session(self,id:int,info:strawberry.types.Info) -> Message:
        try:
            user = info.context.request.user
            session = Session.objects.get(pk=id)
            if not session.active:
                session_active = Session.objects.filter(active=True)
                session_active.update(updated_by = user,active = False)
                session.active = True          
                session.updated_by = user
                session.save()
                return Message(success=True,message=_("session.activated"))
            else:
                session.active = False
                session.save()
                return Message(success=True,message=_("session.deactivated"))
        except Session.DoesNotExist:
            return Message(success=False,message=_("session.not_found")) 
        
    
    @strawberry.mutation()
    def delete_session(self,id:int,info:strawberry.types.Info) -> Message:
        try:
            session = Session.objects.get(pk=id)
            session.delete()
            return Message(success=True,message=_("session.deleted"))
        except Session.DoesNotExist:
            return Message(success=False,message=_("session.not_found")) 
    
    @strawberry.mutation()
    def add_timre_type(self,name:str,info:strawberry.types.Info) -> TypeTimbreType:
        user = info.context.request.user
        timbre_type = TypeTimbre.objects.create(name = name,created_by=user,updated_by=user)
        return timbre_type
    
    @strawberry.mutation()
    def change_timbre_type_name(self,id:int,name:str,info:strawberry.types.Info) -> TypeTimbreType:
        user = info.context.request.user
        timbre_type = TypeTimbre.objects.get(pk=id)
        timbre_type.updated_by=user
        timbre_type.save()
        return timbre_type

    @strawberry.mutation()
    def delete_type_timbre(self,id:int,info:strawberry.types.Info) -> Message:
        try:
            typeTimbre = TypeTimbre.objects.get(pk=id)
            typeTimbre.delete()
            return Message(success=True,message=_("timbre_type.deleted"))
        except TypeTimbre.DoesNotExist:
            return Message(success=False,message=_("timbre_type.not_found"))
    
    @strawberry.mutation()
    def assign_price(self,type_id:int,session_id:int,price:int,info:strawberry.types.Info) -> PriceAssignationType:
        type= TypeTimbre.objects.get(id=type_id)
        session = Session.objects.get(id=session_id)
        user = info.context.request.user
        price_assignation = PriceAssignation.objects.create(type=type,session=session,price=price,created_by=user,updated_by=user)
        return price_assignation
    
    @strawberry.mutation()
    def change_price(self,id:int,price:int,info:strawberry.types.Info) ->PriceAssignationType:
        user = info.context.request.user
        price_assignation = PriceAssignation.objects.get(pk=id)
        price_assignation.price = price
        price_assignation.updated_by = user
        price_assignation.save()
        return price_assignation
    
    @strawberry.mutation()
    def delete_price(self,id:int,info:strawberry.types.Info) ->Message:
        try:
            price_assignation = PriceAssignation.objects.get(pk=id)
            price_assignation.delete()
            return Message(success=True,message=_("price.deleted"))
        except PriceAssignation.DoesNotExist:
            return Message(success=False,message=_("price.not_found"))
    
    @strawberry.mutation()
    def generate_timbre(self,type_id:int,info:strawberry.types.Info)-> TimbreType:
        type = TypeTimbre.objects.get(pk=type_id)
        assign = PriceAssignation.objects.get(type=type)
        user = info.context.request.user
        nb= Timbre.objects.all().count()+1
        reference = f"TMB-00000{nb}"
        secret = randint(500,nb*500)
        qrcode= f"{reference}|{user}|{secret}"
        timbre = Timbre.objects.create(reference=reference,type=type,qrCode=qrcode,secret=secret,owned_by=user,price=assign)
        return timbre
    
    @strawberry.mutation()
    def desactivate(self,id:int,info:strawberry.types.Info) -> Message:
        try:
            timbre = Timbre.objects.get(pk=id) 
            timbre.used = True
            timbre.save()
            return Message(success=True,message=_("timbre.used"))
        except Timbre.DoesNotExist:
            return Message(success=False,message=_("timbre.not_found"))
            
    @strawberry.mutation()
    def delete_timbre(self,id:int,info:strawberry.types.Info) -> Message:
        try:
            timbre = Timbre.objects.get(pk=id)
            timbre.adelete()
            return Message(success=True,message=_("timbre.deleted"))
        except Timbre.DoesNotExist:
            return Message(success=False,message=_("timbre.not_found"))
        
    @strawberry.mutation()
    def init_transaction(self,timbre:int,info:strawberry.types.Info) -> TransactionType:
        user = info.context.request.user
        _timbre = Timbre.objects.get(pk=timbre)
        if _timbre.used:
            raise ValidationError(message=_("timbre.already_used"))
        # test_transction = Transaction.objects.get(timbre=timbre)
        # if test_transction.status
        transaction = Transaction.objects.create(timbre_id=timbre,controller=user,updated_by=user)
        return transaction
    
    @strawberry.mutation()
    def transaction_observe(self,trasnctionId:int,info:strawberry.types.Info) -> TransactionType:
        user = info.context.request.user
        transation = Transaction.objects.get(id=trasnctionId)
        if user.role  == "user" and transation.timbre.owned_by != user:
            raise ValidationError(message=_("transaction.cannot_observe"))
        return transation
               
    @strawberry.mutation()
    def end_transactions(self,transactionId:int,action:str,info:strawberry.types.Info)->Message:
        try:
            actions_allowed = ("accepted","rejected")
            if not action in actions_allowed:
                raise ValidationError(message=_("transaction.action_unknown"))
            user = info.context.request.user
            transaction = Transaction.objects.get(pk=transactionId)
            timbre = Timbre.objects.get(id=transaction.timbre.id)
            other_transaction = Transaction.objects.filter(timbre=timbre).exclude(pk=transactionId)
            if (transaction.timbre.owned_by != user):
                raise ValidationError(message=_("transaction.cannot_end_others")) 
            if timbre.used:
                raise ValidationError(message=_("timbre.already_used"))       
            if transaction.status != "pending":
                raise ValidationError(message=_("transaction.already_finished"))
            if other_transaction:
                other_transaction.update(updated_by = user,status="rejected")   
            transaction.status = action
            transaction.updated_by = user
            transaction.save()
            timbre.used = True
            timbre.save()
            return Message(success=True,message=_("transaction.%s" % action))
        except Transaction.DoesNotExist:
           return  Message(success=False,message=_("transaction.not_found"))
        except Timbre.DoesNotExist:
           return Message(success=False,message=_("transaction.timbre_not_found"))
        

    @strawberry.mutation()
    def mark_all_as_read(self,info:strawberry.types.Info) -> Message:
        user = info.context.request.user
        notifs = Notification.objects.filter(user=user,read=False)
        notifs.update(read=True)
        return Message(success=True,message=_("notifications.all_read"))
    
    @strawberry.mutation()
    def mark_as_read(self,id:int,info:strawberry.types.Info) -> Message:
        user = info.context.request.user
        notif = Notification.objects.get(id=id)
        notif.read = True
        notif.save()
        return Message(success=True,message=_("notifications.read"))
    
    @strawberry.mutation()
    def initiate_payment(
        self,
        phone: str,
        amount: int,
        type:int,
        info:strawberry.types.Info
    ) -> PaymentResponse:
        user = info.context.request.user
        response = create_payment(phone, amount)
        # print(response)
        payment_url = response["redirectUrl"]
        reference = response["merchantPaymentReference"]

        Achat.objects.create(
            reference=reference,
            phone=phone,
            amount=amount,
            user=user,
            type=TypeTimbre.objects.get(pk=type)
        )
        Notification.objects.create(
            user=user,
            content=f"Paiement en attente de confirmation:\n Montant:{amount}\nTelephone:{phone}\ntransactionId:{reference}\n{payment_url}",
        )

        return PaymentResponse(
            payment_url=payment_url,
            reference=reference,
        )
        
    @strawberry.mutation()
    def set_language(self, info: Info, language_code: str) -> bool:
        from django.conf import settings
        if language_code in dict(settings.LANGUAGES):
            info.context.request.session['_language'] = language_code
            translation.activate(language_code)
            return True
        return False
        
schema = JwtSchema(query=Query, mutation=Mutation,extensions=[LanguageExtension])
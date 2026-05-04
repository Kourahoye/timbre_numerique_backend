from django.db import models
from django.forms import ValidationError
from users.models import User
from  django.db.models.constraints import CheckConstraint, UniqueConstraint
from django.db.models import Q
# Create your models here.

class Session(models.Model):
    name = models.CharField(max_length=10,unique=True,null=False,blank=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="session_created_by")
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="session_updated_by")
    
        
    def clean(self):
        if self.start_date < self.end_date:
            raise ValidationError(message="Start date must be before end date")
        return super().clean()
        

    def __str__(self):
        return f"Session {self.name}"


class TypeTimbre(models.Model):
    name = models.CharField(unique=True,null=False,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="type_created_by")
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="type_updated_by")


    def __str__(self):
        return f"Timbre type: {self.name}"


class PriceAssignation(models.Model):
    session = models.ForeignKey(Session,on_delete=models.CASCADE,related_name="session")
    type = models.ForeignKey(TypeTimbre,on_delete=models.CASCADE,related_name="type_timbre")
    price = models.FloatField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="price_assigned_by")
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="price_assigment_updated_by")
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=["session","type"],name="unique_type_session",violation_error_message="Unique price by session")
        ]
    
    def __str__(self):
        return f"Price of type {self.type.name} for session {self.session.name} : {self.price}"


class Timbre(models.Model):
    reference = models.CharField(unique=True,null=False,blank=False)
    type = models.ForeignKey(TypeTimbre,on_delete=models.CASCADE,related_name="type")
    used = models.BooleanField(default=False)
    qrCode = models.CharField(max_length=30)
    secret =  models.FloatField(null=False)
    price = models.ForeignKey(PriceAssignation,on_delete=models.CASCADE,related_name="assigned_price")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    owned_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="timbre_owned_by")
    
    class Meta:
        permissions = [
            # --- USER ---
            ("buy_stamp", "Can buy stamp"),
            ("view_own_stamps", "Can view own stamps"),
            ("download_pdf", "Can download PDF"),
            ("generate_qr", "Can generate QR"),     

            # --- CONTROLLER ---
            ("scan_qr", "Can scan QR"),
            ("verify_stamp", "Can verify stamp"),
            ("view_scan_history", "Can view scan history"),
            ("create_stamp", "Can create stamp"),
            ("sell_stamp", "Can sell stamp"),
            ("view_sales", "Can view sales"),

            # --- ADMIN ---
            ("manage_users", "Can manage users"),
            ("view_all_stamps", "Can view all stamps"),
        ]

    def __str__(self):
        return f"Timbre {self.reference}"
    
class Transaction(models.Model):
    timbre = models.ForeignKey(Timbre,on_delete=models.CASCADE)
    status = models.CharField(choices=[("pending","pending"),("rejected","rejected"),("accepted","accepted")],default="pending",null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    controller = models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_initiated_by")
    updated_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="transaction_updated_by")
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'

    def __str__(self):
        return f"Utilisation du timbre {self.timbre} par {self.controller}"
    
class Notification(models.Model):
    content = models.CharField(max_length=100,null=False)
    read = models.BooleanField(default=False,null=False)
    link = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    
    def __str__(self):
        return f"Notification for user {self.user} at {self.created_at}"
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
    
    # class Meta:
    #     constraints =[
    #         CheckConstraint(condition=Q(start_date<end_date))
    #     ]
        
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    owned_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="timbre_owned_by")



    def __str__(self):
        return f"Timbre {self.reference}"
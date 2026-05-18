from django.db import models

# Create your models here.
class Achat(models.Model):
    reference = models.CharField(max_length=200,null=False)
    status = models.CharField(choices=[("pending","pending"),("rejected","rejected"),("accepted","accepted")],default="pending",null=False)
    phone   = models.CharField(max_length=12, blank=True, null=True)
    amount = models.FloatField()
    
    def __str__(self):
        return f"achat du timbre {self.reference}"
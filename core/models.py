from django.db import models

from timbre.models import TypeTimbre

# Create your models here.
class Achat(models.Model):
    reference = models.CharField(max_length=200,null=False)
    status = models.CharField(choices=[("pending","pending"),("SUCCESS","SUCCESS"),("FAILED","FAILED")],default="pending",null=False)
    phone   = models.CharField(max_length=12, blank=True, null=True)
    amount = models.FloatField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="achats")
    type = models.ForeignKey(TypeTimbre, on_delete=models.CASCADE, related_name="achats")
    
    def __str__(self):
        return f"achat no:{self.reference}"
# Create your views here.
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.models import Achat

@method_decorator(csrf_exempt, name="dispatch")
class DjomyWebhookView(View):

    def post(self, request):

        try:

            data = json.loads(request.body)

            reference = data.get("reference")
            status = data.get("status")

            transaction = Achat.objects.get(
                reference=reference
            )

            if status == "SUCCESS":

                transaction.status = "SUCCESS"

                # generateTimbre()

            else:

                transaction.status = "FAILED"

            transaction.save()

            return JsonResponse({
                "ok": True
            })

        except Achat.DoesNotExist:

            return JsonResponse({
                "ok": False,
                "error": "Transaction not found"
            }, status=404)

        except Exception as e:

            return JsonResponse({
                "ok": False,
                "error": str(e)
            }, status=400)
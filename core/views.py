import hashlib
import hmac
import json
import logging
from random import randint
import uuid

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from core.pdf_service import TimbrePDFGenerator
from timbre.models import Notification, PriceAssignation, Timbre, TypeTimbre
from timbre_numerique.settings import DJOMY_CLIENT_SECRET

logger = logging.getLogger(__name__)


def verify_signature(request) -> bool:
    received_sig = request.headers.get("X-Djomy-Signature", "")
    if not received_sig:
        logger.warning("[Djomy Webhook] Signature absente — accepté en sandbox")
        return True

    expected_sig = hmac.new(
        DJOMY_CLIENT_SECRET.encode("utf-8"),
        request.body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(received_sig, expected_sig)


@csrf_exempt
@require_POST
def djomy_webhook(request):
    if not verify_signature(request):
        logger.warning("[Djomy Webhook] Signature invalide — requête rejetée")
        return HttpResponse(status=403)

    try:
        payload = json.loads(request.body)
        # print("==============================================================================================================================\n",payload)   
    except json.JSONDecodeError:
        logger.error("[Djomy Webhook] Body JSON invalide: %s", request.body)
        return HttpResponse(status=400)
    logger.info("[Djomy Webhook] Payload: %s", payload)
    # ── Extraire les champs du vrai payload Djomy ──
    event_type = payload.get("eventType", "")        # "payment.redirected", "payment.success", etc.
    data       = payload.get("data", {})
    metadata   = payload.get("metadata", {})
    status      = data.get("status", "").upper()     # REDIRECTED, SUCCESS, FAILED, PENDING
    tx_id       = data.get("transactionId", "")                 # ID de la transaction chez Djomy
    reference   = (
        data.get("merchantPaymentReference")         # champ principal
        or metadata.get("order_id")                  # fallback dans metadata
        or ""
    )
    amount      = data.get("paidAmount")
    currency    = data.get("currency", "GNF")

    logger.info(
        "[Djomy Webhook] eventType=%s | status=%s | ref=%s | txId=%s | amount=%s %s",
        event_type, status, reference, tx_id, amount, currency,
    )
# bae77b83-0a1e-4c7e-8f7a-5fecc62e7381
    # ── Router selon le statut ──
    # print("===================================================================================",status)
    # if status == "SUCCESS":
    if status:
        _handle_success(reference, tx_id, amount)

    elif status == "FAILED":
        message = payload.get("message", "")
        _handle_failure(reference, tx_id, message)

    elif status in ("REDIRECTED", "PENDING"):
        # L'utilisateur a été redirigé vers Djomy mais n'a pas encore payé
        logger.info("[Djomy Webhook] Paiement en attente (status=%s) ref=%s", status, reference)
        _handle_pending(tx_id)

    else:
        logger.warning("[Djomy Webhook] Statut non géré: %s | event: %s", status, event_type)

    return JsonResponse({"ok": True}, status=200)


# ──────────────────────────────────────────────
# Handlers
# ──────────────────────────────────────────────

def _handle_success(reference: str, transaction_id: str, amount):
    from core.models import Achat

    logger.info("[Djomy] SUCCESS — ref=%s txId=%s", reference, transaction_id)
    try:
        achat = Achat.objects.get(reference=reference)
        achat.status = "SUCCESS"
        achat.save(update_fields=["status"])
        logger.info("[Djomy] Achat %s marqué SUCCESS", achat.id)
        type = TypeTimbre.objects.get(pk=achat.type_id)
        assign = PriceAssignation.objects.get(type=type,session__active=True)
        user = achat.user
        nb= Timbre.objects.all().count()+1          
        #generate 15 digit unique reference 
        ref = str(uuid.uuid4().int)[:15-len(str(nb))]
        reference_timb = f"{ref}{nb}"
        secret = randint(500,nb*500)
        qrcode= f"{reference_timb}|{user}|{secret}"
        try:
            timbre = Timbre.objects.create(reference=reference_timb,type=type,qrCode=qrcode,secret=secret,owned_by=user,price=assign)
        except Exception as e:
            if "UNIQUE constraint failed: core_timbre.reference" in str(e):
                reference_timb = f"{ref}{nb+1}"
                qrcode= f"{reference_timb}|{user}|{secret}"
                timbre = Timbre.objects.create(reference=reference_timb,type=type,qrCode=qrcode,secret=secret,owned_by=user,price=assign)
            else:
                logger.exception("[Djomy] Erreur lors de la création du timbre: %s", e)
                raise e
        pdf_url = TimbrePDFGenerator.generate(timbre)
        # print("==============================================================================================================================")
        Notification.objects.create(
            title="Achat réussi",
            content=f"Votre achat a été confirmé. Merci !",
            user=achat.user,
        )
        # TODO: générer le timbre ici
    except Achat.DoesNotExist:
        logger.error("[Djomy] Achat introuvable pour référence: %s", transaction_id)
    except Exception as e:
        logger.exception("[Djomy] Erreur _handle_success: %s", e)


def _handle_failure(reference: str, transaction_id: str, message: str):
    from core.models import Achat

    logger.warning("[Djomy] FAILED — ref=%s msg=%s", reference, message)
    try:
        achat = Achat.objects.get(reference=transaction_id)
        achat.status = "FAILED"
        achat.save(update_fields=["status"])
        logger.info("[Djomy] Achat %s marqué FAILED", achat.id)
    except Achat.DoesNotExist:
        logger.error("[Djomy] Achat introuvable pour référence: %s", reference)
    except Exception as e:
        logger.exception("[Djomy] Erreur _handle_failure: %s", e)


def _handle_pending(transaction_id: str):
    from core.models import Achat

    try:
        achat = Achat.objects.get(reference=transaction_id)
        if achat.status not in ("SUCCESS", "FAILED"):
            achat.status = "PENDING"
            achat.save(update_fields=["status"])
            logger.info("[Djomy] Achat %s marqué PENDING", achat.id)
    except Achat.DoesNotExist:
        logger.error("[Djomy] Achat introuvable pour référence: %s", transaction_id)
    except Exception as e:
        logger.exception("[Djomy] Erreur _handle_pending: %s", e)


from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required

@csrf_exempt
@require_GET
def download_timbre(request, pk):

    timbre = Timbre.objects.get(pk=pk)

    # Vérification des droits
    if timbre.proprietaire != request.user:
        raise Http404()

    return FileResponse(
        timbre.pdf.open("rb"),
        as_attachment=True,
        filename="timbre.pdf"
    )
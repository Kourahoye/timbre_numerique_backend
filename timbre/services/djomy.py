import hashlib
import hmac
import uuid

import requests

from timbre_numerique.settings import (
    DJOMY_BASE_URL,
    DJOMY_CLIENT_ID,
    DJOMY_CLIENT_SECRET,
)

BASE_URL = DJOMY_BASE_URL
CLIENT_ID = DJOMY_CLIENT_ID
CLIENT_SECRET = DJOMY_CLIENT_SECRET


def generate_signature() -> str:

    signature = hmac.new(
        CLIENT_SECRET.encode("utf-8"),
        CLIENT_ID.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    # return signature
    return f"{CLIENT_ID}:{signature}"


def get_token() -> str:
    """
    Authentification auprès de l'API Djomy.
    Retourne le Bearer token.
    """
    url = f"{BASE_URL}/v1/auth"
    
    headers = {
        "X-API-KEY": generate_signature(),
        "Content-Type": "application/json",
    }
    # print("=======================================================")
    # print(headers)
    # print("=======================================================")
    response = requests.post(url, headers=headers, timeout=10,data={})
    
    if not response.ok:
        raise Exception(
            f"[Djomy] Authentification échouée — "
            f"HTTP {response.status_code}: {response.text}"
        )
    
    data = response.json()
    
    # La réponse peut être directement le token ou dans data.data
    if "data" in data and data["data"] and "accessToken" in data["data"]:
        return data["data"]["accessToken"]
    elif "token" in data:
        return data["token"]
    else:
        raise Exception(
            f"[Djomy] Réponse inattendue — token absent: {data}"
        )


def create_payment(phone: str, amount: int) -> dict:

    token = get_token()
    
    # Générer une référence unique pour le marchand
    merchant_reference = str(uuid.uuid4())
    
    url = f"{BASE_URL}/v1/payments/gateway"
    
    payload = {
        "amount": amount,
        "countryCode": "GN",  # Code pays Guinée
        "payerNumber": phone,  # Doit être au format international ex: 002246XXXXXXXX
        "description": "Paiement timbre",
        "merchantPaymentReference": merchant_reference,
        "returnUrl": "https://swimmer-bullwhip-rearview.ngrok-free.dev/webhook/",
        "cancelUrl": "https://votre-domaine.com/payment/cancel",
        "metadata": {
            "order_id": merchant_reference,
            "product": "timbre_numerique"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-KEY": generate_signature(),
        "Content-Type": "application/json",
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if not response.ok:
        raise Exception(
            f"[Djomy] Création paiement échouée — "
            f"HTTP {response.status_code}: {response.text}"
        )
    
    result = response.json()
    # print(result)
    # Vérifier la structure de la réponse
    if result.get("success") and result.get("data"):
        return result["data"]
    elif result.get("data"):
        return result["data"]
    else:
        return result


def create_payment_without_redirect(phone: str, amount: int, payment_method: str = "OM") -> dict:

    token = get_token()
    
    merchant_reference = str(uuid.uuid4())
    
    url = f"{BASE_URL}/v1/payments"
    
    payload = {
        "paymentMethod": payment_method,  # "OM" ou "MOMO"
        "payerIdentifier": phone,  # Format international
        "amount": amount,
        "countryCode": "GN",
        "description": "Paiement timbre",
        "merchantPaymentReference": merchant_reference,
        "metadata": {
            "order_id": merchant_reference,
            "product": "timbre_numerique"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-KEY": generate_signature(),
        "Content-Type": "application/json",
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    if not response.ok:
        raise Exception(
            f"[Djomy] Création paiement échouée — "
            f"HTTP {response.status_code}: {response.text}"
        )
    
    result = response.json()
    
    if result.get("success") and result.get("data"):
        return result["data"]
    
    return result


def get_payment_status(transaction_id: str) -> dict:
    """
    Récupère le statut d'un paiement.
    
    Args:
        transaction_id: L'ID de transaction retourné par create_payment
    
    Returns:
        dict contenant le statut et les détails du paiement
    """
    token = get_token()
    
    url = f"{BASE_URL}/v1/payments/{transaction_id}/status"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "X-API-KEY": generate_signature(),
        "Content-Type": "application/json",
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if not response.ok:
        raise Exception(
            f"[Djomy] Récupération statut échouée — "
            f"HTTP {response.status_code}: {response.text}"
        )
    
    result = response.json()
    
    if result.get("success") and result.get("data"):
        return result["data"]
    
    return result
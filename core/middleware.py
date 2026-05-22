import jwt
from django.conf import settings
from django.contrib.auth.models import User

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGO])
                request.user = User.objects.get(id=payload["user_id"])
            except Exception:
                request.user = None
        return self.get_response(request)

# timbre_numerique/middleware.py  ← nouveau fichier

class SkipJwtForWebhook:
    """
    Bypasse le middleware JWT de gqlauth pour les routes webhook.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.path.startswith("/djomy/webhook/"):
            # Marquer la requête comme déjà authentifiée pour court-circuiter gqlauth
            request.skip_jwt = True
        return None
    

# middleware.py
from strawberry.extensions import SchemaExtension
from django.utils import translation
import re

class LanguageExtension(SchemaExtension):
    def on_executing_start(self):
        request = self.execution_context.context.get("request")
        if not request:
            return

        raw = request.headers.get("Accept-Language", "fr")
        # "fr-FR,fr;q=0.9,en;q=0.8" → "fr"
        lang = re.split(r'[-_,;]', raw.strip())[0].lower()

        supported = ["fr", "en"]
        if lang not in supported:
            lang = "fr"

        translation.activate(lang)

    def on_executing_end(self):
        translation.deactivate()
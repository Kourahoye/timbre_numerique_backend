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

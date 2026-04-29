from strawberry.permission import BasePermission

class IsAuthenticated(BasePermission):
    message = "Authentication required"

    def has_permission(self, source, info, **kwargs):
        request = info.context.request
        headers = request.headers  # dictionnaire avec tous les headers
        # print(headers.get("Authorization"))  # affichera ton Bearer token
        user = request.user
        # print(user)
        return user.is_authenticated    

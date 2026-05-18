from django.contrib import admin
from django.urls import path

from core.schema import schema
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView

from core.views import DjomyWebhookView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema))),
     path("djomy/webhook/",DjomyWebhookView.as_view(),name="djomy_webhook"),
]

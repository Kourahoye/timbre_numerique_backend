from django.contrib import admin
from django.urls import include, path

from core.schema import schema
from django.views.decorators.csrf import csrf_exempt
from strawberry.django.views import GraphQLView
from django.conf.urls.i18n import i18n_patterns

from core.views import  djomy_webhook

urlpatterns = [
     path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema))),
    path("webhook/", csrf_exempt(djomy_webhook), name="djomy_webhook"),
]

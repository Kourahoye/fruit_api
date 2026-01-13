from django.contrib import admin
from django.urls import path

from django.views.decorators.csrf import csrf_exempt

from strawberry.django.views import GraphQLView

from core.schema import schema
from learngraphene import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema,graphiql=True,multipart_uploads_enabled=True))),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.conf import settings

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
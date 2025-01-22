from django.urls import path, include
from rest_framework import routers

from todo.views import TodoViewSet

router = routers.DefaultRouter()
router.register("", TodoViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "todo"

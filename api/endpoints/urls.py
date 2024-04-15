from rest_framework import routers

from .views import SearchView

router = routers.DefaultRouter()

router.register(r"search", SearchView, basename="search")

urlpatterns = router.urls

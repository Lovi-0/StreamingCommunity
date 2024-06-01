from rest_framework import routers

from .views import SearchView#, DownloadView

router = routers.DefaultRouter()

router.register(r"search", SearchView, basename="search")
#router.register(r"download", DownloadView, basename="download")

urlpatterns = router.urls

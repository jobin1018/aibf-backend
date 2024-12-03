from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import GoogleSignInView, EventViewSet, RegistrationViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'registrations', RegistrationViewSet)

# url patterns for users app
urlpatterns = [
    path('', include(router.urls)),
    path('api/google-signin/', GoogleSignInView.as_view(), name='google-signin'),
]


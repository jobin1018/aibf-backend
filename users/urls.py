from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import GoogleSignInView, EventViewSet, RegistrationViewSet, UserViewSet, CompleteProfileView

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'registrations', RegistrationViewSet)
router.register(r'users', UserViewSet)

# url patterns for users app
urlpatterns = [
    path('', include(router.urls)),
    path('api/google-signin/', GoogleSignInView.as_view(), name='google-signin'),
    path('api/complete-profile/', CompleteProfileView.as_view(), name='complete-profile'),
]

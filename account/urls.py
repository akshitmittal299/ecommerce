from django.urls import path, include
from .views import *
from rest_framework_nested.routers import DefaultRouter,NestedDefaultRouter

router =DefaultRouter()
router.register(r'user', UserViewset)


nested_router = NestedDefaultRouter(router , r'user', lookup= 'user')
nested_router.register(r'profile', UserProfileViewset)
nested_router.register(r'address', UserAddressViewset)

urlpatterns= [
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
    path("login/", UserLoginView.as_view()),
    path("verify-email/", VerifyEmailView.as_view())
]
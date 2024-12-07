from django.urls import path, include
from .views import *
from rest_framework_nested.routers import DefaultRouter,NestedDefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

router =DefaultRouter()
router.register(r'user', RegisterUserViewSet)


nested_router = NestedDefaultRouter(router , r'user', lookup= 'user')
nested_router.register(r'profile', UserProfileViewset)
nested_router.register(r'address', UserAddressViewset)
nested_router.register(r'stripe', StripeCustomerViewset)


urlpatterns= [
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("", include(router.urls)),
    path("", include(nested_router.urls)),
    path("verify-email/", VerifyEmailView.as_view()),
]


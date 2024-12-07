from rest_framework import viewsets, status, generics, permissions
from rest_framework.views import APIView
from .serializer import *
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
import stripe
from django.conf import settings
from django.db import transaction

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Create the user first
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create a Stripe customer after the user is created
        try:
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
            )

            # Create a StripeCustomer record in the database
            StripeCustomer.objects.create(
                user=user,
                stripe_customer_id=stripe_customer.id,
            )
            
            # Respond with the user and their Stripe customer ID
            return Response({
                'user': UserSerializer(user).data,
                'stripe_customer_id': stripe_customer.id,
            })
        except stripe.error.StripeError as e:
            # Handle Stripe error if something goes wrong
            return Response({"error": str(e)}, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Call the original post method to get the tokens
        response = super().post(request, *args, **kwargs)
        
        # Add a custom message and status
        response_data = {
            "status": "success",
            "message": "Login successful",  # You can customize this message
            "data": response.data  # This contains the 'access' and 'refresh' tokens
        }
        
        return Response(response_data, status=status.HTTP_200_OK)    


class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get("token")
        try:
            user = User.objects.get(verification_code = token)
            if user.is_expired():
                return Response({"success":False, "response_data":"token is expired"}, status=400)
            elif user:
                user.is_verified = True
                user.is_active = True
                user.verification_code = ""
                user.token_created = None
                user.save()
                return Response({"success":True, "response_data":"email successfully verified"}, status = status.HTTP_200_OK)
        except:
            return Response({"success":False, "response_data":"Invalid Verification token"}, status = status.HTTP_404_NOT_FOUND)
        
class UserProfileViewset(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()


class UserAddressViewset(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()


class StripeCustomerViewset(viewsets.ModelViewSet):
    serializer_class = StripeCustomerSerializer
    queryset = StripeCustomer.objects.all()

from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from rest_framework.permissions import *
from .serializer import *
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *
from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
import stripe
from django.conf import settings
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from .utils import send_forgot_password_email  
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            stripe_customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
            )

            StripeCustomer.objects.create(
                user=user,
                stripe_customer_id=stripe_customer.id,
            )
            
            return Response({
                "success":True,
                "message":"user registered successfully",
                'user': UserSerializer(user).data,
                'stripe_customer_id': stripe_customer.id,
            })
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        response_data = {
            "status": "success",
            "message": "Login successful",  
            "data": response.data  
        }
        
        return Response(response_data, status=status.HTTP_200_OK)    


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
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
    permission_classes = [permissions.AllowAny]

class UserAddressViewset(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()
    permission_classes =[permissions.AllowAny]

class StripeCustomerViewset(viewsets.ModelViewSet):
    serializer_class = StripeCustomerSerializer
    queryset = StripeCustomer.objects.all()


class GetUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user 
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}reset-password/{token}/" 
        
        try:
            send_forgot_password_email(user, token)
        except Exception as e:
            return Response({"success": False, "message": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"success": True, "message": "Password reset email has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [permissions.AllowAny]

    def get_user_from_token(self, token):
        for user in User.objects.all():
            if default_token_generator.check_token(user, token):
                return user
        return None

    def post(self, request, token):
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"detail": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_user_from_token(token)

        if not user:
            raise ValidationError("The password reset token is invalid or has expired.")

        user.set_password(new_password)
        user.save()

        return Response({"success": True, "message": "Password has been successfully reset."}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            if not user.check_password(old_password):
                raise serializers.ValidationError("Old password is incorrect.")
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            return Response({"success": True, "message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response({"success":False, "error":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

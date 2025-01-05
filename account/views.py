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
from django.contrib.auth.hashers import make_password  # To hash the new password
from rest_framework.exceptions import ValidationError
from rest_framework import permissions
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

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
                "success":True,
                "message":"user registered successfully",
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


class UserAddressViewset(viewsets.ModelViewSet):
    serializer_class = UserAddressSerializer
    queryset = UserAddress.objects.all()


class StripeCustomerViewset(viewsets.ModelViewSet):
    serializer_class = StripeCustomerSerializer
    queryset = StripeCustomer.objects.all()


class GetUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user  # Get the authenticated user
        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class ForgotPasswordView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        email = request.data.get("email")

        # Validate if email is provided
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the user based on the provided email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Return a response if user doesn't exist
            return Response({"success":False,"message": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate the password reset token
        token = default_token_generator.make_token(user)
        print(token)
        # reset_link = settings.FRONTEND_URL + "reset-password/"+token+"/"  # Construct the reset link
        # print(reset_link, "herer")
        try:
            # Call the utility function to send the reset email
            send_forgot_password_email(user, token)
        except Exception as e:
            # If the email sending fails, return an error response
            return Response({"success":False,"message": f"Error sending email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return success response if email was sent successfully
        return Response({"success":True,"message": "Password reset email has been sent."}, status=status.HTTP_200_OK)





class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    def get_user_from_token(self, token):
        """
        Helper function to retrieve the user from the reset token.
        """
        try:
            user = User.objects.get(email=default_token_generator.check_token(user, token))
            return user
        except:
            return None
    def post(self, request, token):
        # Retrieve the new password from the request
        new_password = request.data.get("new_password")

        # Validate if new password is provided
        if not new_password:
            return Response({"detail": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)
        print(token)
        # Get the user based on the token (no need to iterate over all users)
        user = self.get_user_from_token(token)
        print(user)
        if not user:
            raise ValidationError("The password reset token is invalid or has expired.")

        # Set the new password
        user.password = make_password(new_password)
        user.save()



        # Return success response
        return Response({"detail": "Your password has been successfully reset."}, status=status.HTTP_200_OK)

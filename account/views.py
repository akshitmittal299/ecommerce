from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from .serializer import UserAddressSerializer, UserProfileSerializer, UserRegisterSerializer, UserLoginSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import *

class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True, "response_data":serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success":False, "response_data":serializer.errors}, status= 400)


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer =  self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = authenticate(email=serializer.validated_data["email"], password=serializer.validated_data["password"])
            if user: 
                if user.is_active and user.is_verified:
                    token , created = Token.objects.get_or_create(user = user)
                    return Response({"success":True, "response_data":{"token":token.key}}, status=200)
                return Response({"success":False, "response_data":"verify your email"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"success":"false", "response_data":"email or password is incorrect"}, status = status.HTTP_401_UNAUTHORIZED)
        return Response({"success":"false", "response_data":serializer.error_messages}, status=400)
            # token, create = Token.objects.get_or_create()
            
        
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
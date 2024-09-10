from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from .serializer import UserRegisterSerializer, UserLoginSerializer
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class UserRegisterView(generics.CreateAPIView):
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
                token , created = Token.objects.get_or_create(user = user)
                return Response({"success":True, "response_data":{"token":token.key}}, status=200)
            else:
                return Response({"success":"false", "response_data":"email or password is incorrect"}, status = status.HTTP_401_UNAUTHORIZED)
        return Response({"success":"false", "response_data":serializer.error_messages}, status=400)
            # token, create = Token.objects.get_or_create()
            
        

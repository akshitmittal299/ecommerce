from rest_framework import serializers
from .models import User
from .utils import send_welcome_email

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_no', 'password', 'password_confirm')
        extra_kwargs={"password":{"write_only":True},"password_confirm":{"write_only":True}}
    
    def validate(self, data):
        if data['password'] != data["password_confirm"]:
            raise serializers.ValidationError({"password":"Passwords do not match"})
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user= self.Meta.model.objects.create_user(**validated_data)
        user.set_password(password)
        user.password_confirm = user.password
        user.save()
        send_welcome_email(user)
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=50)
from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'},)    
    
    class Meta:
        model = User
        fields = ['email','first_name','last_name', 'password', 'role']
        extra_kwargs={
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
            role=validated_data.get('role', None),is_active=False, is_staff=False, is_superuser=False, email_verified=False
            
        )
        return user
    
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        
    )
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True}
        }

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
       
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError({"custom_error": "Invalid credentials."})
            if not user.is_active:
                raise serializers.ValidationError("User account is inactive.")
            if not user.email_verified:
                raise serializers.ValidationError("Email is not verified.")
            
        
        refresh = RefreshToken.for_user(user)
        return {
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        
class PasswordResetRequestSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    
class PasswordResetConfirmSerializer(serializers.ModelSerializer):
    token = serializers.CharField(
        write_only=True,
        style={'input_type': 'text'},
        required=True
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        min_length=8
    )
    

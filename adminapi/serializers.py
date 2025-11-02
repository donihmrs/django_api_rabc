from rest_framework import serializers
from .models import User, Product, Order, Invitation
import base64
import json
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .permissions import ROLE_PERMISSIONS

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # encode data profile
        user_profile = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role
        }

        user_profile_json = json.dumps(user_profile)
        user_profile_base64 = base64.b64encode(user_profile_json.encode('utf-8')).decode('utf-8')
        data['profile'] = user_profile_base64

        # Ambil permissions
        role_perm = ROLE_PERMISSIONS.get(user.role, {})

        # Encode ke base64
        role_perm_json = json.dumps(role_perm)  # dict → JSON string
        role_perm_base64 = base64.b64encode(role_perm_json.encode('utf-8')).decode('utf-8')

        data['permissions'] = role_perm_base64

        return data
    
class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name']
        read_only_fields = ['id']

class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'password','first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

class ProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'status', 'created_at']

class ProductForeignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']

class OrderSerializer(serializers.ModelSerializer):
    product = ProductForeignSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
        coerce_to_string=False
    )
    class Meta:
        model = Order
        fields = ['id', 'product','product_id', 'customer_name', 'quantity', 'total_price', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ['id', 'email', 'role', 'token', 'inviter', 'is_used', 'created_at', 'expires_at']
        read_only_fields = ['token', 'inviter', 'is_used', 'created_at', 'expires_at']
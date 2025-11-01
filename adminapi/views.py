from django.shortcuts import render
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Product, Order, Invitation
from .serializers import UserSerializer, AdminCreateUserSerializer, ProductSerializer, OrderSerializer, InvitationSerializer
from .permissions import UserPermission, ProductPermission, OrderPermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermission]

    def get_serializer_class(self):
        if self.request.user and self.request.user.role == 'admin' and self.action == 'create':
            return AdminCreateUserSerializer
        return UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductPermission]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [OrderPermission]

    def perform_create(self, serializer):
        # Calculate total_price automatically
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        total = product.price * quantity
        serializer.save(total_price=total)

class InvitationViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin):
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if request.user.role not in ('admin', 'manager'):
            return Response({'detail': 'Forbidden'}, status=403)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save(inviter=request.user)

        invite_link = f"{request.scheme}://{request.get_host()}/api/invitations/accept/?token={invitation.token}"
        subject = 'You are invited'
        message = f"You have been invited. Click to accept: {invite_link}\nThis link expires: {invitation.expires_at}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [invitation.email])

        print(f"Invitation sent to {invitation.email} with link: {invite_link}")

        return Response(self.get_serializer(invitation).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='accept', permission_classes=[AllowAny])
    def accept(self, request):
        token = request.data.get('token') or request.query_params.get('token')
        if not token:
            return Response({'detail': 'token required'}, status=400)
        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            return Response({'detail': 'Invalid or expired token'}, status=400)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not invitation.is_valid():
            return Response({'detail': 'invitation invalid or expired'}, status=400)

        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not username or not password:
            return Response({'detail': 'username and password required'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'detail': 'username exists'}, status=400)

        User.objects.create_user(username=username, email=invitation.email, first_name=first_name, last_name=last_name, 
                                 password=password, role=invitation.role)

        invitation.is_used = True
        invitation.save()

        return Response({'detail': 'account created'}, status=201)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def revoke(self, request, pk=None):
        """Revoke (cancel) an existing invitation by ID."""
        invitation = self.get_object()

        # hanya admin boleh revoke invitation

        if request.user.role != 'admin':
            return Response({'detail': 'Forbidden'}, status=403)

        # kalau sudah dipakai / expired, tidak bisa di revoke lagi
        if getattr(invitation, 'is_used', False) or invitation.is_used:
            return Response({'detail': 'Invitation already used or revoked'}, status=400)

        # ubah status
        invitation.is_used = True
        invitation.save()

        return Response({'detail': 'Invitation revoked successfully'}, status=200)
    
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token required"}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

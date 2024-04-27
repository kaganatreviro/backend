import datetime
import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import (
    RetrieveAPIView, UpdateAPIView, DestroyAPIView, CreateAPIView, ListAPIView,
    GenericAPIView
)
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from happyhours.permissions import (
    IsUserOwner, IsPartnerAndAdmin, IsNotAuthenticated
)

from .serializers import (
    UserSerializer, TokenObtainSerializer, ClientRegisterSerializer,
    PartnerCreateSerializer, ClientPasswordForgotPageSerializer,
    ClientPasswordResetSerializer, ClientPasswordChangeSerializer
)
from .utils import generate_reset_code, datetime_serializer, \
    datetime_deserializer

User = get_user_model()


class TokenObtainView(TokenObtainPairView):
    """
    Token Obtaining view
    """
    serializer_class = TokenObtainSerializer


class ClientRegisterView(CreateAPIView):
    """
    Individual Client Register View
    """
    queryset = User.objects.all()
    permission_classes = [IsNotAuthenticated]
    serializer_class = ClientRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        data = serializer.data
        data["tokens"] = {"refresh": str(token),
                          "access": str(token.access_token)}
        headers = self.get_success_headers(serializer.data)
        return Response(
            data, status=status.HTTP_201_CREATED, headers=headers
        )


class ClientPasswordChangeView(GenericAPIView):
    serializer_class = ClientPasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        user.set_password(serializer.validated_data['password'])
        user.save()
        print('work?')
        return Response(
            'Password successfully changed', status=status.HTTP_200_OK
        )


class UserViewSet(ViewSetMixin,
                  RetrieveAPIView,
                  UpdateAPIView,
                  DestroyAPIView):
    """
    User viewset with Owner permission
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsUserOwner]


class CreatePartner(CreateAPIView):
    """
    Individual Partner Register View
    """
    queryset = User.objects.all()
    serializer_class = PartnerCreateSerializer
    permission_classes = [IsAdminUser]


class ClientListView(ListAPIView):
    """
    List of clients for partner (or admin?)
    """
    queryset = User.objects.all().filter(role='client').order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsPartnerAndAdmin]


class ClientPasswordForgotPageView(GenericAPIView):
    serializer_class = ClientPasswordForgotPageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = generate_reset_code()
        request.session['reset_code'] = str(reset_code)
        time_now = datetime.datetime.now()
        request.session['reset_code_create_time'] = (
            datetime_serializer(time_now))
        return Response('Success', status=status.HTTP_200_OK)


class ClientPasswordResetView(GenericAPIView):
    serializer_class = ClientPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_code = serializer.validated_data['reset_code']

        if ('reset_code' in request.session
                and 'reset_code_create_time' in request.session):
            stored_code = request.session['reset_code']
            stored_code_date = datetime_deserializer(
                request.session['reset_code_create_time']
            )
            passed_time = datetime.datetime.now()

            if (stored_code == reset_code and
                    (passed_time - stored_code_date).total_seconds() < 600):
                user = User.objects.get(
                    email=serializer.validated_data['email']
                )
                token = RefreshToken.for_user(user)
                del request.session['reset_code']
                del request.session['reset_code_create_time']
                print(request.session['reset_code'])
                return Response(
                    {'refresh': str(token), 'access': str(token.access_token)}
                )
        return Response('Invalid code', status=status.HTTP_400_BAD_REQUEST)

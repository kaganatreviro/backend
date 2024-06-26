import datetime

from django.contrib.auth import get_user_model

from drf_spectacular.utils import extend_schema
from rest_framework import status, filters
from rest_framework.generics import (
    RetrieveAPIView,
    UpdateAPIView,
    DestroyAPIView,
    CreateAPIView,
    ListAPIView,
    GenericAPIView,
    get_object_or_404,
)
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken
)
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenViewBase

from happyhours.permissions import (
    IsUserOwner,
    IsPartnerUser,
    IsNotAuthenticated,
    IsAdmin,
    IsAuthenticatedAndNotAdmin,
)

from .serializers import (
    UserSerializer,
    TokenObtainSerializer,
    ClientRegisterSerializer,
    PartnerCreateSerializer,
    ClientPasswordForgotPageSerializer,
    ClientPasswordResetSerializer,
    ClientPasswordChangeSerializer,
    AdminLoginSerializer,
    ClientListSerializer,
    PartnerListSerializer,
    BlockUserSerializer,
    PartnerProfileSerializer,
    ClientSerializer,
    PartnerProfileAdminSerializer,
    TokenRefreshBlockCheckSerializer,
    PartnerLoginSerializer,
)
from .utils import (
    generate_reset_code,
    datetime_serializer,
    datetime_deserializer,
    send_reset_code_email,
)

User = get_user_model()


@extend_schema(tags=["Users"])
class TokenObtainView(TokenObtainPairView):
    """
    User authorization. View responsible for creating valid refresh and access
    tokens. Users of all roles can access this view. But admin have separated
    view. Return not only tokens but a user's information
    (id, email, name, role, max_establishments)

    ### Access Control:
    - All authenticated users can access this view.

    ### Implementation Details:
    - Serializer check if user exists in queryset. If not will throw an
    exception. Additionally, checks if user does not have flag is_blocked. If
    it is blocked, the user won't receive tokens
    """

    serializer_class = TokenObtainSerializer


@extend_schema(tags=["Users"])
class AdminLoginView(TokenObtainView):
    """
    Separated admin authorization. View responsible for creating valid refresh
    and access tokens for admin role or superuser.
    Return not only tokens but a user's information
    (id, email, name, role)

    ### Access Control:
    - Only users with admin role or superuser

    ### Implementation Details:
    - Serializer check if user exists in queryset. If not will throw an
    exception, checks if user has admin role or superuser
    """

    serializer_class = AdminLoginSerializer


@extend_schema(tags=["Users"])
class PartnerLoginView(TokenObtainView):
    """
    Separated partner authorization. View responsible for creating valid refresh
    and access tokens for partner role.
    Return not only tokens but a user's information
    (id, email, name, role, max_establishments)

    ### Access Control:
    - Only users with partner role

    ### Implementation Details:
    - Serializer check if user exists in queryset. If not will throw an
    exception, checks if user has admin role or superuser
    """
    serializer_class = PartnerLoginSerializer


@extend_schema(tags=["Users"])
class TokenRefreshBlockCheckView(TokenViewBase):
    """
    Check if user is blocked
    """

    serializer_class = TokenRefreshBlockCheckSerializer


@extend_schema(tags=["Users"])
class ClientRegisterView(CreateAPIView):
    """
    Client user creation. View responsible for creating user object with role
    client. Unauthenticated users can access this view.
    Returns tokens and the user's information

    ### Fields:
    - `email`: Email address of the client user
    - `password`: Password of the client user
    - `password_confirm` : Password confirmation
    - `name`: Name of the client user
    - `date_of_birth`: Birth date of client user
    - `avatar`: Profile image of client user [Optional]

    ### Access Control:
    - Only unauthenticated users can access this view

    ### Implementation Details:
    - Obtains tokens in create function

    """

    queryset = User.objects.all()
    permission_classes = [IsNotAuthenticated]
    serializer_class = ClientRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = RefreshToken.for_user(user)
        token["email"] = user.email
        data = serializer.data
        data["tokens"] = {"refresh": str(token), "access": str(token.access_token)}
        headers = self.get_success_headers(serializer.data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(tags=["Users"])
class ClientPasswordChangeView(GenericAPIView):
    """
    User password change creation. View responsible for changing password of
    users (client, partner). Admin and superuser can not access this view.

    ### Fields:
    - `password`: Password of the user
    - `password_confirm` : Password confirmation

    ### Access Control:
    - Only unauthenticated users (client or partner) can access this view

    ### Implementation Details:
    - Sets new password

    """

    serializer_class = ClientPasswordChangeSerializer
    permission_classes = [IsAuthenticatedAndNotAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=self.request.user.email)
        user.set_password(serializer.validated_data["password"])
        user.save()
        return Response("Password successfully changed", status=status.HTTP_200_OK)


@extend_schema(tags=["Users"])
class UserViewSet(ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    User's profile CRUD. For client (mobile)

    ### Fields:
    - `name`: Name of the Client/Partner
    - `date_of_birth`: Birth of the Client
    - `avatar`: Image of Client profile
    - `phone_number`: Phone number of Partner

    ### Access Control:
    - Only user himself can access this endpoint

    ### Implementation Details:
    - Takes user object from request

    """

    queryset = User.objects.all()
    permission_classes = [IsUserOwner]

    def get_object(self):
        obj = get_object_or_404(self.queryset, id=self.request.user.id)
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        if not self.request.user.is_anonymous:
            if self.request.user.role == "partner":
                return PartnerProfileSerializer
        return UserSerializer


@extend_schema(tags=["Users"])
class ClientViewSetAdmin(ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    View that checks if a client exists in the database. For partner

    ### Fields:
    - `email`: Email if client user

    ### Access Control:
    - Partner, Admin, Superuser

    ### Implementation Details:
    - Check if email from post-request exists in the database

    """

    queryset = User.objects.filter(role="client")

    def get_serializer_class(self):
        user = self.request.user
        if not user.is_anonymous:
            if user.role == "admin" or user.is_superuser:
                return ClientSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            permissions = [IsPartnerUser]
        else:
            permissions = [IsAdmin]
        return [permission() for permission in permissions]


@extend_schema(tags=["Users"])
class PartnerViewSetAdmin(ViewSetMixin, RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    Partner's profile CRUD for admin

    ### Fields:
    - `name`: Name of the User
    - `email`: Email of the User
    - `role`: Role of the User
    - `phone_number`: Phone number of the User
    - `max_establishments`: Max establishments of the User
    - `is_blocked`: Blocked status of the User

    ### Access Control:
    - Admin, Superuser

    """

    queryset = User.objects.filter(role="partner")
    permission_classes = [IsAdmin]
    serializer_class = PartnerProfileAdminSerializer


@extend_schema(tags=["Users"])
class ClientRetrieveView(RetrieveAPIView):
    """
    Client's profile

    ### Fields:
    - `name`: Name of the Client
    - `email`: Email of the Client
    - `role`: Role of the Client
    - `phone_number`: Phone number of the Client
    - `avatar`: Avatar of the Client
    - `is_blocked`: Blocked status of the Client

    ### Access Control:
    - Partner, Admin, Superuser

    """

    queryset = User.objects.filter(role="client")
    permission_classes = [IsPartnerUser]
    serializer_class = ClientSerializer


@extend_schema(tags=["Users"])
class CreatePartner(CreateAPIView):
    """
    Partner user creation. View responsible for creating user object with role
    client. Only admin or superuser can access this view.
    Returns tokens and the user's information

    ### Fields:
    - `email`: Email address of the client user
    - `password`: Password of the client user
    - `password_confirm` : Password confirmation
    - `name`: Name of the client user
    - `max_establishments`: Name of the client user

    ### Access Control:
    - Only admin and superuser

    ### Implementation Details:
    - Does not obtain token

    """

    queryset = User.objects.all()
    serializer_class = PartnerCreateSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=["Users"])
class ClientListView(ListAPIView):
    """
    List of clients. View responsible for listing of client users.

    ### Params:
    - `limit`: Quantity of items
    - `offset`: Start index of the items
    - `search` : Text-based search

    ### Access Control:
    - Partner, Admin, Superuser

    """

    queryset = User.objects.all().filter(role="client").order_by("id")
    serializer_class = ClientListSerializer
    permission_classes = [IsPartnerUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["email"]

    def get_queryset(self):
        queryset = super().get_queryset()
        email = self.request.query_params.get("search", None)
        if email:
            queryset = queryset.filter(
                email__exact=email)
        return queryset


@extend_schema(tags=["Users"])
class PartnerListView(ListAPIView):
    """
    List of partners

    ### Params:
    - `limit`: Quantity of items
    - `offset`: Start index of the items
    - `search` : Text-based search

    ### Access Control:
    - Admin, Superuser

    """

    queryset = User.objects.all().filter(role="partner").order_by("id")
    serializer_class = PartnerListSerializer
    permission_classes = [IsAdmin]


@extend_schema(tags=["Users"])
class BlockUserView(GenericAPIView):
    """
    View responsible for blocking users. Alters flag is_blocked. Which prevents
    users from getting access tokens.

    ### Fields:
    - `email`: Email address
    - `is_blocked`: Block state

    ### Access Control:
    - Admin, Superuser

    ### Implementation Details:
    - Throw an error if state did not change

    """

    queryset = User.objects.all()
    serializer_class = BlockUserSerializer
    permission_classes = [IsAdmin]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data.get("email"))
        if user.role in ("client", "partner"):
            is_blocked = serializer.validated_data.get("is_blocked")
            user.is_blocked = is_blocked
            if is_blocked:
                tokens = OutstandingToken.objects.filter(user=user)
                for token in tokens:
                    BlacklistedToken.objects.get_or_create(token=token)
            user.save()
            return Response("Successful", status=status.HTTP_200_OK)
        return Response("Impossible", status=status.HTTP_403_FORBIDDEN)


@extend_schema(tags=["Users"])
class ClientPasswordForgotPageView(GenericAPIView):
    """
    User password forgot page. View responsible for sending email with reset
    code.

    ### Fields:
    - `email`: Email address

    ### Access Control:
    - Everybody

    ### Implementation Details:
    - Happy Hours does not check if user's email is legit. If email does not
    exist, error won't be displayed

    """

    serializer_class = ClientPasswordForgotPageSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset_code = generate_reset_code()
        user = serializer.validated_data["email"]
        request.session["reset_code"] = str(reset_code)
        time_now = datetime.datetime.now()
        request.session["reset_code_create_time"] = datetime_serializer(time_now)
        send_reset_code_email(user, reset_code)
        return Response("Success", status=status.HTTP_200_OK)


@extend_schema(tags=["Users"])
class ClientPasswordResetView(GenericAPIView):
    """
    User password reset page. View responsible for checking if reset code is
    valid. Then gives access tokens.

    ### Fields:
    - `email`: Email address
    - `reset_code`: Reset code

    ### Access Control:
    - Everybody

    ### Implementation Details:
    - Reset code valid only 5 minutes after email sending

    """

    serializer_class = ClientPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reset_code = serializer.validated_data["reset_code"]

        if (
            "reset_code" in request.session
            and "reset_code_create_time" in request.session
        ):
            stored_code = request.session["reset_code"]
            stored_code_date = datetime_deserializer(
                request.session["reset_code_create_time"]
            )
            passed_time = datetime.datetime.now()

            if (
                stored_code == reset_code
                and (passed_time - stored_code_date).total_seconds() < 600
            ):
                user = User.objects.get(email=serializer.validated_data["email"])
                token = RefreshToken.for_user(user)
                request.session["reset_code"] = ""
                request.session["reset_code_create_time"] = ""
                return Response(
                    {"refresh": str(token), "access": str(token.access_token)}
                )
            elif (passed_time - stored_code_date).total_seconds() >= 600:
                return Response(
                    {
                        "error_code": "2",
                        "message": "Code expired",
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {
                "error_code": "1",
                "message": "Incorrect code",
            },
            status=status.HTTP_400_BAD_REQUEST
        )

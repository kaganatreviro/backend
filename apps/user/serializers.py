from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class TokenObtainSerializer(TokenObtainPairSerializer):
    """
    Token Obtaining Serializer
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token


class ClientRegisterSerializer(serializers.ModelSerializer):
    """
    Individual register view for client user
    """
    password = serializers.CharField(
        write_only=True, required=True, min_length=8
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'password',
            'password_confirm',
        )

    def validate(self, attrs):
        """
        Validating passwords form user input
        :param attrs:
        :return:
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        """
        Creating user with client role
        :param validated_data:
        :return:
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            role='client'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer
    """
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'date_of_birth',
            'avatar',
        )


class PartnerCreateSerializer(serializers.ModelSerializer):
    """
    Individual create view for partner user
    """
    password = serializers.CharField(
        write_only=True, required=True, min_length=8
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'password',
            'password_confirm',
            'max_establishments'
        )

    def validate(self, attrs):
        """
        Validating passwords from user input
        :param attrs:
        :return:
        """
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        """
        Creating user with partner role
        :param validated_data:
        :return:
        """
        user = User.objects.create_user(
            email=validated_data['email'], name=validated_data['name'],
            max_establishments=validated_data['max_establishments'],
            role='partner'
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

from rest_framework import serializers

from .models import Establishment
from .utils import phone_number_validation


class EstablishmentSerializer(serializers.ModelSerializer):
    """
    Main serializer for Establishment model
    """
    class Meta:
        model = Establishment
        fields = (
            'id',
            'name',
            'location_char',
            'description',
            'phone_number',
            'logo',
            'owner',
        )

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.logo != '':
            return request.build_absolute_uri(obj.logo.url)
        else:
            return ''

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['logo'] = self.get_image_url(instance)
        representation['owner'] = instance.owner.username
        return representation


class EstablishmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Establishment
        fields = (
            'id',
            'name',
            'location_char',
            'description',
            'phone_number',
            'logo',
            'owner',
        )

    def create(self, validated_data):
        """
        Create and return a new `Establishment` instance.
        :param validated_data:
        :return:
        """
        phone_number_validation(validated_data)
        establishment = Establishment.objects.create(**validated_data)
        return establishment

    def update(self, instance, validated_data):
        """
        Update existing Establishment instance.
        :param instance:
        :param validated_data:
        :return:
        """
        phone_number_validation(validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
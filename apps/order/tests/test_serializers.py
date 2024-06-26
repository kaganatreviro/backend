from datetime import timedelta

import pytest
from rest_framework import serializers
from rest_framework.test import APIRequestFactory
from django.utils import timezone
from ..serializers import OrderSerializer, OwnerOrderSerializer

from happyhours.factories import UserFactory, EstablishmentFactory, BeverageFactory, OrderFactory
from ..utils import validate_order_per_day, validate_order_per_hour, validate_order_happyhours


@pytest.fixture
def api_request_factory():
    return APIRequestFactory()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def establishment():
    return EstablishmentFactory(happyhours_start='00:00:00', happyhours_end='23:59:59')


@pytest.fixture
def beverage(establishment):
    return BeverageFactory(establishment=establishment)


@pytest.fixture
def order(user, beverage):
    return OrderFactory(client=user, beverage=beverage, establishment=beverage.establishment)


@pytest.mark.django_db
def test_order_serializer_validation(user, beverage, api_request_factory):
    request = api_request_factory.post('/')
    request.user = user

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now()
    }

    serializer = OrderSerializer(data=data, context={'request': request})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_owner_order_serializer_validation(user, beverage, api_request_factory):
    owner = UserFactory(role='owner')
    request = api_request_factory.post('/')
    request.user = owner

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now(),
        'client_email': user.email
    }

    serializer = OwnerOrderSerializer(data=data, context={'request': request})

    assert serializer.is_valid(), serializer.errors


@pytest.mark.django_db
def test_owner_order_serializer_invalid_client_email(user, beverage, api_request_factory):
    owner = UserFactory(role='owner')
    request = api_request_factory.post('/')
    request.user = owner

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now(),
        'client_email': 'nonexistent@example.com'
    }

    serializer = OwnerOrderSerializer(data=data, context={'request': request})

    assert not serializer.is_valid()
    assert 'client_email' in serializer.errors


@pytest.mark.django_db
def test_order_happyhours_validation(order, beverage, api_request_factory):
    request = api_request_factory.post('/')
    request.user = order.client

    # Modify establishment to not be in happy hour
    beverage.establishment.happy_hour_start = timezone.now() + timezone.timedelta(hours=1)
    beverage.establishment.happy_hour_end = timezone.now() + timezone.timedelta(hours=2)
    beverage.establishment.save()

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now()
    }

    serializer = OrderSerializer(data=data, context={'request': request})

    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
def test_order_per_hour_validation(user, beverage, api_request_factory):
    request = api_request_factory.post('/')
    request.user = user

    # Create an order within the last hour
    OrderFactory(client=user, beverage=beverage, establishment=beverage.establishment,
                 order_date=timezone.now() - timezone.timedelta(minutes=30))

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now()
    }

    serializer = OrderSerializer(data=data, context={'request': request})

    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
def test_order_per_day_validation(user, beverage, api_request_factory):
    request = api_request_factory.post('/')
    request.user = user

    # Create an order earlier today
    OrderFactory(client=user, beverage=beverage, establishment=beverage.establishment,
                 order_date=timezone.now() - timezone.timedelta(hours=3))

    data = {
        'beverage': beverage.id,
        'order_date': timezone.now()
    }

    serializer = OrderSerializer(data=data, context={'request': request})

    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors


@pytest.mark.django_db
def test_validate_order_happyhours():
    establishment = EstablishmentFactory()

    establishment.is_happy_hour = lambda: False
    with pytest.raises(serializers.ValidationError, match="Order can only be placed during happy hours."):
        validate_order_happyhours(establishment)

    establishment.is_happy_hour = lambda: True
    try:
        validate_order_happyhours(establishment)
    except serializers.ValidationError:
        pytest.fail("Validation should not fail during happy hours")


@pytest.mark.django_db
def test_validate_order_per_hour():
    client = UserFactory()

    OrderFactory(client=client, status='pending')
    with pytest.raises(serializers.ValidationError, match="You can only place one order per hour."):
        validate_order_per_hour(client)



@pytest.mark.django_db
def test_validate_order_per_day():
    client = UserFactory()
    establishment = EstablishmentFactory()

    OrderFactory(client=client, establishment=establishment, order_date=timezone.now(), status='pending')
    with pytest.raises(serializers.ValidationError, match="You can only place one order per establishment per day."):
        validate_order_per_day(client, establishment)


from rest_framework import serializers
from .models import Beverage, Category
from .schema_definitions import beverage_serializer_schema


class CategorySerializer(serializers.ModelSerializer):
    beverages = serializers.HyperlinkedRelatedField(
        many=True, read_only=True, view_name="v1:beverage-detail"
    )

    class Meta:
        model = Category
        fields = ["id", "name", "beverages"]


@beverage_serializer_schema
class BeverageSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Beverage
        fields = [
            "id",
            "name",
            "price",
            "description",
            "availability_status",
            "establishment",
            "category",
            "category_id",
        ]

    def to_representation(self, instance):
        """Modify the output of the GET method to show names instead of IDs."""
        ret = super().to_representation(instance)
        ret["category"] = instance.category.name if instance.category else None
        ret["category_id"] = instance.category.id
        ret["establishment"] = (
            instance.establishment.name if instance.establishment else None
        )
        return ret

    def validate_establishment(self, value):
        user = self.context["request"].user
        if value.owner != user:
            raise serializers.ValidationError("User does not own this establishment.")
        return value

    def validate_price(self, value):
        """
        Check that the price is not negative.
        Check that price is between 50 and 999
        """
        if value < 0:
            raise serializers.ValidationError("The price must be a non-negative number.")
        if not 50 <= value <= 999:
            raise serializers.ValidationError("The price must be between 50 and 999.")
        return value


from rest_framework import serializers
import re

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "id",
            "name",
            "phone",
            "age",
            "hobby",
            "address",
            "avatar",
            "last_active_at",
            "created_at",
            "updated_at",
        ]


class MallRegisterSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=64)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate_phone(self, value):
        v = value.strip()
        if not re.fullmatch(r"1\d{10}", v):
            raise serializers.ValidationError("手机号格式不正确")
        if Customer.objects.filter(phone=v).exists():
            raise serializers.ValidationError("手机号已注册")
        return v

    def validate_password(self, value):
        if not re.fullmatch(r"\d{6,}", value or ""):
            raise serializers.ValidationError("密码必须为至少6位纯数字")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        phone = validated_data["phone"]
        customer = Customer(
            phone=phone,
            name=(validated_data.get("name") or f"用户{phone[-4:]}").strip() or f"用户{phone[-4:]}",
            age=None,
            hobby="",
            address="",
        )
        customer.set_password(password)
        customer.save()
        return customer


class MallLoginSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=64)

    def validate_phone(self, value):
        return value.strip()

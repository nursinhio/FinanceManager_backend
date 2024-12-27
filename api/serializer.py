from rest_framework import serializers
from .models import Expense, User


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ('id', 'amount', 'category', 'description', 'date', 'user')
        read_only_fields = ('user',)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields=['email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

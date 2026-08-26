from rest_framework import serializers
from users.models import User, Payment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone', 'city', 'avatar', 'password')
        extra_kwargs = {'password': {'write_only': True}}  # Пароль нельзя будет прочитать в GET-ответе

    def create(self, validated_data):
        # Переопределяем создание, чтобы захешировать пароль
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

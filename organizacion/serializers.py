from rest_framework import serializers
from core.models import Departamento, Direccion, Profile
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ('id', 'cargo', 'user')


class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = ('id', 'nombre_direccion')


class DepartamentoSerializer(serializers.ModelSerializer):
    direccion_nombre = serializers.CharField(
        source='direccion.nombre_direccion',
        read_only=True
    )
    encargado_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Departamento
        fields = (
            'id',
            'nombre_departamento',
            'estado',
            'encargado',
            'direccion',
            'direccion_nombre',
            'encargado_nombre',
        )
def get_encargado_nombre(self, obj):
        if obj.encargado:
            return f"{obj.encargado.user.first_name} {obj.encargado.user.last_name}"
        return "sin encargado"
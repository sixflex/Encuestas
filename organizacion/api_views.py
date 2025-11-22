from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Departamento, Direccion
from registration.models import Profile
from .serializers import DepartamentoSerializer, DireccionSerializer, ProfileSerializer

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all().select_related('direccion', 'encargado__user')
    serializer_class = DepartamentoSerializer
    permission_classes = [IsAuthenticated]


class DireccionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Direccion.objects.filter(estado=True)
    serializer_class = DireccionSerializer
    permission_classes = [IsAuthenticated]


class EncargadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all().select_related('user')
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

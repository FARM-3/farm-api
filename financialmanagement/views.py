from django.shortcuts import render
from rest_framework import viewsets
from .models import Wage
from .serializers import WageSerializer

# Create your views here.
class WageViewSet(viewsets.ModelViewSet):
    queryset = Wage.objects.all()
    serializer_class = WageSerializer

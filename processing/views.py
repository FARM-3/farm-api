from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Fermenting,Washing,Sundrying,Bagging
from .serializers import (
    FermentingSerializer,
    WashingSerializer,
    SundryingSerializer,
    BaggingSerializer

)


class FermentingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fermenting process
    
    Automatically provides these endpoints:
    - GET /api/fermenting/ - List all records
    - POST /api/fermenting/ - Create new record
    - GET /api/fermenting/{id}/ - Get single record
    - PUT /api/fermenting/{id}/ - Update record (full)
    - PATCH /api/fermenting/{id}/ - Update record (partial)
    - DELETE /api/fermenting/{id}/ - Delete record
    """
    queryset = Fermenting.objects.all()
    serializer_class = FermentingSerializer
    
    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Fields you can filter by: /api/fermenting/?grade=A&days=3
    filterset_fields = ['grade', 'days', 'date']
    
    # Fields you can search in: /api/fermenting/?search=batch1
    search_fields = ['processing_id', 'name']
    
    # Fields you can order by: /api/fermenting/?ordering=-date
    ordering_fields = ['date', 'weight_before', 'created_at']
    
    # Default ordering
    ordering = ['-date']
    
"""    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
       #Custom endpoint: /api/fermenting/summary/
       #Returns summary statistics for all fermentation batches
"""
        queryset = self.get_queryset()
        total_batches = queryset.count()
        total_weight_before = sum(f.weight_before for f in queryset)
        total_weight_after = sum(f.weight_after for f in queryset)
        
        return Response({
            'total_batches': total_batches,
            'total_weight_before': float(total_weight_before),
            'total_weight_after': float(total_weight_after),
            'total_weight_loss': float(total_weight_before - total_weight_after),
            'average_days': queryset.aggregate(avg_days=models.Avg('days'))['avg_days']
        })
"""

class WashingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Washing process
    Provides full CRUD operations
    """
    queryset = Washing.objects.all()
    serializer_class = WashingSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'date']
    search_fields = ['processing_id', 'name']
    ordering_fields = ['date', 'weight_before', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Custom endpoint: /api/washing/summary/
        """
        queryset = self.get_queryset()
        total_batches = queryset.count()
        total_weight_before = sum(w.weight_before for w in queryset)
        total_weight_after = sum(w.weight_after for w in queryset)
        
        return Response({
            'total_batches': total_batches,
            'total_weight_before': float(total_weight_before),
            'total_weight_after': float(total_weight_after),
            'total_weight_loss': float(total_weight_before - total_weight_after)
        })
    

class SundryingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Sundrying process
    Includes weather and moisture tracking
    """
    queryset = Sundrying.objects.all()
    serializer_class = SundryingSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'weather', 'date']
    search_fields = ['processing_id', 'name']
    ordering_fields = ['date', 'temperature', 'moisture_content', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def by_weather(self, request):
        """
        Custom endpoint: /api/sundrying/by_weather/
        Groups sundrying records by weather conditions
        """
        from django.db.models import Count, Avg
        
        weather_stats = self.get_queryset().values('weather').annotate(
            count=Count('id'),
            avg_temperature=Avg('temperature'),
            avg_moisture=Avg('moisture_content'),
            avg_weight_loss=Avg(models.F('weight_before') - models.F('weight_after'))
        )
        
        return Response(weather_stats)
    

class BaggingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bagging process (final stage)
    """
    queryset = Bagging.objects.all()
    serializer_class = BaggingSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'date']
    search_fields = ['processing_id', 'name']
    ordering_fields = ['date', 'weight', 'moisture_content', 'created_at']
    ordering = ['-date']
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Custom endpoint: /api/bagging/summary/
        Returns final bagging statistics
        """
        from django.db.models import Sum, Avg
        
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_batches=Count('id'),
            total_weight=Sum('weight'),
            avg_moisture=Avg('moisture_content')
        )
        
        # Group by grade
        by_grade = queryset.values('grade').annotate(
            count=Count('id'),
            total_weight=Sum('weight')
        )
        
        return Response({
            'overall': stats,
            'by_grade': list(by_grade)
        })


# Import models for custom actions
from django.db.models import Avg, Count, Sum, F


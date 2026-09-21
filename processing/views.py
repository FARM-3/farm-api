from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from aggregation import models
from .models import Fermenting, Washing, NaturalSundrying, Drying, Bagging, Hulling, Ripeness, Floating, Batch
from .serializers import (
    FermentingSerializer,
    WashingSerializer,
    NaturalSundryingSerializer,
    DryingSerializer,
    BaggingSerializer,
    HullingSerializer,
    RipenessSerializer,
    FloatingSerializer,
    BatchSerializer
)


class FermentingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Fermenting process
    Links to grade_id from Floating (Quality Control)

    Automatically provides these endpoints:
    - GET /api/fermenting/ - List all records
    - POST /api/fermenting/ - Create new record
    - GET /api/fermenting/{processing_id}/ - Get single record
    - PUT /api/fermenting/{processing_id}/ - Update record (full)
    - PATCH /api/fermenting/{processing_id}/ - Update record (partial)
    - DELETE /api/fermenting/{processing_id}/ - Delete record
    """
    queryset = Fermenting.objects.all()
    serializer_class = FermentingSerializer

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields you can filter by: /api/fermenting/?grade={grade_id}&days=3
    filterset_fields = ['grade', 'days', 'start_date', 'end_date']

    # Fields you can search in: /api/fermenting/?search=FERM-20250114
    search_fields = ['processing_id', 'grade__grade_id']

    # Fields you can order by: /api/fermenting/?ordering=-end_date
    ordering_fields = ['start_date', 'end_date', 'days', 'weight', 'created_at']

    # Default ordering
    ordering = ['-end_date']
    

class WashingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Washing process
    Links to grade_id from Floating (Quality Control)
    """
    queryset = Washing.objects.all()
    serializer_class = WashingSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'date']
    search_fields = ['processing_id', 'grade__grade_id']
    ordering_fields = ['date', 'weight', 'created_at']
    ordering = ['-date']


class NaturalSundryingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Natural Sundrying process
    Links to grade_id from Floating (Quality Control)
    """
    queryset = NaturalSundrying.objects.all()
    serializer_class = NaturalSundryingSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['grade', 'start_date']
    search_fields = ['processing_id', 'grade__grade_id']
    ordering_fields = ['start_date', 'weight', 'created_at']
    ordering = ['-start_date']
    

class DryingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Drying process
    Includes daily drying progress tracking with auto-calculated fields
    """
    queryset = Drying.objects.all()
    serializer_class = DryingSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['processing_id', 'lot_id', 'date']
    search_fields = ['processing_id', 'lot_id']
    ordering_fields = ['date', 'moisture_content', 'moisture_deviation', 'outturn', 'created_at']
    ordering = ['-date', '-lot_id']
    

class HullingViewSet(viewsets.ModelViewSet):
    queryset = Hulling.objects.all()
    serializer_class = HullingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lot_id', 'date', 'staff_id']
    search_fields = ['lot_id', 'staff_id']
    ordering_fields = ['date', 'weight_before', 'outturn', 'created_at']
    ordering = ['-date']


class BaggingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Bagging process (final stage)

    Offline-First Approach:
    - Backend is a simple CRUD API
    - Frontend handles ALL business logic, validation, and calculations
    - No complex filtering or custom endpoints

    Automatically provides:
    - GET /api/processing/bagging/ - List all records
    - POST /api/processing/bagging/ - Create new record
    - GET /api/processing/bagging/{id}/ - Get single record
    - PUT /api/processing/bagging/{id}/ - Full update
    - PATCH /api/processing/bagging/{id}/ - Partial update
    - DELETE /api/processing/bagging/{id}/ - Delete record
    """
    queryset = Bagging.objects.all()
    serializer_class = BaggingSerializer

    # Enable basic filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['lot_id', 'date']
    search_fields = ['lot_id']
    ordering_fields = ['date', 'weight', 'moisture_content', 'no_of_bags', 'created_at']
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Custom endpoint: /api/processing/bagging/summary/
        Returns basic bagging statistics (aggregated data)
        """
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_records=Count('id'),
            total_weight=Sum('weight'),
            avg_moisture=Avg('moisture_content'),
            total_bags=Sum('no_of_bags')
        )

        # Group by lot_id for overview
        by_lot = queryset.values('lot_id').annotate(
            record_count=Count('id'),
            total_weight=Sum('weight'),
            avg_moisture=Avg('moisture_content'),
            avg_outturn=Avg('outturn')
        ).order_by('-record_count')

        return Response({
            'overall': stats,
            'by_lot': list(by_lot)
        })


# Import models for custom actions
from django.db.models import Avg, Count, Sum, F


class RipenessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ripeness (Quality Control) testing

    Automatically provides these endpoints:
    - GET /api/ripeness/ - List all ripeness tests
    - POST /api/ripeness/ - Create new ripeness test
    - GET /api/ripeness/{harvest_id}/ - Get ripeness test for specific harvest
    - PUT /api/ripeness/{harvest_id}/ - Update ripeness test (full)
    - PATCH /api/ripeness/{harvest_id}/ - Update ripeness test (partial)
    - DELETE /api/ripeness/{harvest_id}/ - Delete ripeness test
    """
    queryset = Ripeness.objects.all()
    serializer_class = RipenessSerializer

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields you can filter by: /api/ripeness/?date=2025-01-14
    filterset_fields = ['date', 'harvest']

    # Fields you can search in: /api/ripeness/?search=ED0711PA1
    search_fields = ['harvest']

    # Fields you can order by: /api/ripeness/?ordering=-ripeness_score
    ordering_fields = ['date', 'ripeness_score', 'sample_size', 'created_at']

    # Default ordering (most recent first)
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Custom endpoint: /api/ripeness/summary/
        Returns summary statistics for all ripeness tests
        """
        queryset = self.get_queryset()

        if queryset.count() == 0:
            return Response({
                'total_tests': 0,
                'average_ripeness_score': 0,
                'passing_tests': 0,  # >= 80%
                'failing_tests': 0   # < 80%
            })

        total_tests = queryset.count()
        avg_score = queryset.aggregate(Avg('ripeness_score'))['ripeness_score__avg']
        passing = queryset.filter(ripeness_score__gte=80).count()
        failing = queryset.filter(ripeness_score__lt=80).count()

        return Response({
            'total_tests': total_tests,
            'average_ripeness_score': float(avg_score) if avg_score else 0,
            'passing_tests': passing,
            'failing_tests': failing,
            'pass_rate': f"{(passing / total_tests * 100):.2f}%" if total_tests > 0 else "0%"
        })


class FloatingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Floating (Quality Control) testing

    Automatically provides these endpoints:
    - GET /api/floating/ - List all floating tests
    - POST /api/floating/ - Create new floating test
    - GET /api/floating/{grade_id}/ - Get specific floating test
    - PUT /api/floating/{grade_id}/ - Update floating test (full)
    - PATCH /api/floating/{grade_id}/ - Update floating test (partial)
    - DELETE /api/floating/{grade_id}/ - Delete floating test
    """
    queryset = Floating.objects.all()
    serializer_class = FloatingSerializer

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields you can filter by: /api/floating/?grade=A&date=2025-01-14
    filterset_fields = ['grade', 'date', 'harvest']

    # Fields you can search in: /api/floating/?search=GRA1411A00
    search_fields = ['grade_id', 'grade', 'harvest']

    # Fields you can order by: /api/floating/?ordering=-weight
    ordering_fields = ['date', 'weight', 'ripeness_score', 'created_at']

    # Default ordering (most recent first)
    ordering = ['-date']

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Custom endpoint: /api/floating/summary/
        Returns summary statistics grouped by grade
        """
        queryset = self.get_queryset()

        # Overall statistics
        total_tests = queryset.count()
        total_weight = queryset.aggregate(Sum('weight'))['weight__sum'] or 0

        # Group by grade
        by_grade = queryset.values('grade').annotate(
            count=Count('grade_id'),
            total_weight=Sum('weight'),
            avg_weight=Avg('weight')
        ).order_by('grade')

        return Response({
            'overall': {
                'total_tests': total_tests,
                'total_weight': float(total_weight)
            },
            'by_grade': list(by_grade)
        })

    @action(detail=False, methods=['get'], url_path='by-harvest/(?P<harvest_id>[^/.]+)')
    def by_harvest(self, request, harvest_id=None):
        """
        Custom endpoint: /api/floating/by-harvest/{harvest_id}/
        Returns all floating tests for a specific harvest
        """
        tests = self.queryset.filter(harvest__harvest_id=harvest_id)
        serializer = self.get_serializer(tests, many=True)

        # Calculate totals
        total_weight = tests.aggregate(Sum('weight'))['weight__sum'] or 0

        return Response({
            'harvest_id': harvest_id,
            'tests': serializer.data,
            'total_weight': float(total_weight),
            'test_count': tests.count()
        })


class BatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Batch management
    Handles grouping of multiple grade IDs for batch processing

    Automatically provides these endpoints:
    - GET /api/batch/ - List all batches
    - POST /api/batch/ - Create new batch
    - GET /api/batch/{batch_id}/ - Get specific batch
    - PUT /api/batch/{batch_id}/ - Update batch (full)
    - PATCH /api/batch/{batch_id}/ - Update batch (partial)
    - DELETE /api/batch/{batch_id}/ - Delete batch
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer

    # Enable filtering, searching, and ordering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Fields you can filter by: /api/batch/?created_by=John
    filterset_fields = ['created_by', 'created_at']

    # Fields you can search in: /api/batch/?search=BA001
    search_fields = ['batch_id', 'created_by', 'notes']

    # Fields you can order by: /api/batch/?ordering=-created_at
    ordering_fields = ['batch_id', 'created_at', 'updated_at']

    # Default ordering (most recent first)
    ordering = ['-created_at']



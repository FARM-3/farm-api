from rest_framework import viewsets, permissions
from django.contrib.contenttypes.models import ContentType
from .models import Activity
from .serializers import ActivitySerializer

class ActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        """
        Filter activities based on platform.
        - Mobile: Exclude financial activities (sales, expenses, wages)
        - Web: Show all activities
        """
        queryset = Activity.objects.all()
        platform = self.request.query_params.get('platform', 'web')

        if platform == 'mobile':
            # Mobile app: Exclude financial activities
            try:
                from financialmanagement.models import Sales, Expenses, Wages
                excluded_types = ContentType.objects.get_for_models(
                    Sales, Expenses, Wages
                ).values()
                queryset = queryset.exclude(content_type__in=excluded_types)
            except ImportError:
                # Financial models don't exist, no filtering needed
                pass

        # Web app (platform == 'web'): Show all activities, no filtering
        return queryset

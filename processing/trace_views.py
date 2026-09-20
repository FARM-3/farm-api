from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .trace_service import trace_by_code, trace_harvest


class HarvestTrackView(APIView):
    """GET /api/processing/track/{harvest_id}/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, harvest_id):
        data = trace_harvest(harvest_id)
        if not data:
            return Response(
                {'detail': f'Harvest {harvest_id} not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(data)


class TraceScanView(APIView):
    """GET /api/processing/trace/scan/?code=LOT:W12"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.query_params.get('code', '').strip()
        if not code:
            return Response(
                {'detail': 'Query parameter "code" is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = trace_by_code(code)
        if not data:
            return Response(
                {'detail': f'No trace record found for code: {code}'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(data)

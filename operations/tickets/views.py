from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from operations.escalations.services import escalate_target

from .models import Ticket
from .serializers import TicketCommentSerializer, TicketSerializer
from .services import add_ticket_comment, create_ticket


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['priority', 'status', 'assigned_team', 'assigned_to', 'customer', 'incident']
    search_fields = ['ticket_number', 'subject', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'response_due_at', 'resolution_due_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Ticket.objects.filter(company_id=self.request.user.company_id).select_related(
            'company', 'customer', 'incident', 'assigned_team', 'assigned_to', 'created_by'
        ).prefetch_related('comments', 'attachments')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = create_ticket(company_id=request.user.company_id, actor=request.user, data=serializer.validated_data)
        return Response(self.get_serializer(ticket).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        serializer = TicketCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = add_ticket_comment(ticket=self.get_object(), actor=request.user, **serializer.validated_data)
        return Response(TicketCommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        ticket = self.get_object()
        escalate_target(target=ticket, reason=request.data.get('reason', 'Manual ticket escalation'))
        ticket.refresh_from_db()
        return Response(self.get_serializer(ticket).data)


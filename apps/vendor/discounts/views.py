from rest_framework import viewsets, status
from .models import TotalBillPreset, Discount


class TotalBillPresetViewSet(viewsets.ModelViewSet):
    queryset = TotalBillPreset.objects.all()
    serializer_class = TotalBillPresetSerializer


# Discount CRUD + Approve/Reject
class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    @action(detail=True, methods=["post"], url_path="approve")
    def approve_discount(self, request, pk=None):
        discount = self.get_object()
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can approve discounts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        action_type = request.data.get("action", "approve")  # "approve" or "reject"
        if action_type == "approve":
            discount.approval_status = "approved"
        elif action_type == "reject":
            discount.approval_status = "rejected"
        else:
            return Response(
                {"detail": "Invalid action. Use 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount.approved_by = request.user
        discount.approved_at = timezone.now()
        discount.save()
        serializer = self.get_serializer(discount)
        return Response(serializer.data)

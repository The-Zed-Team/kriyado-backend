from rest_framework import viewsets, status

from core.authentication.permission_class import HasVendorBranchPermission
from .models import DiscountPreset, Category, VendorBranchDiscount
from .serializers import (
    CategorySerializer,
    DiscountPresetSerializer,
    VendorBranchDiscountSerializer,
)


class VendorBranchDiscountViewSet(viewsets.ModelViewSet):
    queryset = VendorBranchDiscount.objects.all()
    serializer_class = VendorBranchDiscountSerializer
    permission_classes = [HasVendorBranchPermission]  # Define appropriate permissions

    def get_queryset(self):
        return VendorBranchDiscount.objects.filter(
            vendor_branch=self.request.vendor_branch
        )


class DiscountPresetViewSet(viewsets.ModelViewSet):
    queryset = DiscountPreset.objects.all()
    serializer_class = DiscountPresetSerializer

    def get_queryset(self):
        return DiscountPreset.objects.all()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# class TotalBillPresetViewSet(viewsets.ModelViewSet):
#     queryset = TotalBillPreset.objects.all()
#     serializer_class = TotalBillPresetSerializer


# # Discount CRUD + Approve/Reject
# class DiscountViewSet(viewsets.ModelViewSet):
#     queryset = Discount.objects.all()
#     serializer_class = DiscountSerializer

#     @action(detail=True, methods=["post"], url_path="approve")
#     def approve_discount(self, request, pk=None):
#         discount = self.get_object()
#         if not request.user.is_staff:
#             return Response(
#                 {"detail": "Only admins can approve discounts."},
#                 status=status.HTTP_403_FORBIDDEN,
#             )

#         action_type = request.data.get("action", "approve")  # "approve" or "reject"
#         if action_type == "approve":
#             discount.approval_status = "approved"
#         elif action_type == "reject":
#             discount.approval_status = "rejected"
#         else:
#             return Response(
#                 {"detail": "Invalid action. Use 'approve' or 'reject'."},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         discount.approved_by = request.user
#         discount.approved_at = timezone.now()
#         discount.save()
#         serializer = self.get_serializer(discount)
#         return Response(serializer.data)

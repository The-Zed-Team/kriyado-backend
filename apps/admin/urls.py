from django.urls import path

from apps.admin import views

urlpatterns = [
    path("admin/signup/", views.SignupAdminAPIView.as_view(), name="signup-admin"),
    path("admin/pending/list/", views.PendingAdminListAPIView.as_view(), name="pending-admins"),
    path("admin/approve/activation/<uuid:id>/", views.ApproveAdminAPIView.as_view(), name="approve-admin"),
    path("reject/<uuid:id>/", views.RejectAdminAPIView.as_view(), name="reject-admin"),

    path("admin/role/create/", views.AdminUserRoleCreateAPIView.as_view(), name="admin-role-create"),
    path("admin/role/list/", views.AdminUserRoleListAPIView.as_view(), name="admin-role-list"),
    path("role/update/<uuid:id>/", views.AdminUserRoleUpdateAPIView.as_view(), name="admin-role-update"),
    path("role/delete/<uuid:id>/", views.AdminUserRoleDeleteAPIView.as_view(), name="admin-role-delete"),

    path("user/create/", views.AdminUserCreateAPIView.as_view(), name="admin-user-create"),
    path("admin/super/create/", views.CreateSuperAdminAPIView.as_view(), name="create-super-admin"),

]

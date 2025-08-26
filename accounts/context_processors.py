from .models import CustomUser
from dashboard.models import Tenant

def user_info(request):
    user_data = None
    tenant_data = None

    # Check if a User is logged in
    user_id = request.session.get('user_id')
    if user_id:
        try:
            user_data = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            user_data = None

    # Check if a Tenant is logged in
    tenant_id = request.session.get('tenant_id')
    if tenant_id:
        try:
            tenant_data = Tenant.objects.get(id=tenant_id)
        except Tenant.DoesNotExist:
            tenant_data = None

    return {
        'user_data': user_data,
        'tenant_data': tenant_data
    }

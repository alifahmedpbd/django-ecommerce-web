from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

class OwnerRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != "owner":

            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
    
class StaffRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):

        if request.user.role not in [

            "owner",

            "staff",
        ]:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)
    
class CustomerRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):

        if request.user.role != "customer":

            raise PermissionDenied
    
        return super().dispatch(request, *args, **kwargs)
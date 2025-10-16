from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    change_form_template = "admin/customer/change_form.html"
    list_display = ("first_name", "last_name", "email")
    ordering = ('-id',)
    
    # Only show these fields
    fields = ("first_name", "last_name", "email")
    
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Only show users in Customer group (pk = 1)
        return qs.filter(groups__id = 1)
    
    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        Inject extra context to the change form page.
        This makes 'original' available in the template (used for the customer ID).
        """
        extra_context = extra_context or {}
        extra_context["api_enabled"] = True  # optional flag for conditional JS logic
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
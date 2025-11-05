from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Mess, Membership, Meal, Expense, Deposit, Message


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'phone', 'is_staff']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2'),
        }),
    )

class MealAdmin(admin.ModelAdmin):
    list_display = ['user', 'mess', 'date', 'breakfast', 'lunch', 'dinner', 'total_meals']
    list_filter = ['mess', 'date']

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['mess', 'amount', 'description', 'date', 'created_by']
    list_filter = ['mess', 'date']

class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'mess', 'amount', 'date']
    list_filter = ['mess', 'date']

class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'mess', 'content_short', 'created_at']
    list_filter = ['mess', 'created_at']
    
    def content_short(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_short.short_description = 'Content'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Mess)
admin.site.register(Membership)
admin.site.register(Meal, MealAdmin)
admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Deposit, DepositAdmin)
admin.site.register(Message, MessageAdmin)
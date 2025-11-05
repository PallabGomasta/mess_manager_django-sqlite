from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from datetime import date

class CustomUser(AbstractUser):
    
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="user",
    )
    
    def __str__(self):
        return self.username

class Mess(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = ''.join(random.choices(string.digits, k=6))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Membership(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('member', 'Member'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'mess')
    
    def __str__(self):
        return f"{self.user.username} - {self.mess.name} ({self.role})"
    
    def delete(self, *args, **kwargs):
        """
        Custom delete method that removes all member data when a membership is deleted
        """
        user = self.user
        mess = self.mess
        
        try:
            Meal.objects.filter(user=user, mess=mess).delete()
            Deposit.objects.filter(user=user, mess=mess).delete()
            print(f"Deleted all data for user {user.username} from mess {mess.name}")
            
        except Exception as e:
            print(f"Error deleting member data: {str(e)}")
        
        super().delete(*args, **kwargs)

class Meal(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    date = models.DateField(default=date.today)
    breakfast = models.PositiveIntegerField(default=0)
    lunch = models.PositiveIntegerField(default=0)
    dinner = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    month = models.PositiveIntegerField(blank=True, null=True) 
    year = models.PositiveIntegerField(blank=True, null=True)   
    
    class Meta:
        unique_together = ('user', 'mess', 'date')
    
    def save(self, *args, **kwargs):
        if self.date:
            self.month = self.date.month
            self.year = self.date.year
        super().save(*args, **kwargs)
    
    def total_meals(self):
        return self.breakfast + self.lunch + self.dinner
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"

class Expense(models.Model):
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    date = models.DateField(default=date.today)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    month = models.PositiveIntegerField(blank=True, null=True) 
    year = models.PositiveIntegerField(blank=True, null=True)  
    
    def save(self, *args, **kwargs):
        if self.date:
            self.month = self.date.month
            self.year = self.date.year
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.mess.name} - {self.amount} - {self.date}"

class Deposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    month = models.PositiveIntegerField(blank=True, null=True)  
    year = models.PositiveIntegerField(blank=True, null=True)   
    
    def save(self, *args, **kwargs):
        if self.date:
            self.month = self.date.month
            self.year = self.date.year
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.date}"

class Message(models.Model):
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('alert', 'Alert'),
        ('success', 'Success'),
    )
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    mess = models.ForeignKey(Mess, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
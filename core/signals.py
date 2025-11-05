from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Meal, Expense, Deposit, Membership
from .views import create_notification

@receiver(post_save, sender=Meal)
def meal_created_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(
            user=instance.user,
            title='Meal Entry Added',
            message=f'Meal entry added for {instance.date}: B{instance.breakfast}, L{instance.lunch}, D{instance.dinner}',
            notification_type='info',
            mess=instance.mess
        )

@receiver(post_save, sender=Expense)
def expense_created_notification(sender, instance, created, **kwargs):
    if created:
        members = Membership.objects.filter(mess=instance.mess)
        for member in members:
            create_notification(
                user=member.user,
                title='New Expense Added',
                message=f'New expense: ৳{instance.amount} - {instance.description}',
                notification_type='warning',
                mess=instance.mess
            )

@receiver(post_save, sender=Deposit)
def deposit_created_notification(sender, instance, created, **kwargs):
    if created:
        create_notification(
            user=instance.user,
            title='Deposit Recorded',
            message=f'Deposit of ৳{instance.amount} recorded on {instance.date}',
            notification_type='success',
            mess=instance.mess
        )


from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Membership, Meal, Deposit, Message

@receiver(pre_delete, sender=Membership)
def delete_member_data(sender, instance, **kwargs):
   
    user = instance.user
    mess = instance.mess

    Meal.objects.filter(user=user, mess=mess).delete()
    Deposit.objects.filter(user=user, mess=mess).delete()
    print(f"Deleted all data for user {user.username} from mess {mess.name}")

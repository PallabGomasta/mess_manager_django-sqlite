from .models import Notification

def notification_count(request):
    if request.user.is_authenticated:
        try:
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            return {'unread_notification_count': unread_count}
        except:
            return {'unread_notification_count': 0}
    return {'unread_notification_count': 0}
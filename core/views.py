from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .models import Mess, Membership, Meal, Expense, Deposit, Message, CustomUser, Notification
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages
from django.db import models
from datetime import date, datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
import json
from calendar import month_name

def home(request):
    user_messes = None
    if request.user.is_authenticated:
        user_messes = Membership.objects.filter(user=request.user).select_related('mess')
    return render(request, 'core/home.html', {'user_messes': user_messes})

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('home')
        else:
           
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')

                user_messes = Membership.objects.filter(user=request.user)
                if user_messes.exists():
                    first_mess = user_messes.first()
                    if first_mess.role == 'manager':
                        return redirect('mess_dashboard', mess_id=first_mess.mess.id)
                    else:
                        return redirect('member_dashboard', mess_id=first_mess.mess.id)
                else:
                    return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def create_mess(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')

        mess = Mess.objects.create(name=name, address=address)
        Membership.objects.create(user=request.user, mess=mess, role='manager')
        
        messages.success(request, f'Mess "{name}" created successfully! Your mess code is: {mess.code}')
        return redirect('home')
    
    return redirect('home')

@login_required
def join_mess(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        
        try:
            mess = Mess.objects.get(code=code)
            if not Membership.objects.filter(user=request.user, mess=mess).exists():
                Membership.objects.create(user=request.user, mess=mess, role='member')
                messages.success(request, f'Successfully joined {mess.name}!')
                
                return redirect('member_dashboard', mess_id=mess.id)
            else:
                messages.info(request, 'You are already a member of this mess.')
                membership = Membership.objects.get(user=request.user, mess=mess)
                if membership.role == 'manager':
                    return redirect('mess_dashboard', mess_id=mess.id)
                else:
                    return redirect('member_dashboard', mess_id=mess.id)
                    
        except Mess.DoesNotExist:
            messages.error(request, 'Invalid mess code. Please try again.')
        except Membership.DoesNotExist:
            messages.error(request, 'Membership error. Please try again.')
    
    return redirect('home')

@login_required
def dashboard(request):
    user_messes = Membership.objects.filter(user=request.user, role='manager').select_related('mess')
    
    if not user_messes:
        messages.warning(request, 'You are not a manager of any mess.')
        return redirect('home')
    
    first_mess = user_messes.first().mess if user_messes.first() else None
    if first_mess:
        return redirect('mess_dashboard', mess_id=first_mess.id)
    else:
        messages.error(request, 'No mess found.')
        return redirect('home')

@login_required
def mess_dashboard(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        if membership.role != 'manager':
            messages.error(request, 'You do not have permission to access this mess.')
            return redirect('home')

        total_members = Membership.objects.filter(mess=mess).count()
        
        meals = Meal.objects.filter(mess=mess)
        total_meals = 0
        for meal in meals:
            total_meals += meal.breakfast + meal.lunch + meal.dinner
        
        expense_agg = Expense.objects.filter(mess=mess).aggregate(total=models.Sum('amount'))
        total_expense = expense_agg['total'] or 0
         
        deposit_agg = Deposit.objects.filter(mess=mess).aggregate(total=models.Sum('amount'))
        total_deposit = deposit_agg['total'] or 0
        
        context = {
            'mess': mess,
            'membership': membership,
            'total_members': total_members,
            'total_meals': total_meals,
            'total_expense': total_expense,
            'total_deposit': total_deposit,
        }
        
        return render(request, 'core/manager/dashboard.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def manage_members(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)

        if membership.role != 'manager':
            messages.error(request, 'You do not have permission to manage members.')
            return redirect('home')
        
        members = Membership.objects.filter(mess=mess).select_related('user')
        
        context = {
            'mess': mess,
            'members': members,
        }
        
        return render(request, 'core/manager/manage_members.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def remove_member(request, mess_id, user_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        user_membership = get_object_or_404(Membership, user=request.user, mess=mess)

        if user_membership.role != 'manager':
            messages.error(request, 'You do not have permission to remove members.')
            return redirect('home')
        
        if request.user.id == user_id:
            messages.error(request, 'You cannot remove yourself as manager.')
            return redirect('manage_members', mess_id=mess_id)

        member_to_remove = get_object_or_404(Membership, user__id=user_id, mess=mess)
        username = member_to_remove.user.username
        member_to_remove.delete()
        
        messages.success(request, f'Member {username} has been removed successfully.')
        return redirect('manage_members', mess_id=mess_id)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Member not found or you do not have access.')
        return redirect('home')

@login_required
def update_accounts(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)

        if membership.role != 'manager':
            messages.error(request, 'You do not have permission to update accounts.')
            return redirect('home')
        
        members = Membership.objects.filter(mess=mess).select_related('user')
        today = date.today()
        
        today_meals = Meal.objects.filter(mess=mess, date=today)
        today_expenses = Expense.objects.filter(mess=mess, date=today)
        today_deposits = Deposit.objects.filter(mess=mess, date=today)
        
        context = {
            'mess': mess,
            'members': members,
            'today': today,
            'today_meals': today_meals,
            'today_expenses': today_expenses,
            'today_deposits': today_deposits,
        }
        
        return render(request, 'core/manager/update_accounts.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def add_meal(request, mess_id):
    if request.method == 'POST':
        try:
            mess = get_object_or_404(Mess, id=mess_id)
            membership = get_object_or_404(Membership, user=request.user, mess=mess)
            
            if membership.role != 'manager':
                messages.error(request, 'Permission denied.')
                return redirect('home')
            
            user_id = request.POST.get('user')
            meal_date_str = request.POST.get('date')  
            breakfast = int(request.POST.get('breakfast', 0))
            lunch = int(request.POST.get('lunch', 0))
            dinner = int(request.POST.get('dinner', 0))
            
            
            try:
                meal_date = datetime.strptime(meal_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                meal_date = date.today()
            
            user = get_object_or_404(CustomUser, id=user_id)
            
            meal, created = Meal.objects.update_or_create(
                user=user, mess=mess, date=meal_date,  
                defaults={'breakfast': breakfast, 'lunch': lunch, 'dinner': dinner}
            )
            
            if created:
                messages.success(request, f'Meal entry created for {user.username} on {meal_date}')
            else:
                messages.success(request, f'Meal entry updated for {user.username} on {meal_date}')
            
        except (ValueError, CustomUser.DoesNotExist) as e:
            messages.error(request, f'Invalid data provided: {str(e)}')
        
        return redirect('update_accounts', mess_id=mess_id)
    return redirect('update_accounts', mess_id=mess_id)


@login_required
def add_expense(request, mess_id):
    if request.method == 'POST':
        try:
            mess = get_object_or_404(Mess, id=mess_id)
            membership = get_object_or_404(Membership, user=request.user, mess=mess)
            
            if membership.role != 'manager':
                messages.error(request, 'Permission denied.')
                return redirect('home')
            
            amount = float(request.POST.get('amount', 0))
            description = request.POST.get('description', '').strip()
            expense_date_str = request.POST.get('date')
            
            
            try:
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                expense_date = date.today()
            
           
            if description:
                Expense.objects.create(
                    mess=mess,
                    amount=amount,
                    description=description,
                    date=expense_date, 
                    created_by=request.user
                )
                if amount < 0:
                    messages.success(request, f'Expense adjustment of {amount} added successfully.')
                else:
                    messages.success(request, 'Expense added successfully.')
            else:
                messages.error(request, 'Please provide a description.')
                
        except ValueError as e:
            messages.error(request, f'Invalid amount provided: {str(e)}')
        
        return redirect('update_accounts', mess_id=mess_id)
    return redirect('update_accounts', mess_id=mess_id)

@login_required
def add_deposit(request, mess_id):
    if request.method == 'POST':
        try:
            mess = get_object_or_404(Mess, id=mess_id)
            membership = get_object_or_404(Membership, user=request.user, mess=mess)
            
            if membership.role != 'manager':
                messages.error(request, 'Permission denied.')
                return redirect('home')
            
            user_id = request.POST.get('user')
            amount = float(request.POST.get('amount', 0))
            deposit_date_str = request.POST.get('date')
            
            
            try:
                deposit_date = datetime.strptime(deposit_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                deposit_date = date.today()
            
            user = get_object_or_404(CustomUser, id=user_id)
            
            
            Deposit.objects.create(
                user=user,
                mess=mess,
                amount=amount,
                date=deposit_date  
            )
            
            if amount < 0:
                messages.success(request, f'Deposit adjustment of {amount} added for {user.username}.')
            else:
                messages.success(request, f'Deposit of {amount} added for {user.username}.')
                
        except (ValueError, CustomUser.DoesNotExist) as e:
            messages.error(request, f'Invalid data provided: {str(e)}')
        
        return redirect('update_accounts', mess_id=mess_id)
    return redirect('update_accounts', mess_id=mess_id)


@login_required
def view_reports(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        if membership.role != 'manager':
            messages.error(request, 'You do not have permission to view reports.')
            return redirect('home')

        selected_month = request.GET.get('month', datetime.now().month)
        selected_year = request.GET.get('year', datetime.now().year)
        
        try:
            selected_month = int(selected_month)
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            selected_month = datetime.now().month
            selected_year = datetime.now().year

        first_day = date(selected_year, selected_month, 1)
        if selected_month == 12:
            last_day = date(selected_year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(selected_year, selected_month + 1, 1) - timedelta(days=1)

        meals = Meal.objects.filter(mess=mess, date__range=[first_day, last_day])
        expenses = Expense.objects.filter(mess=mess, date__range=[first_day, last_day])
        deposits = Deposit.objects.filter(mess=mess, date__range=[first_day, last_day])
        members = Membership.objects.filter(mess=mess)
        
        total_expense = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        total_deposit = deposits.aggregate(total=models.Sum('amount'))['total'] or 0
        
        grand_total_meals = 0
        member_meals = {}
        
        for meal in meals:
            total_meals = meal.breakfast + meal.lunch + meal.dinner
            grand_total_meals += total_meals
            if meal.user.id not in member_meals:
                member_meals[meal.user.id] = 0
            member_meals[meal.user.id] += total_meals
        
        meal_rate = total_expense / grand_total_meals if grand_total_meals > 0 else 0
        
        member_reports = []
        for member in members:
            total_meal = member_meals.get(member.user.id, 0)
            total_cost = total_meal * meal_rate
            member_deposit = deposits.filter(user=member.user).aggregate(total=models.Sum('amount'))['total'] or 0
            balance = member_deposit - total_cost
            
            member_reports.append({
                'user': member.user,
                'total_meal': total_meal,
                'total_cost': total_cost,
                'total_deposit': member_deposit,
                'balance': balance,
                'role': member.role
            })
        
        months = [(i, month_name[i]) for i in range(1, 13)]
        current_year = datetime.now().year
        years = list(range(current_year - 2, current_year + 1))
        
        context = {
            'mess': mess,
            'month': first_day.strftime("%B %Y"),
            'selected_month': selected_month,
            'selected_year': selected_year,
            'months': months,
            'years': years,
            'grand_total_meals': grand_total_meals,
            'total_expense': total_expense,
            'total_deposit': total_deposit,
            'meal_rate': meal_rate,
            'member_reports': member_reports,
            'expenses': expenses,
            'deposits': deposits,
        }
        
        return render(request, 'core/manager/view_reports.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def download_report_pdf(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        if membership.role != 'manager':
            messages.error(request, 'Only managers can download reports.')
            return redirect('home')
        
        selected_month = request.GET.get('month', datetime.now().month)
        selected_year = request.GET.get('year', datetime.now().year)
        
        try:
            selected_month = int(selected_month)
            selected_year = int(selected_year)
        except (ValueError, TypeError):
            selected_month = datetime.now().month
            selected_year = datetime.now().year

        first_day = date(selected_year, selected_month, 1)
        if selected_month == 12:
            last_day = date(selected_year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(selected_year, selected_month + 1, 1) - timedelta(days=1)
        
        meals = Meal.objects.filter(mess=mess, date__range=[first_day, last_day])
        expenses = Expense.objects.filter(mess=mess, date__range=[first_day, last_day])
        deposits = Deposit.objects.filter(mess=mess, date__range=[first_day, last_day])
        members = Membership.objects.filter(mess=mess)
        
        total_expense = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
        total_deposit = deposits.aggregate(total=models.Sum('amount'))['total'] or 0
     
        grand_total_meals = 0
        member_meals = {}
        
        for meal in meals:
            total_meals = meal.breakfast + meal.lunch + meal.dinner
            grand_total_meals += total_meals
            if meal.user.id not in member_meals:
                member_meals[meal.user.id] = 0
            member_meals[meal.user.id] += total_meals
        
        meal_rate = total_expense / grand_total_meals if grand_total_meals > 0 else 0
        
        member_reports = []
        for member in members:
            total_meal = member_meals.get(member.user.id, 0)
            total_cost = total_meal * meal_rate
            member_deposit = deposits.filter(user=member.user).aggregate(total=models.Sum('amount'))['total'] or 0
            balance = member_deposit - total_cost
            
            member_reports.append({
                'user': member.user,
                'total_meal': total_meal,
                'total_cost': total_cost,
                'total_deposit': member_deposit,
                'balance': balance,
                'role': member.role
            })
        
        context = {
            'mess': mess,
            'month': first_day.strftime("%B %Y"),
            'selected_month': selected_month,
            'selected_year': selected_year,
            'grand_total_meals': grand_total_meals,
            'total_expense': total_expense,
            'total_deposit': total_deposit,
            'meal_rate': meal_rate,
            'member_reports': member_reports,
            'expenses': expenses,
            'deposits': deposits,
        }
        
        html_string = render_to_string('core/manager/report_pdf_simple.html', context)
        
        result = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            filename = f"{mess.name}_report_{selected_month}_{selected_year}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        return HttpResponse('Error generating PDF: ' + str(pdf.err))
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')
    except Exception as e:
        messages.error(request, f'Error generating PDF: {str(e)}')
        return redirect('view_reports', mess_id=mess_id)
    
@login_required
def role_change(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        current_user_membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        if current_user_membership.role != 'manager':
            messages.error(request, 'Only managers can change roles.')
            return redirect('home')
        
        members = Membership.objects.filter(mess=mess).exclude(user=request.user)
        
        if request.method == 'POST':
            new_manager_id = request.POST.get('new_manager')
            
            try:
                new_manager_membership = get_object_or_404(Membership, id=new_manager_id, mess=mess)

                current_user_membership.role = 'member'
                current_user_membership.save()
                
                new_manager_membership.role = 'manager'
                new_manager_membership.save()
                
                messages.success(request, f'Manager role transferred to {new_manager_membership.user.username}. You are now a member.')
                return redirect('home')
                
            except (Membership.DoesNotExist, ValueError):
                messages.error(request, 'Invalid selection.')
        
        context = {
            'mess': mess,
            'members': members,
            'current_user_membership': current_user_membership,
        }
        
        return render(request, 'core/manager/role_change.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def member_mess_list(request):
    user_messes = Membership.objects.filter(user=request.user).select_related('mess')
    return render(request, 'core/member/mess_list.html', {'user_messes': user_messes})

@login_required
def member_dashboard(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)

        today = datetime.now().date()
        first_day = today.replace(day=1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        member_meals = Meal.objects.filter(user=request.user, mess=mess, date__range=[first_day, last_day])
        member_deposits = Deposit.objects.filter(user=request.user, mess=mess, date__range=[first_day, last_day])

        total_meals = sum(meal.breakfast + meal.lunch + meal.dinner for meal in member_meals)
        total_deposit = member_deposits.aggregate(total=models.Sum('amount'))['total'] or 0

        mess_expenses = Expense.objects.filter(mess=mess, date__range=[first_day, last_day])
        total_expense = mess_expenses.aggregate(total=models.Sum('amount'))['total'] or 0
 
        all_meals = Meal.objects.filter(mess=mess, date__range=[first_day, last_day])
        grand_total_meals = sum(meal.breakfast + meal.lunch + meal.dinner for meal in all_meals)
        meal_rate = total_expense / grand_total_meals if grand_total_meals > 0 else 0
        
        total_cost = total_meals * meal_rate
        balance = total_deposit - total_cost
        
        context = {
            'mess': mess,
            'membership': membership,
            'total_meals': total_meals,
            'total_deposit': total_deposit,
            'total_cost': total_cost,
            'balance': balance,
            'meal_rate': meal_rate,
            'month': first_day.strftime("%B %Y"),
            'member_meals': member_meals,
            'member_deposits': member_deposits,
        }
        
        return render(request, 'core/member/dashboard.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def member_members(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        members = Membership.objects.filter(mess=mess).select_related('user')
        
        context = {
            'mess': mess,
            'membership': membership,
            'members': members,
        }
        
        return render(request, 'core/member/members.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

@login_required
def messages_view(request, mess_id):
    try:
        mess = get_object_or_404(Mess, id=mess_id)
        membership = get_object_or_404(Membership, user=request.user, mess=mess)
        
        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            if content:
                Message.objects.create(
                    mess=mess,
                    user=request.user,
                    content=content
                )
                messages.success(request, 'Message sent successfully!')
                if membership.role == 'manager':
                    return redirect('manager_messages', mess_id=mess_id)
                else:
                    return redirect('member_messages', mess_id=mess_id)
        
        mess_messages = Message.objects.filter(mess=mess).select_related('user').order_by('-created_at')[:50]
        
        context = {
            'mess': mess,
            'membership': membership,
            'messages': mess_messages,
        }

        if membership.role == 'manager':
            return render(request, 'core/manager/messages.html', context)
        else:
            return render(request, 'core/member/messages.html', context)
        
    except (Mess.DoesNotExist, Membership.DoesNotExist):
        messages.error(request, 'Mess not found or you do not have access.')
        return redirect('home')

def create_notification(user, title, message, notification_type='info', mess=None):
    """Helper function to create notifications"""
    Notification.objects.create(
        user=user,
        mess=mess,
        title=title,
        message=message,
        notification_type=notification_type
    )

@login_required
def notifications_view(request):
    """View user notifications"""
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = user_notifications.filter(is_read=False).count()
    
    user_notifications.update(is_read=True)
    
    context = {
        'notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'core/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

@login_required
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'success': True})

@login_required
def get_unread_count(request):
    """API endpoint for unread notification count"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})
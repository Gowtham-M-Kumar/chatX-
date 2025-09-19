from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from userauth.models import Post, Profile, Reel
from django.contrib import messages
from .models import UserBlock
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin, login_url='/loginn')
def admin_dashboard(request):
    user_count = User.objects.count()
    post_count = Post.objects.count()
    reel_count = Reel.objects.count()
    blocked_users_count = UserBlock.objects.filter(is_blocked=True).count()
    
    recent_users = Profile.objects.select_related('user').order_by('-user__date_joined')[:5]
    recent_posts = Post.objects.all().order_by('-created_at')[:5]
    recent_reels = Reel.objects.all().order_by('-created_at')[:5]
    
    context = {
        'user_count': user_count,
        'post_count': post_count,
        'reel_count': reel_count,
        'blocked_users_count': blocked_users_count,
        'recent_users': recent_users,
        'recent_posts': recent_posts,
        'recent_reels': recent_reels,
    }
    return render(request, 'customadmin/dashboard.html', context)


@user_passes_test(is_admin, login_url='/loginn')
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    
    # Prepare user data with block status
    user_data = []
    for user in users:
        try:
            user_block = UserBlock.objects.get(user=user)
            is_blocked = user_block.is_currently_blocked()
            days_remaining = user_block.days_remaining()
            reason = user_block.reason
        except UserBlock.DoesNotExist:
            is_blocked = False
            days_remaining = 0
            reason = ''
        
        # Count posts by username (since Post.user is CharField, not ForeignKey)
        post_count = Post.objects.filter(user=user.username).count()
        reel_count = Reel.objects.filter(user=user.username).count()
        
        user_data.append({
            'user': user,
            'is_blocked': is_blocked,
            'days_remaining': days_remaining,
            'reason': reason,
            'post_count': post_count,
            'reel_count': reel_count
        })
    
    context = {
        'user_data': user_data,
    }
    return render(request, 'customadmin/user_list.html', context)


@user_passes_test(is_admin, login_url='/loginn')
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    context = {'posts': posts}
    return render(request, 'customadmin/post_list.html', context)

@user_passes_test(is_admin, login_url='/loginn')
def reel_list(request):
    reels = Reel.objects.all().order_by('-created_at')
    context = {'reels': reels}
    return render(request, 'customadmin/reel_list.html', context)

@user_passes_test(is_admin, login_url='/loginn')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        Post.objects.filter(user=user.username).delete()
        Reel.objects.filter(user=user.username).delete()
        Profile.objects.filter(user=user).delete()
        UserBlock.objects.filter(user=user).delete()
        user.delete()
        
        messages.success(request, f'User {user.username} has been deleted successfully.')
        return redirect('customadmin:user_list')
    
    context = {'user': user}
    return render(request, 'customadmin/confirm_delete_user.html', context)

@user_passes_test(is_admin, login_url='/loginn')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post has been deleted successfully.')
        return redirect('customadmin:post_list')
    
    context = {'post': post}
    return render(request, 'customadmin/confirm_delete_post.html', context)

@user_passes_test(is_admin, login_url='/loginn')
def delete_reel(request, reel_id):
    reel = get_object_or_404(Reel, id=reel_id)
    
    if request.method == 'POST':
        reel.delete()
        messages.success(request, 'Reel has been deleted successfully.')
        return redirect('customadmin:reel_list')
    
    context = {'reel': reel}
    return render(request, 'customadmin/confirm_delete_reel.html', context)

@user_passes_test(is_admin, login_url='/loginn')
def toggle_block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Get or create UserBlock
    user_block, created = UserBlock.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        duration = int(request.POST.get('duration', 7))
        
        if action == 'block':
            user_block.is_blocked = True
            user_block.reason = request.POST.get('reason', '')
            user_block.blocked_until = timezone.now() + timedelta(days=duration)
            user_block.save()
            messages.success(request, f'User {user.username} has been blocked for {duration} days.')
        elif action == 'unblock':
            user_block.is_blocked = False
            user_block.save()
            messages.success(request, f'User {user.username} has been unblocked.')
        
        return redirect('customadmin:user_list')
    
    context = {
        'user': user,
        'is_blocked': user_block.is_currently_blocked(),
        'block_info': user_block,
    }
    return render(request, 'customadmin/toggle_block_user.html', context)
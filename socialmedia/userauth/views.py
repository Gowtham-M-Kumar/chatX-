from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Followers, LikePost, Post, Profile, Comment, Reel, LikeReel
from django.db.models import Q
from django.contrib import messages

def signup(request):
    try:
        if request.method == 'POST':
            fnm = request.POST.get('fnm')
            emailid = request.POST.get('emailid')
            pwd = request.POST.get('pwd')
            print(fnm, emailid, pwd)
            my_user = User.objects.create_user(fnm, emailid, pwd)
            my_user.save()
            user_model = User.objects.get(username=fnm)
            new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
            new_profile.save()
            if my_user is not None:
                login(request, my_user)
                return redirect('/')
            return redirect('/loginn')
    except:
        invalid = "User already exists"
        return render(request, 'signup.html', {'invalid': invalid})
    return render(request, 'signup.html')

def loginn(request):
    if request.method == 'POST':
        fnm = request.POST.get('fnm')
        pwd = request.POST.get('pwd')
        print(fnm, pwd)
        userr = authenticate(request, username=fnm, password=pwd)
        if userr is not None:
            login(request, userr)
            return redirect('/')
        invalid = "Invalid Credentials"
        return render(request, 'loginn.html', {'invalid': invalid})
    return render(request, 'loginn.html')

@login_required(login_url='/loginn')
def logoutt(request):
    logout(request)
    return redirect('/loginn')

@login_required(login_url='/loginn')
def home(request):
    try:
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'id_user': request.user.id,
                'bio': '',
                'profileimg': 'blank-profile-picture.png',
                'location': ''
            }
        )

        following_users = Followers.objects.filter(follower=request.user.username).values_list('user', flat=True)
        post_list = Post.objects.filter(Q(user=request.user.username) | Q(user__in=following_users)).order_by('-created_at')

        # Build a dictionary of comments for each post
        post_comments = {p.id: p.comments.order_by('created_at') for p in post_list}

        context = {
            'post': post_list,
            'profile': profile,
            'post_comments': post_comments,
        }
        return render(request, 'main.html', context)
    except Exception as e:
        print(f"Error in home view: {e}")
        return redirect('/loginn')

@login_required(login_url='/loginn')
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')

@login_required(login_url='/loginn')
def likes(request, id):
    if request.method == 'GET':
        username = request.user.username
        post = get_object_or_404(Post, id=id)
        like_filter = LikePost.objects.filter(post_id=id, username=username).first()
        if like_filter is None:
            new_like = LikePost.objects.create(post_id=id, username=username)
            post.no_of_likes = post.no_of_likes + 1
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes - 1
        post.save()
        # Redirect back to the post's detail page
        print(post.id)
        return redirect('/#' + str(id))

@login_required(login_url='/loginn')
def explore(request):
    post_list = Post.objects.all().order_by('-created_at')
    profile = Profile.objects.get(user=request.user)
    post_comments = {p.id: p.comments.order_by('created_at') for p in post_list}
    context = {
        'post': post_list,
        'profile': profile,
        'post_comments': post_comments,
    }
    return render(request, 'explore.html', context)


@login_required(login_url='/loginn')
def profile(request, id_user):
    try:
        user_object = User.objects.get(username=id_user)
    except User.DoesNotExist:
        messages.error(request, "User does not exist.")
        return redirect('/')
    
    try:
        profile = Profile.objects.get(user=request.user)
        user_profile = Profile.objects.get(user=user_object)
    except Profile.DoesNotExist:
        messages.error(request, "Profile does not exist.")
        return redirect('/')
    
    user_posts = Post.objects.filter(user=id_user).order_by('-created_at')
    user_reels = Reel.objects.filter(user=id_user).order_by('-created_at')
    user_post_length = len(user_posts)
    user_reels_length = len(user_reels)
    follower = request.user.username
    user = id_user
    
    if Followers.objects.filter(follower=follower, user=user).first():
        follow_unfollow = 'Unfollow'
    else:
        follow_unfollow = 'Follow'
    
    user_followers = len(Followers.objects.filter(user=id_user))
    user_following = len(Followers.objects.filter(follower=id_user))
    
    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_reels': user_reels,
        'user_post_length': user_post_length,
        'user_reels_length': user_reels_length,
        'profile': profile,
        'follow_unfollow': follow_unfollow,
        'user_followers': user_followers,
        'user_following': user_following,
    }

    if request.user.username == id_user:
        if request.method == 'POST':
            if request.FILES.get('image') is None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            else:
                image = request.FILES.get('image')
                bio = request.POST['bio']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.bio = bio
                user_profile.location = location
                user_profile.save()
            return redirect('/profile/' + id_user)
        else:
            return render(request, 'profile.html', context)
    return render(request, 'profile.html', context)


@login_required(login_url='/loginn')
def delete(request, id):
    post = Post.objects.get(id=id)
    post.delete()
    return redirect('/profile/' + request.user.username)

@login_required(login_url='/loginn')
def delete_reel(request, id):
    reel = Reel.objects.get(id=id)
    reel.delete()
    return redirect('/profile/' + request.user.username)

@login_required(login_url='/loginn')
def search_results(request):
    query = request.GET.get('q')
    users = Profile.objects.filter(user__username__icontains=query)
    posts = Post.objects.filter(caption__icontains=query)
    reels = Reel.objects.filter(caption__icontains=query)
    context = {
        'query': query,
        'users': users,
        'posts': posts,
        'reels': reels,
    }
    return render(request, 'search_user.html', context)

def home_post(request, id):
    post = Post.objects.get(id=id)
    profile = Profile.objects.get(user=request.user)
    context = {
        'post': post,
        'profile': profile,
    }
    return render(request, 'main.html', context)

def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']
        if Followers.objects.filter(follower=follower, user=user).first():
            delete_follower = Followers.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = Followers.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')

@login_required(login_url='/loginn')
def add_comment(request, id):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                post_id=id,
                user=request.user.username,
                content=content
            )
            return redirect('/#' + str(id))
    return redirect('/')

@login_required(login_url='/loginn')
def delete_comment(request, id):
    comment = get_object_or_404(Comment, id=id)
    if comment.user == request.user.username:
        comment.delete()
        return redirect('/#' + str(comment.post.id))

@login_required(login_url='/loginn')
def upload_reel(request):
    if request.method == 'POST':
        user = request.user.username
        video = request.FILES.get('reel_video')
        caption = request.POST['caption']
        new_reel = Reel.objects.create(user=user, video=video, caption=caption)
        new_reel.save()
        return redirect('/reels')
    else:
        return redirect('/reels')

@login_required(login_url='/loginn')
def reels_view(request):
    try:
        profile = Profile.objects.get(user=request.user)
        all_reels = Reel.objects.all().order_by('-created_at')
        
        # Build a dictionary of likes for each reel by current user
        reel_likes = {}
        for reel in all_reels:
            reel_likes[reel.id] = LikeReel.objects.filter(reel_id=reel.id, username=request.user.username).exists()
        
        context = {
            'reels': all_reels,
            'profile': profile,
            'reel_likes': reel_likes,
        }
        return render(request, 'reels.html', context)
    except Exception as e:
        print(f"Error in reels view: {e}")
        return redirect('/loginn')

@login_required(login_url='/loginn')
def like_reel(request, id):
    if request.method == 'GET':
        username = request.user.username
        reel = get_object_or_404(Reel, id=id)
        like_filter = LikeReel.objects.filter(reel_id=id, username=username).first()
        
        if like_filter is None:
            new_like = LikeReel.objects.create(reel_id=id, username=username)
            reel.no_of_likes = reel.no_of_likes + 1
        else:
            like_filter.delete()
            reel.no_of_likes = reel.no_of_likes - 1
        
        reel.save()
        return redirect('/reels')
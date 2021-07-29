from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, FormView, ListView, TemplateView, UpdateView

from .forms import CommentForm, FeedbackForm, RegisterForm
from .models import Comment, Post

User = get_user_model()


class HomePageView(TemplateView):
    template_name = 'index.html'


class RegisterFormView(SuccessMessageMixin, FormView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('index')
    success_message = 'Profile created'

    def form_valid(self, form):
        form.save()

        username = self.request.POST['username']
        password = self.request.POST['password1']

        user = authenticate(username=username, password=password)
        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'email']
    template_name = 'registration/update_profile.html'
    success_url = reverse_lazy('index')
    success_message = 'Profile updated'

    def get_object(self, queryset=None):
        user = self.request.user
        return user


def feedback_form(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            subject = 'New feedback!'
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            send_mail(subject, message, from_email, ['admin@example.com'])
            return redirect('feedback')
    else:
        form = FeedbackForm()
    return render(request, 'feedback.html', context={'form': form})


class PostCreate(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'short_description', 'image', 'full_description', 'posted']
    template_name = 'post_create.html'
    success_url = reverse_lazy('post_list')

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        # if form.is_valid():
        #     subject = 'New post'
        #     message = 'New post created! Check it on admin panel.'
        #     from_email = 'ad@example.com'
        #     send_mail(subject, message, from_email, ['admin@example.com'])
        self.object = post
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(cache_page(10), name='dispatch')
class PostList(ListView):
    model = Post
    paginate_by = 10
    template_name = 'post_list.html'

    # queryset = Post.objects.all().filter(posted=True)
    # context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.all().filter(posted=True)


@cache_page(10)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, posted=True)
    comments = Comment.objects.all().filter(post=post).filter(moderated=True)
    # comments = post.comment_set.filter(moderated=True)
    paginator = Paginator(comments, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comm = Comment()
            comm.username = form.cleaned_data['username']
            comm.text = form.cleaned_data['text']
            comm.post = post
            comm.save()
            return HttpResponseRedirect(reverse('post_detail', args=(post.id,)))

    else:
        initial = {'username': request.user.username}
        form = CommentForm(initial=initial)

    context = {'form': form, 'post': post, 'page_obj': page_obj}

    return render(request, 'post_detail.html', context)


class PostUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Post
    template_name = 'post_update.html'
    fields = ['title', 'short_description', 'image', 'full_description', 'posted']
    success_url = reverse_lazy('post_list')
    success_message = 'Post updated'

    def get_success_url(self):
        post_id = self.kwargs['pk']
        return reverse_lazy('post_update', kwargs={'pk': post_id})


class PostDelete(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')
    template_name = 'post_delete.html'
    success_message = 'Post deleted'


@cache_page(10)
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk, is_staff=False)
    posts = Post.objects.filter(author=user).filter(posted=True)
    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'obj': user,
    }
    return render(request, 'user_detail.html', context)


@cache_page(10)
def users_posts(request):
    current_user = request.user

    posted_posts = Post.objects.filter(author=current_user).filter(posted=True)
    paginator = Paginator(posted_posts, 2)
    page_number = request.GET.get('page')
    page_obj_posted = paginator.get_page(page_number)

    unposted_posts = Post.objects.filter(author=current_user).filter(posted=False)
    paginator = Paginator(unposted_posts, 2)
    page_number = request.GET.get('page')
    page_obj_unposted = paginator.get_page(page_number)

    context = {
        'page_obj_posted': page_obj_posted,
        'page_obj_unposted': page_obj_unposted,
    }
    return render(request, 'users_posts.html', context)


@method_decorator(cache_page(10), name='dispatch')
class UserList(ListView):
    model = User
    template_name = 'user_list.html'
    paginate_by = 10
    queryset = User.objects.filter(is_staff=False)

    # def get_queryset(self):
    #     return User.objects.filter(is_staff=False)

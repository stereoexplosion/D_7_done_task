from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_protect
from django.db.models import Exists, OuterRef
from django.shortcuts import render
from .models import Post, Category, Subscription
from .filters import PostFilter
from .forms import PostSearchForm


class PostsList(ListView):
    model = Post
    ordering = '-post_create_time'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'post_search'
    queryset = Post.objects.all().values().order_by('-id')
    paginate_by = 10
    form_class = PostSearchForm

    # Переопределяем функцию получения списка товаров
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #Забираем отфильтрованные объекты
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) #вписываем фильтр в контекст
        context['categories'] = Post.objects.all()
        context['form'] = PostSearchForm()
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

class NewsCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    raise_exception = True
    permission_required = ('news.add_post',)
    form_class = PostSearchForm
    model = Post
    template_name = 'news_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_choice = 'NE'
        return super().form_valid(form)

class ArticleCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    raise_exception = True
    permission_required = ('news.add_post',)
    form_class = PostSearchForm
    model = Post
    template_name = 'article_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_choice = 'AR'
        return super().form_valid(form)

class NewsUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    raise_exception = True
    permission_required = ('news.change_post',)
    form_class = PostSearchForm
    model = Post
    template_name = 'news_edit.html'

class ArticlesUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    raise_exception = True
    permission_required = ('news.change_post',)
    form_class = PostSearchForm
    model = Post
    template_name = 'articles_edit.html'

class NewsDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    raise_exception = True
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'news_delete.html'
    success_url = reverse_lazy('posts_list')

class ArticlesDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    raise_exception = True
    permission_required = ('news.delete_post',)
    model = Post
    template_name = 'articles_delete.html'
    success_url = reverse_lazy('posts_list')

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('category_name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )
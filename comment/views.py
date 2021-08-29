from django.shortcuts import render, get_object_or_404
from stanfordcorenlp import StanfordCoreNLP
from .models import Post
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from nltk.tree import Tree
from django.http import HttpResponse

class PostListView(ListView):
    model = Post
    template_name = 'Comment/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

class UserPostListView(ListView):
    model = Post
    template_name = 'Comment/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post

class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content']
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']
    success_url = 'http://127.0.0.1:8000/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    user = Post.objects.filter(id='3').values_list('content', flat=True)
    data = user[0]
    testdata = [1, 2, 3, 4, 5, 5, 6]
    return render(request, 'Comment/about.html', {'posts': testdata})

def nlp(request, pk):
    content = Post.objects.filter(id=pk).values_list('content', flat=True)
    data = content[0]
    nlp = StanfordCoreNLP(r'D:\StanfordCoreNLP\stanford-corenlp-full-2018-10-05')
    sentence = data
    sen_tag = nlp.pos_tag(sentence)  # 词性标注

    noun = []
    preposition = []
    verb = []
    adjective = []
    conjunction = []
    cardinumber = []
    determiner = []
    adverb = []
    TO = []
    wh_determiner = []
    wh_pronoum = []
    wh_adverb = []
    personal = []

    for i in sen_tag:
        if i[1].startswith('CC'):
            conjunction.append(i[0])
        elif i[1].startswith('DT'):
            determiner.append(i[0])
        elif i[1].startswith('CD'):
            cardinumber.append(i[0])
        elif i[1].startswith('N'):
            noun.append(i[0])
        elif i[1] == 'IN':
            preposition.append(i[0])
        elif i[1].startswith('V'):
            verb.append(i[0])
        elif i[1].startswith('JJ'):
            adjective.append(i[0])
        elif i[1].startswith('RB'):
            adverb.append(i[0])
        elif i[1].startswith('to'):
            TO.append(i[0])
        elif i[1].startswith('WDT'):
            wh_determiner.append(i[0])
        elif i[1].startswith('WP'):
            wh_pronoum.append(i[0])
        elif i[1].startswith('WRB'):
            wh_adverb.append(i[0])
        elif i[1].startswith('PRP'):
            personal.append(i[0])


        nlp.close()

    return render(request, 'Comment/post_nlp.html', {'posts': data, 'noun': noun, 'verb': verb, 'preposition': preposition,
                                                     'adjective': adjective, 'conjunction': conjunction, 'cardinumber': cardinumber,
                                                     'determiner': determiner, 'adverb': adverb, 'TO': TO, 'wh_determiner': wh_determiner,
                                                     'wh_pronoum': wh_pronoum, 'wh_adverb': wh_adverb, 'tagged_posts': sen_tag, 'personal': personal})


def tree(request, pk):
    content = Post.objects.filter(id=pk).values_list('content', flat=True)
    data = content[0]
    nlp = StanfordCoreNLP(r'D:\StanfordCoreNLP\stanford-corenlp-full-2018-10-05')
    sentence = data
    tree = Tree.fromstring(nlp.parse(sentence))
    tree.draw()
    nlp.close()
    return render(request, 'Comment/post_nlpgraph.html')

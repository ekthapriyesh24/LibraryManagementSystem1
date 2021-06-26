from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from myapp.forms import RenewBookForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Book, Author, BookInstance, Genre
# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }
    return render(request, 'index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    paginate_by = 5

class BookDetailView(generic.DetailView):
    model = Book

class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'myapp.can_mark_returned'

class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre']
    permission_required = 'myapp.can_mark_returned'

class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'myapp.can_mark_returned'

class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 5

class AuthorDetailView(generic.DetailView):
    model = Author

class AuthorCreate(PermissionRequiredMixin,CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'myapp.can_mark_returned'

class AuthorUpdate(PermissionRequiredMixin,UpdateView):
    model = Author
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'myapp.can_mark_returned'

class AuthorDelete(PermissionRequiredMixin,DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'myapp.can_mark_returned'

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name ='myapp/bookinstance_list_borrowed_user.html'
    paginate_by = 5

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    permission_required = 'myapp.can_mark_returned'
    template_name = 'myapp/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

@login_required
@permission_required('myapp.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()
            return HttpResponseRedirect(reverse('all-borrowed') )
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})
    context = {
        'form': form,
        'book_instance': book_instance,
    }
    return render(request, 'myapp/book_renew_librarian.html', context)

class BookInstanceCreate(PermissionRequiredMixin,CreateView):
    model = BookInstance
    fields = ['book','imprint','due_back','borrower','status']
    permission_required = 'myapp.can_mark_returned'
    def get_success_url(self):
        return reverse('book-detail', kwargs={'pk': self.object.book.pk})

class BookInstanceUpdate(PermissionRequiredMixin,UpdateView):
    model = BookInstance
    fields = ['book','imprint','due_back','borrower','status']
    permission_required = 'myapp.can_mark_returned'
    def get_success_url(self):
        return reverse('book-instance-detail', kwargs={'pk': self.object.pk})

class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('book-instances')
    permission_required = 'myapp.can_mark_returned'
    # def get_success_url(self):
    #     return reverse('book-detail', kwargs={'pk': self.object.book.pk})

class BookInstanceListView(generic.ListView):
    model = BookInstance
    template_name = 'myapp/bookinstance_list.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.all()

class BookInstanceDetailView(generic.DetailView):
    model = BookInstance

class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'myapp.can_mark_returned'

class GenreCreate(PermissionRequiredMixin,CreateView):
    model = Genre
    fields = ['name']
    permission_required = 'myapp.can_mark_returned'

class GenreListView(generic.ListView):
    model = Genre
    paginate_by = 5

class GenreDetailView(generic.DetailView):
    model = Genre

class GenreUpdate(PermissionRequiredMixin,UpdateView):
    model = Genre
    fields = '__all__' # Not recommended (potential security issue if more fields added)
    permission_required = 'myapp.can_mark_returned'

class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'myapp.can_mark_returned'
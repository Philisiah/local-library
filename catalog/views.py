from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

#form imports
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import  HttpResponseRedirect
from django.urls import reverse
import datetime

# CRUD views imports
from django.views.generic.edit import CreateView, UpdateView,DeleteView
from django.urls import  reverse_lazy


from .models import Book, Author, BookInstance, Genre
from .forms import RenewBookForm

# Create your views here.

class BookListView(generic.ListView):

    model = Book
    paginate_by = 10


class BookDetailView(generic.DetailView):


    model = Book

class AuthorListView(generic.ListView):


    model = Author
    paginate_by = 10

class AuthorDetailView(generic.DetailView):


    model = Author

class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):


    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by =  10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_visits = request.session.get('num_visits',0)
    request.session['num_visits'] = num_visits+1

    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors,'num_visits': num_visits ,
                 'num_genres': num_genres},
    )

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    bookinst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        #create new form
        form = RenewBookForm(request.POST)
        #validate form data
        if form.is_valid():
            #runs form.cleaned data on post data
            bookinst.due_back = form.cleaned_data['renewal_date']
            bookinst.save()

            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})
    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst': bookinst})


#AUTHOR CRUD
class AuthorCreate(CreateView):
    model =  Author
    fields = '__all__'
    initial = {'date_of_death':'12/10/2017',}
    permission_required = 'catalog.can_mark_returned'

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    permission_required = 'catalog.can_mark_returned'

class AuthorDelete(DeleteView):
    model =  Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.can_mark_returned'

#BOOK CRUD

class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    initial = {'date_of_death': '12/10/2017', }
    permission_required = 'catalog.can_mark_returned'

class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    permission_required = 'catalog.can_mark_returned'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.can_mark_returned'
from django.template.defaultfilters import title

from .forms import *
from .models import *

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import Greatest
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.auth import login, views as auth_views
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages

from taggit.models import Tag

from datetime import timedelta


# from django.core.mail import send_mail

def home(request, tag_slug=None):
    books = Book.objects.all().order_by('-id')
    # show with tag
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        books = books.filter(tags__in=[tag])

    paginator = Paginator(books, 8)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)

    return render(request, 'pages/home.html', {'page': page_obj, 'tag': tag})


def book_detail(request, pk):
    book = get_object_or_404(Book, id=pk)
    # similar book
    ids = book.tags.values_list('id', flat=True)
    similar_books = Book.objects.filter(tags__in=ids).exclude(id=book.id)
    similar_books = similar_books.annotate(same_tags=Count('tags')).order_by('-same_tags', 'status')

    return render(request, 'pages/detail/book_detail.html', {'book': book, 'similar_books': similar_books})


class AuthorDetail(DetailView):
    model = Author
    context_object_name = 'author'
    template_name = 'pages/detail/author_detail.html'


class AuthorList(ListView):
    model = Author
    context_object_name = 'authors'
    paginate_by = 4
    template_name = 'pages/list/author_list.html'


class PublisherList(ListView):
    model = Publisher
    context_object_name = 'publishers'
    paginate_by = 6
    template_name = 'pages/list/publisher_list.html'


class PublisherDetail(DetailView):
    model = Publisher
    context_object_name = 'publisher'
    template_name = 'pages/detail/publisher_detail.html'


class CategoryList(ListView):
    model = Category
    context_object_name = 'categories'
    paginate_by = 8
    template_name = 'pages/list/Category_list.html'


class CategoryDetail(DetailView):
    model = Category
    context_object_name = 'category'
    template_name = 'pages/detail/Category_detail.html'


@login_required(login_url='login_required')
@permission_required('library.add_book', login_url='403')
def add_book(request):
    authors = Author.objects.all()
    publishers = Publisher.objects.all()
    categories = Category.objects.all()
    if request.method == "POST":
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.title = form.clean_title()
            form.author = form.clean_author()
            form.publisher = form.cleaned_data.get('publisher')
            form.category = form.cleaned_data.get('category')
            form.isbn = form.clean_isbn()
            form.publication_year = form.clean_publication_year()
            form.total_copies = form.clean_total_copies()
            form.available_copies = form.clean_available_copies()
            form.status = form.cleaned_data.get('status')
            form.cover_image = form.clean_cover_image()
            form.description = form.cleaned_data.get('description')
            form.pages = form.clean_pages()
            form.save()
            book = Book.objects.get(isbn=form.isbn)
            tags = [tag.strip() for tag in request.POST.get('tags').split(',') if tag.strip()]
            for tag in tags:
                book.tags.add(tag)
                book.save()
            return redirect('home')
    else:
        form = BookForm()

    content = {"form": form,
               "authors": authors,
               "publishers": publishers,
               "categories": categories,
               "tag": request.POST.get('tags'),
               }
    return render(request, 'forms/add-book-form.html', content)


@login_required(login_url='login_required')
def borrow_book(request, book_id):
    member = request.user.member_profile
    book = Book.objects.get(id=book_id)
    if book.status == 'lost':
        return redirect('book_detail', book_id)
    due_date = timezone.now().date() + timedelta(days=21)

    if Borrow.objects.filter(member=member, book=book, status='borrowed').exists():
        return redirect('book_detail', book_id)

    if book.available_copies <= 0:
        return redirect('book_detail', book_id)

    try:
        Borrow.objects.create(member=member, book=book, due_date=due_date)
        message = "The book successfully borrowed"
    except ValueError as e:
        message = str(e)

    return render(request, 'pages/borrow_result.html', {'messages': message})


@login_required(login_url='login_required')
def reserve_book(request, book_id):
    member = request.user.member_profile
    book = get_object_or_404(Book, id=book_id)
    if book.status == 'lost' or book.available_copies >= 1:
        return redirect('book_detail', book_id)

    reserve_at = timezone.now()

    try:
        Reservation.objects.create(member=member, book=book, reserved_at=reserve_at)
        messages = "The book successfully reserved"
    except ValueError as e:
        messages = str(e)

    return render(request, 'pages/borrow_result.html', {'messages': messages})


@login_required(login_url='login_required')
def member_history(request):
    member = request.user.member_profile
    borrows = member.borrowed_books.all()
    reservations = member.reservations.all()
    paginator_b = Paginator(borrows, 4)
    paginator_r = Paginator(reservations, 4)
    page_b = request.GET.get('borrow_page')
    page_r = request.GET.get('reservation_page')
    page_obj_b = paginator_b.get_page(page_b)
    page_obj_r = paginator_r.get_page(page_r)
    return render(request, "pages/member_history.html", {'borrows': page_obj_b, 'reservations': page_obj_r})


def contact(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = EmailForm(request.POST)
            if form.is_valid():
                form = form.cleaned_data
                name = form['name']
                subject = form['subject']
                message = form['message']
                email = form['email']
                # from_email = settings.DEFAULT_FROM_EMAIL
                # recipient_list = settings.DEFAULT_FROM_EMAIL
                msg = f"\n\n=-----------------------------=\n\nmember name: {name}\nemail: {email}\nsubject: {subject}\nmessage: \n'{message}'\n{timezone.now()}\n"

                try:
                    # send_mail(subject=subject, message=msg, from_email=from_email, recipient_list=recipient_list,
                    #           fail_silently=False)

                    txt_file = os.path.join(settings.BASE_DIR, 'contact.txt')
                    with open(txt_file, 'a') as f:
                        f.write(msg)

                    return JsonResponse({
                        "success": True,
                        "message": "Message sent successfully",
                    })
                except Exception as e:
                    return JsonResponse({
                        "success": False,
                        "message": "Message not sent successfully",
                        "error": str(e)
                    }, status=500)
            else:
                return JsonResponse({
                    "success": False,
                    "message": "Invalid form data",
                    "errors": form.errors
                }, status=400)

        return JsonResponse({
            "success": False,
            "message": "Request is invalid",
        }, status=405)
    return JsonResponse({
        "success": False,
        "message": "most login",
    }, status=405)


def search(request, tag_slug=None):
    if request.method == "GET":
        query_name = request.GET.get('search-query', '').strip()
        if query_name:
            request.session["search_query"] = query_name
        else:
            try:
                query_name = request.session["search_query"]
            except:
                query_name = ""

        books = Book.objects.annotate(similarity=Greatest(
            TrigramSimilarity('description', query_name),
            TrigramSimilarity('title', query_name),
            TrigramSimilarity('author__first_name', query_name),
            TrigramSimilarity('author__last_name', query_name),
            TrigramSimilarity('category__name', query_name),
            TrigramSimilarity('publisher__name', query_name),
            TrigramSimilarity('isbn', query_name),
            # TrigramSimilarity('tags', query_name),
        )).filter(similarity__gte=0.15)

        tag = None
        if tag_slug:
            try:
                tag = Tag.objects.get(slug=tag_slug)
                books = books.filter(tags__in=[tag])
            except Tag.DoesNotExist:
                books = Book.objects.none()

        books = books.distinct().order_by('-similarity')

        paginator = Paginator(books, 8)
        page = request.GET.get('page')
        page_obj = paginator.get_page(page)

        return render(request, 'pages/home.html', {'page': page_obj, 'tag': tag})


@login_required(login_url='login_required')
def member_profile(request):
    member = Member.objects.get(user=request.user)
    return render(request, 'pages/detail/member_profile.html', {'member': member})


class CustomLoginView(UserPassesTestMixin, auth_views.LoginView):
    form_class = LoginForm
    template_name = 'auth/login.html'

    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(1209600)

        return super().form_valid(form)

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('logout_required')


def logout_required(user):
    return not user.is_authenticated


@user_passes_test(logout_required, login_url='logout_required')
def member_register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"{username} you sing up")

            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Fix errors')
    else:
        form = MemberRegistrationForm()

    return render(request, 'auth/register.html', {'form': form})


@login_required(login_url='login_required')
class CustomChangePasswordView(auth_views.PasswordChangeView):
    form_class = CustomChangePasswordForm
    success_url = reverse_lazy('profile')
    template_name = 'auth/change_password.html'


class CustomResetPasswordView(UserPassesTestMixin, auth_views.PasswordResetView):
    template_name = 'auth/reset_password/password_reset.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'auth/reset_password/password_reset_email.html'

    # success_url = reverse_lazy('password_reset_confirm')

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('logout_required')


class CustomPasswordResetDoneView(UserPassesTestMixin, auth_views.PasswordResetDoneView):
    template_name = 'auth/reset_password/password_reset_done.html'

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('logout_required')


class CustomPasswordResetConfirmView(UserPassesTestMixin, auth_views.PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = 'auth/reset_password/Password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def test_func(self):
        return not self.request.user.is_authenticated

    def handle_no_permission(self):
        return redirect('logout_required')


# ------------------------#  views for DRF  #------------------------#


from .serializers import *
from .permissions import *

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response


class APIAutorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrRead]


class APIPublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrRead]


class APICategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrRead]


class APIBookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all().select_related("publisher", "category").prefetch_related("author", "tags")
    serializer_class = BookSerializer

    @action(detail=True)
    @permission_classes([permissions.IsAuthenticated])
    def borrow(self, request, pk=None):
        book = self.get_object()
        member = request.user.member_profile

        if book.status == "lost":
            return Response({
                'status': "fail",
                'message': "This book is unavailable."
            }, status=status.HTTP_400_BAD_REQUEST)

        if book.available_copies >= 1:
            due_date = timezone.now().date() + timedelta(days=21)

            if Borrow.objects.filter(member=member, book=book, status='borrowed').exists():
                return Response({
                    'status': "fail",
                    "message": "You're already borrowed this book."
                })

            active_borrows = Borrow.objects.filter(member=member, status="borrowed").count()
            if active_borrows >= member.max_books_allowed():
                return Response({
                    "status": "fail",
                    "message": f"You can not borrow more than {member.max_books_allowed()} book."
                }, status=status.HTTP_426_UPGRADE_REQUIRED)

            try:
                Borrow.objects.create(member=member, book=book, due_date=due_date)
                message = f"The {book.title} book successfully borrowed."
                return Response({
                    "status": "success",
                    "message": message
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                message = str(e)
                return Response({
                    "status": "fail",
                    "message": message
                })
        else:
            if Reservation.objects.filter(member=member, book=book, status='active').exists():
                return Response({
                    'status': "fail",
                    "message": "You're already reserved this book."
                })

            active_borrows = Reservation.objects.filter(member=member, status="active").count()
            if active_borrows >= member.max_books_allowed():
                return Response({
                    "status": "fail",
                    "message": f"You can not reserve more than {member.max_books_allowed()} book."
                }, status=status.HTTP_426_UPGRADE_REQUIRED)

            try:
                Reservation.objects.create(member=member, book=book)
                message = f"The {book.title} book is unavailable.\nYou successfully reserve it."
                return Response({
                    "status": "success",
                    "message": message
                }, status=status.HTTP_200_OK)
            except ValueError as e:
                message = str(e)
                return Response({
                    "status": "fail",
                    "message": message
                })


class APIBorrowHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BorrowListSerializer

    def get_queryset(self):
        return Borrow.objects.filter(member=self.request.user.member_profile)


class APIReserveHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BorrowListSerializer

    def get_queryset(self):
        return Borrow.objects.filter(member=self.request.user.member_profile)



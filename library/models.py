from django.utils import timezone
from django.contrib.auth.models import User
from django.db import models, transaction
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
import uuid
import os
import datetime
from taggit.managers import TaggableManager


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="authors_profile/", blank=True, null=True)

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo_image = models.ImageField(upload_to="publisher_logo/", blank=True, null=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    logo_image = models.ImageField(upload_to="category_logo/", blank=True, null=True)

    def __str__(self):
        return self.name


def generate_unique_membership_number():
    while True:
        code = uuid.uuid4().hex[:10].upper()
        if not Member.objects.filter(membership_number=code).exists():
            return code


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    membership_number = models.CharField(max_length=20, unique=True, blank=True,
                                         default=generate_unique_membership_number)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    membership_date = models.DateField(auto_now_add=True)
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('guest', 'Guest'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_image = models.ImageField(upload_to="member_profile/", blank=True, null=True)

    def max_books_allowed(self):
        if self.role == 'teacher':
            return 10
        elif self.role == 'student':
            return 5
        else:
            return 2

    def __str__(self):
        return f"{self.user.username} - {self.membership_number}"


class Book(models.Model):
    STATUS_CHOICES = (
        ("available", "Available"),
        ("borrowed", "Borrowed"),
        ("reserved", "Reserved"),
        ("lost", "Lost"),
    )
    title = models.CharField(max_length=200)
    author = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    isbn = models.CharField(max_length=20, unique=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    pages = models.PositiveIntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tags = TaggableManager()

    def __str__(self):
        return self.title

    class Meta:
        permissions = [
            ('can_add_book', 'Can Add a book(adder)'),
        ]


class Borrow(models.Model):
    STATUS_CHOICES = (
        ("borrowed", "Borrowed"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrows")
    borrow_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="borrowed")

    def is_overdue(self):
        if self.status == "borrowed" and timezone.now().date() > self.due_date:
            return True
        return False

    def save(self, *args, **kwargs):

        # 🔒 برای جلوگیری از race condition
        with transaction.atomic():

            # ---------------- BORROW ----------------
            if not self.pk:
                active_borrows = Borrow.objects.filter(
                    member=self.member,
                    status="borrowed"
                ).count()

                if active_borrows >= self.member.max_books_allowed():
                    raise ValueError(
                        f"You are not allowed to borrow more than {self.member.max_books_allowed()} books"
                    )

                # قفل روی کتاب (جلوگیری از همزمانی)
                book = Book.objects.select_for_update().get(pk=self.book.pk)

                if book.available_copies > 0:
                    book.available_copies -= 1
                    book.save()
                else:
                    raise ValueError("Books isn't available, you should reserve")

            # ---------------- RETURN DETECTION ----------------
            is_returned_now = False
            if self.pk:
                old = Borrow.objects.get(pk=self.pk)
                if old.status != "returned" and self.status == "returned":
                    is_returned_now = True

            super().save(*args, **kwargs)

            # ---------------- AFTER RETURN ----------------
            if is_returned_now:
                book = Book.objects.select_for_update().get(pk=self.book.pk)
                book.available_copies += 1
                book.save()

                first_reservation = book.reservations.filter(
                    status="active"
                ).order_by("reserved_at").first()

                if first_reservation:
                    first_reservation.status = "fulfilled"
                    first_reservation.save()

    def mark_returned(self):
        if self.status == "returned":
            return

        self.status = "returned"
        self.return_date = timezone.now().date()

        self.save()

        first_reservation = self.book.reservations.filter(
            status="active"
        ).order_by("reserved_at").first()

        if first_reservation:
            first_reservation.fulfill()

    def __str__(self):
        return f"{self.book.title} borrowed by {self.member.user.username}"


class Reservation(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="reservations")
    reserved_at = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(("active", "Active"),
                                                      ("fulfilled", "Fulfilled"),
                                                      ("cancelled", "Cancelled")),
                              default="active")

    def email_sender(self):
        subject = "Your book is ready to be received"
        message = (
            f'Hi {self.member.user.username}\n\nThe {self.book.title} book you reserved is now available at the library.'
            f'\n{datetime.datetime.now()}')
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.member.user.email]
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
                  fail_silently=False)

        txt_file = os.path.join(settings.BASE_DIR, 'logs', 'reservation_notifications.txt')
        with open(txt_file, 'a') as f:
            f.write(f"\n=-----------------------------=\nsubject : Your book is ready to be received\nusername : {self.member.user.username}\nbook : {self.book.title}\nemail : {self.member.user.email}\nmessage : \n {message}\n")

    def save(self, *args, **kwargs):
        is_new_fulfilled = False

        if self.pk:
            old = Reservation.objects.get(pk=self.pk)
            if old.status != "fulfilled" and self.status == "fulfilled":
                is_new_fulfilled = True

        super().save(*args, **kwargs)

        if is_new_fulfilled:
            self.email_sender()

    def fulfill(self):
        self.status = "fulfilled"
        self.save()
        self.email_sender()

    def __str__(self):
        return f"{self.member} - {self.book}"

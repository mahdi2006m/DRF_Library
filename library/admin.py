from django.contrib import admin
from .models import (
    Book, Author, Category, Publisher,
    Member, Borrow, Reservation
)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Base Information', {
            'fields': [
                'title', 'isbn', 'publication_year', 'pages', 'tags'
            ],
        }),
        ('Writer Information', {
            'fields': [
                'author', 'publisher', 'category'
            ],
        }),
        ('Copies Information', {
            'fields': [
                'total_copies', 'available_copies', 'status'
            ],
        }),
        ('Other Information', {
            'fields': [
                'cover_image', 'description'
            ],
        }),
    ]
    list_display = (
        'id',
        'title',
        'publisher',
        'category',
        'total_copies',
        'available_copies',
        'status',
    )
    list_filter = ('category', 'publisher', 'status', 'publication_year')
    search_fields = ('title', 'isbn')
    filter_horizontal = ('author',)
    list_editable = ('status', 'available_copies', 'total_copies')
    list_display_links = ('id', 'title')


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Information', {
            'fields': [
                'first_name', 'last_name',
            ],
        }),
        ('Other Information', {
            'fields': [
                'bio', 'profile_image',
            ],
        }),
    ]
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {
            'fields': [
                'name', 
            ],
        }),
        ('Website', {
            'fields': [
                'website',
            ],
        }),
        ('Address', {
            'fields':[
                'address',
            ]
        }),
        ('Logo', {
            'fields':[
                'logo_image',
            ]
        })
    ]
    list_display = ('name', 'website')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Name', {
            'fields': [
                'name', 'slug',
            ],
        }),
        ('Description', {
            'fields': [
                'description',
            ]
        }),
        ('Logo', {
            'fields': [
                'logo_image',
            ]
        })
    ]
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    readonly_fields = ('get_username', 'get_email', 'membership_date', 'membership_number', 'get_fullname')

    fieldsets = [
        ('User Information', {
            'fields': [
                'user', 'get_fullname','get_username','get_email',
            ],
        }),
        ('Member Information', {
            'fields': [
                'phone', 'membership_number', 'role', 'membership_date', 'address',
            ]
        }),
        ('Profile Image', {
            'fields': [
                'profile_image',
            ]
        })
    ]
    list_display = (
        'user',
        'membership_number',
        'role',
        'membership_date',
    )
    search_fields = (
        'user__username',
        'membership_number',
    )
    list_filter = ('role',)
    list_editable = ('role',)

    def get_username(self, obj):
        if obj.user:
            return obj.user.get_username()
        return "-"
    get_username.short_description = 'Username'

    def get_fullname(self, obj):
        if obj.user:
            return obj.user.get_full_name()
        return "-"
    get_fullname.short_description = 'Fullname'

    def get_email(self, obj):
        if obj.user:
            return obj.user.email
        return '-'
    get_email.short_description = 'Email'



@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    readonly_fields = ('borrow_date', 'member', 'book')
    fieldsets = [
        ('Borrowed', {
            'fields': [
                'member', 'book',
            ],
        }),
        ('Date', {
            'fields': [
                'borrow_date', 'due_date', 'return_date', 'status',
            ],
        })
    ]
    list_display = (
        'member',
        'book',
        'borrow_date',
        'due_date',
        'return_date',
        'status',
    )
    list_filter = ('status', 'member')
    search_fields = (
        'member__user__username',
        'book__title',
    )
    list_editable = ('status', 'return_date')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    readonly_fields = ('reserved_at', 'member', 'book')
    fieldsets = [
        ('Reserver', {
            'fields': [
                'member', 'book',
            ],
        }),
        ('Date', {
            'fields': [
                'reserved_at', 'status',
            ],
        })
    ]
    list_display = (
        'member',
        'book',
        'reserved_at',
        'status',
    )
    list_filter = ('status',)
    search_fields = (
        'member__user__username',
        'book__title',
    )
    list_editable = ('status',)

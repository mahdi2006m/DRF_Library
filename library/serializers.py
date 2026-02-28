from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import serializers


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Author
        fields = ['url', 'first_name', 'last_name', 'bio', 'profile_image']


class PublisherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publisher
        fields = ['url', 'name', 'address', 'website', 'logo_image']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['url', 'name', 'slug', 'description', 'logo_image']


class AuthorSerializerForBook(serializers.HyperlinkedModelSerializer):
    fullname = serializers.CharField(source="__str__")

    class Meta:
        model = Author
        fields = ['url', 'fullname']


class PublisherSerializerForBook(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publisher
        fields = ['url', 'name']


class CategorySerializerForBook(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ['url', 'name']


class BookSerializer(serializers.HyperlinkedModelSerializer):
    author = AuthorSerializerForBook(read_only=True, many=True)
    publisher = PublisherSerializerForBook(read_only=True)
    category = CategorySerializerForBook(read_only=True)
    tags = serializers.SerializerMethodField()
    borrow_url = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["url",
                  "author",
                  "publisher",
                  "category",
                  "title",
                  "isbn",
                  "publication_year",
                  "total_copies",
                  "available_copies",
                  "status",
                  "pages",
                  "tags",
                  "description",
                  "cover_image",
                  "borrow_url",
                  ]

    def get_tags(self, obj):
        if hasattr(obj, '_prefetched_objects_cache') and 'tags' in obj._prefetched_objects_cache:
            return [tag.name for tag in obj.tags.all()]
        return [tag.name for tag in obj.tags.all()]

    def get_borrow_url(self, obj):
        request = self.context.get("request")
        if request is None:
            return None

        relative_url = reverse("book-borrow", kwargs={'pk': obj.pk})

        return request.build_absolute_uri(relative_url)


class BookSerializerForBorrow(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ['url', 'title', "isbn"]


class BorrowListSerializer(serializers.HyperlinkedModelSerializer):
    book = BookSerializerForBorrow(read_only=True)

    class Meta:
        model = Borrow
        fields = [
            'url',
            "book",
            "status",
            "borrow_date",
            "due_date",
            "return_date",
        ]


class ReserveListSerializer(serializers.HyperlinkedModelSerializer):
    book = BookSerializerForBorrow(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'url',
            "book",
            "status",
            "reserved_at"
        ]

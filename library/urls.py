from django.urls import path , include
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views


from rest_framework import routers


router = routers.DefaultRouter()
router.register(r"authors", views.APIAutorViewSet)
router.register(r"categories", views.APICategoryViewSet)
router.register(r"publishers", views.APIPublisherViewSet)
router.register(r"books", views.APIBookViewSet)
router.register(r"borrows_history", views.APIBorrowHistoryViewSet, basename="borrow")
router.register(r"reserv_history", views.APIReserveHistoryViewSet, basename="reserve")



urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include("rest_framework.urls", namespace='rest_framework')),
    path('test/', views.test_list, name='test_list'),
    path('', views.home, name='home'),
    path('filter/<slug:tag_slug>/', views.home, name='filter_tag'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('authors/', views.AuthorList.as_view(), name='author_list'),
    path('authors/<int:pk>/', views.AuthorDetail.as_view(), name='author_detail'),
    path('publishers/', views.PublisherList.as_view(), name='publisher_list'),
    path('publishers/<int:pk>/', views.PublisherDetail.as_view(), name='publisher_detail'),
    path('categories/', views.CategoryList.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views.CategoryDetail.as_view(), name='category_detail'),
    path('books/addbook', views.add_book, name='add_book'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('reserve/<int:book_id>/', views.reserve_book, name='reserve_book'),
    path('history/', views.member_history, name='member_history'),
    path('privacy/', TemplateView.as_view(template_name="pages/privacy_policy.html"), name='privacy'),
    path('terms/', TemplateView.as_view(template_name="pages/terms_of_service.html"), name='terms'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset_password/', views.CustomResetPasswordView.as_view(), name='password_reset'),
    path('reset_password/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset_password/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('change-password/', views.CustomChangePasswordView, name='change_password'),
    path('register/', views.member_register, name='register'),
    path('profile/', views.member_profile, name='profile'),
    path('login_required/', TemplateView.as_view(template_name='auth/message_most_logged_in.html'), name='login_required'),
    path('logout_required/', TemplateView.as_view(template_name='auth/message_most_logged_out.html'), name='logout_required'),
    path('access_denied/', TemplateView.as_view(template_name='403.html'), name='403'),
    path('not_found/', TemplateView.as_view(template_name='404.html'), name='404'),

]

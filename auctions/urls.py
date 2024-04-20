from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("category/", views.categories, name="categories"),
    path("category/<str:category>/", views.category, name="category"),
    path("create_listing/", views.create_listing, name="create_listing"),
    path("your_listings/", views.your_listings, name="your_listings"),
    path("won_listings/", views.won_listings, name="won_listings"),
    path("watch_list/", views.watch_list, name="watch_list"),
    path("listing/<int:listing_id>/", views.view_listing, name="listing"),
    path("listing/<int:listing_id>/watch/", views.watch, name="watch"),
    path("listing/<int:listing_id>/close/", views.close_auction, name="close_auction"),
    path("listing/<int:listing_id>/bid/", views.bid, name="bid"),
    path("listing/<int:listing_id>/comment/", views.comment, name="comment"),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('otp-success/', views.otp_success, name='otp_success'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password-otp/', views.password_otp, name='password_otp'),
    path('profile/', views.view_profile, name='view_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/edit/password/', views.edit_password, name='edit_password'),
]

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listings, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("display_listing", views.display_category, name="display_listing"),
    path("comment", views.comment, name="comment"),
    path("end_watchlist", views.end_watchlist, name="end_watchlist"),
    path("add_watchlist", views.add_watchlist, name="add_watchlist"),
    path("place_bid", views.place_bid, name="place_bid"),
    path("end_listing", views.end_listing, name="end_listing"),
    path("recycle_deposit", views.trash, name="recycle_deposit"),
    path("auctions_won", views.auctions_won, name="auctions_won"),
    path("profile", views.profile, name="profile"),
    path("search_item", views.search_item, name="search_item"),
    path("markers_info", views.markers_info, name="markers_info"),
    path("end_trash", views.end_trash, name="end_trash"),
]

from django.urls import path

from . import views

urlpatterns = [
    path("session/", views.SessionView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("logout/", views.LogoutView.as_view()),
    path("password/", views.PasswordView.as_view()),
    path("questions/", views.QuestionListView.as_view()),
    path("attempts/", views.SubmissionView.as_view()),
    path("overview/", views.OverviewView.as_view()),
    path("topics/", views.TopicListView.as_view()),
    path("documents/", views.DocumentListView.as_view()),
    path("profile/", views.ProfileView.as_view()),
]

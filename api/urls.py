from django.urls import path, include
from .views import JobList, JobListAll, JobView, CommentView, JobRetrive, AdminControl

urlpatterns = [
    path("jobs/", JobListAll.as_view(), name="job_list_all"),
    path("jobs/<int:pk>/", JobList.as_view(), name="job_list"),
    path("detailed_jobs/", JobView.as_view(), name="job_list_all"),
    path("comments/", CommentView.as_view(), name="comment_list"),
    path("get_job/", JobRetrive.as_view(), name="job_retrive"),
    path("admin_control/<str:password>/", AdminControl.as_view(), name="admin_control"),
]

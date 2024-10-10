from django.urls import path
from .views import JobView, CommentView, JobRetrieve, AdminControl, GetJob, GetAllJobs


urlpatterns = [
    # Get detailed list of all jobs
    path("jobs/", JobView.as_view(), name="job_list"),

    # Post a comment to a specific job
    path("jobs/comments/", CommentView.as_view(), name="job_comment"),

    # Retrieve details of a specific job
    path("jobs/detail/", JobRetrieve.as_view(), name="job_detail"),

    # Admin control panel with password authentication
    path("admin/control/<str:password>/", AdminControl.as_view(), name="admin_control"),

    # Get job details as an HTML page (e.g., for front-end display)
    path("jobs/page/", GetJob.as_view(), name="job_page"),

    # Get HTML page with a list of all jobs
    path("jobs/all/", GetAllJobs.as_view(), name="job_list_page"),
]


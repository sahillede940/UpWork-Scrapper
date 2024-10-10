from django.urls import path, include
from .views import JobList, JobListAll, JobView, CommentView, JobRetrieve, AdminControl, LLMView, get_all_jobs

urlpatterns = [
    path("jobs/", JobListAll.as_view(), name="job_list_all"),
    path("jobs/<int:pk>/", JobList.as_view(), name="job_list"),
    path("detailed_jobs/", JobView.as_view(), name="job_list_all"),
    path("comments/", CommentView.as_view(), name="comment_list"),
    path("get_job/", JobRetrieve.as_view(), name="job_retrive"),
    path("admin_control/<str:password>/", AdminControl.as_view(), name="admin_control"),
    path("llm/", LLMView.as_view, name="llm"),
    # returns html page with all jobs. used django's render function. so correctly write the path
    path("all_jobs/", get_all_jobs, name="job_list_page"),
]

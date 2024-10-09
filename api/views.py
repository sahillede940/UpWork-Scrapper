from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from .models import Job_List, Job, Comment
from .serializer import JobListSerializer, JobSerializer, CommentSerializer


class JobList(APIView):

    permission_classes = []

    def get(self, request, pk=None):
        try:
            if not pk:
                return Response(
                    {"message": "Job ID is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            job = get_object_or_404(Job_List.objects.all(), pk=pk)
            serializer = JobListSerializer(job)
            return Response(
                {
                    "job": serializer.data,
                    "message": "Job retrieved successfully",
                    "success": True,
                }
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            job = request.data.get("job")
            if not job:
                return Response(
                    {"message": "Job data is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = JobListSerializer(data=job)
            if serializer.is_valid():
                job_saved = serializer.save()
                return Response(
                    {
                        "message": f"Job '{job_saved.title}' created successfully",
                        "success": True,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "message": "Job data is invalid",
                        "errors": serializer.errors,
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk):
        try:
            saved_job = get_object_or_404(Job_List.objects.all(), pk=pk)
            data = request.data.get("job")
            if not data:
                return Response(
                    {"message": "Job data is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = JobListSerializer(instance=saved_job, data=data, partial=True)
            if serializer.is_valid():
                job_saved = serializer.save()
                return Response(
                    {
                        "message": f"Job '{job_saved.title}' updated successfully",
                        "success": True,
                    }
                )
            else:
                return Response(
                    {
                        "message": "Job data is invalid",
                        "errors": serializer.errors,
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            job = get_object_or_404(Job_List.objects.all(), pk=pk)
            job.delete()
            return Response(
                {"message": f"Job with id `{pk}` has been deleted.", "success": True},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobListAll(APIView):

    permission_classes = []

    def get(self, request):
        try:
            jobs = Job_List.objects.all()
            serializer = JobListSerializer(jobs, many=True)
            return Response(
                {
                    "jobs": serializer.data,
                    "message": "Jobs retrieved successfully",
                    "success": True,
                }
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            jobs = request.data.get("jobs")
            if not jobs:
                return Response(
                    {"message": "Jobs data is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            for job_data in jobs:
                job_id = job_data.get("job_id")
                if not job_id:
                    continue  # Skip if job_id is missing

                existing_job = Job_List.objects.filter(job_id=job_id).first()
                if existing_job:
                    continue  # Skip if job already exists

                serializer = JobListSerializer(data=job_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    continue  # Skip if data is invalid

            return Response(
                {"message": "Jobs created successfully", "success": True},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        try:
            jobs = Job_List.objects.all()
            jobs.delete()
            return Response(
                {"message": "All Jobs have been deleted.", "success": True},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobView(APIView):

    permission_classes = []

    def get(self, request):
        try:
            jobs = Job.objects.all()
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(jobs, request)
            serializer = JobSerializer(result_page, many=True)
            return Response(
                {
                    "jobs": serializer.data,
                    "message": "Jobs retrieved successfully",
                    "success": True,
                    "count": paginator.page.paginator.count,
                    "num_pages": paginator.page.paginator.num_pages,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            job_data = request.data.get("job")
            if not job_data:
                return Response(
                    {"message": "Job data is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            job_id = job_data.get("job_id")
            if not job_id:
                return Response(
                    {"message": "Job ID is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            existing_job = Job.objects.filter(job_id=job_id).first()
            if existing_job:
                return Response(
                    {"message": "Job already exists", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = JobSerializer(data=job_data)
            if serializer.is_valid():
                job_saved = serializer.save()
                return Response(
                    {
                        "message": f"Job '{job_saved.title}' created successfully",
                        "success": True,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "message": "Job data is invalid",
                        "errors": serializer.errors,
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {
                    "message": f"An error occurred while creating the job: {str(e)}",
                    "success": False,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        try:
            jobs = Job.objects.all()
            jobs.delete()
            return Response(
                {"message": "All Jobs have been deleted.", "success": True},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CommentView(APIView):

    permission_classes = []

    def get(self, request):
        try:
            comments = Comment.objects.all()
            paginator = PageNumberPagination()
            result_page = paginator.paginate_queryset(comments, request)
            serializer = CommentSerializer(result_page, many=True)
            return Response(
                {
                    "comments": serializer.data,
                    "message": "Comments retrieved successfully",
                    "success": True,
                    "count": paginator.page.paginator.count,
                    "num_pages": paginator.page.paginator.num_pages,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            comments = request.data.get("comments")
            job_id = request.data.get("job_id")
            if not comments or not job_id:
                return Response(
                    {"message": "Comments and job_id are required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            job = get_object_or_404(Job, job_id=job_id)

            for comment_data in comments:
                comment_data["job"] = job.id
                print(comment_data['rating'])
                serializer = CommentSerializer(data=comment_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    continue  # Skip invalid comments

            return Response(
                {
                    "message": f"Comments added successfully, Job: {job_id}",
                    "success": True,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request):
        try:
            comments = Comment.objects.all()
            comments.delete()
            return Response(
                {"message": "All Comments have been deleted.", "success": True},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JobRetrive(APIView):

    permission_classes = []

    def get(self, request):
        try:
            job_id = request.query_params.get("job_id")
            id = request.query_params.get("id")
            if job_id:
                job = get_object_or_404(Job.objects.all(), job_id=job_id)
            elif id:
                job = get_object_or_404(Job.objects.all(), id=id)
            else:
                return Response(
                    {"message": "Job ID or PK is required", "success": False},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            comments = Comment.objects.filter(job=job)
            comment_serializer = CommentSerializer(comments, many=True)
            job_serializer = JobSerializer(job)
            return Response(
                {
                    "job": job_serializer.data,
                    "comments": comment_serializer.data,
                    "message": "Job and comments retrieved successfully",
                    "success": True,
                }
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminControl(APIView):

    permission_classes = []

    def delete(self, request, password):
        try:
            if password != "admin@123123":
                return Response(
                    {
                        "message": "You are not authorized to perform this action.",
                        "success": False,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            job_list = Job_List.objects.all()
            job = Job.objects.all()
            comments = Comment.objects.all()
            job_list.delete()
            job.delete()
            comments.delete()
            return Response(
                {"message": "All data has been deleted.", "success": True},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

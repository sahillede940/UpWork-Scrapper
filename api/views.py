from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
import logging
from .models import Job_List, Job, Comment, LLMResponse
from .serializer import (
    JobListSerializer,
    JobSerializer,
    CommentSerializer,
    LLMResponseSerializer,
)
from .utils.LLM import LLM
from django.shortcuts import render

# Initialize logger
logger = logging.getLogger(__name__)


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
                print(comment_data["rating"])
                serializer = CommentSerializer(data=comment_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    continue  # Skip invalid comments

            try:
                data = LLM(job_id=job_id)
                if data.get("success"):
                    filtered_llm_data = {
                        key: value
                        for key, value in data.items()
                        if key
                        not in [
                            "client_names",
                            "keywords",
                            "company",
                            "client_location",
                            "success",
                        ]
                    }
                    llm_resp = LLMResponse.objects.create(
                        job=job,
                        client_names=data.get("client_names"),
                        keywords=data.get("keywords"),
                        company=data.get("company"),
                        client_location=data.get("client_location"),
                        other_data=filtered_llm_data,
                    )

                    # save llm response
                    llm_resp.save()

            except Exception as e:
                pass

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


class JobRetrieve(APIView):
    permission_classes = []

    def get(self, request):
        try:
            job_id = request.query_params.get("job_id")
            pk = request.query_params.get("id")
            # its a boolean value
            refresh_llm = request.query_params.get("refresh_llm") == "true"
            need_comments = request.query_params.get("need_comments") != "false"

            if not job_id and not pk:
                raise ValidationError("Either 'job_id' or 'id' is required")

            # Fetch the job by job_id or id
            job = None
            if job_id:
                job = get_object_or_404(Job, job_id=job_id)
            elif pk:
                job = get_object_or_404(Job, id=pk)

            if not job:
                return Response(
                    {"message": "Job not found", "success": False},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Handle LLM response
            if refresh_llm:
                llm_data = self.get_llm_data(job_id=job_id, pk=pk)
            else:
                llm_data = self.get_or_create_llm_response(job, job_id, pk)

            # Fetch comments and serialize job
            if need_comments:
                comments = Comment.objects.filter(job=job)
            else:
                comments = Comment.objects.none()

            comment_serializer = CommentSerializer(comments, many=True)
            job_serializer = JobSerializer(job)

            # Construct response
            return Response(
                {
                    "job": job_serializer.data,
                    "llm_response": llm_data,  # llm_data,
                    "comments": comment_serializer.data,
                    "refresh_llm": refresh_llm,
                    "message": "Job and comments retrieved successfully",
                    "success": True,
                }
            )

        except ValidationError as ve:
            logger.error(f"Validation error: {ve}")
            return Response(
                {"message": str(ve), "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get_llm_data(self, job_id=None, pk=None):
        """
        Fetch or initialize LLM data.
        """
        try:
            # Simulating LLM call or response generation
            llm = LLM(job_id=job_id, id=pk)
            return llm
        except Exception as e:
            logger.error(f"Error fetching LLM data: {e}")
            raise

    @transaction.atomic
    def get_or_create_llm_response(self, job, job_id=None, pk=None):
        """
        Retrieve existing LLM response or create a new one.
        """
        try:
            # Check if an LLM response already exists
            llm_response = job.llm_responses.first()
            if llm_response:
                return LLMResponseSerializer(llm_response).data

            # If no response exists, create a new one
            llm_data = self.get_llm_data(job_id=job_id, pk=pk)
            if not llm_data.get("success"):
                return llm_data

            # Remove any unnecessary nested structures from llm_data for other_data field
            filtered_llm_data = {
                key: value
                for key, value in llm_data.items()
                if key
                not in [
                    "client_names",
                    "keywords",
                    "company",
                    "client_location",
                    "success",
                ]
            }

            llm_response = LLMResponse.objects.create(
                job=job,
                client_names=llm_data.get("client_names"),
                keywords=llm_data.get("keywords"),
                company=llm_data.get("company"),
                client_location=llm_data.get("client_location"),
                other_data=filtered_llm_data,  # Store only the filtered data
            )
            llm_response.save()

            return LLMResponseSerializer(llm_response).data

        except Exception as e:
            # Handle exception appropriately (you can log the error if needed)
            return {"success": False, "error": str(e)}


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


class LLMView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            job_id = request.query_params.get("job_id")
            id = request.query_params.get("id")
            res = LLM(job_id=job_id, id=id)
            return Response(
                {
                    "message": "LLM data retrieved successfully",
                    "success": True,
                    "data": res,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}", "success": False},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Get all jobs and render them in an HTML template
class GetAllJobs(APIView):
    permission_classes = []

    def get(self, request):
        jobs = Job.objects.all()
        serialized_jobs = JobSerializer(jobs, many=True).data
        return render(request, "index.html", {"jobs": serialized_jobs})


# Get a specific job by id and render it in an HTML template
class GetJob(APIView):
    permission_classes = []

    def get(self, request, pk=None):
        try:
            job_retrieve_view = JobRetrieve()
            data = job_retrieve_view.get(request)

            if data:
                return render(request, "job.html", data.data)
            else:
                return render(request, "job.html", {})
        except Exception as e:
            return render(request, "job.html", {})

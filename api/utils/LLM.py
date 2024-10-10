from langchain_openai import ChatOpenAI
import re
import json
from dotenv import load_dotenv
import os
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from api.models import Job, Comment
from api.serializer import JobSerializer, CommentSerializer

load_dotenv()

prompt = """
Please analyze the provided job data and freelancer feedback to extract information about the client. Specifically, you should:

1. Collect all client names mentioned in the data, including multiple names if available.
2. Determine the client's location based on the information provided.
3. Identify the client's company name, if it is mentioned.
4. Generate a list of currently trending SEO keywords that can improve the client's visibility on LinkedIn, focusing on jobs that are less than two years old.
5. Describe the type of work the client performs based on the job descriptions and feedback.
6. Extract any other critical information about the client that could be useful for future reference.

Important Guidelines:
1. Use only the data provided; do not make any assumptions or add information that is not explicitly present.
2. Avoid hallucinations by strictly adhering to the given data.
3. If certain information is missing, leave the corresponding field empty in the JSON response.

Sample JSON Response Format:
{
  "client_names": [
    "List all client names or first names mentioned in the data."
  ],
  "client_location": "Client's location as mentioned in the data.",
  "company": "Client's company name, if provided.",
  "keywords": [
    "List of currently trending SEO keywords to improve the client's LinkedIn visibility."
  ],
  "work": "Description of the type of work the client does based on the job descriptions and feedback.",
  "crucial_info": "Any other critical information about the client from the data."
}

JSON Data:
"""


def sanitize_json_string(json_string: str) -> str:
    json_string = re.sub(r"[\x00-\x1f\x7f]", "", json_string)
    return json_string


def LLM(job_id: str = None, id: str = None):
    try:
        if job_id:
            job = get_object_or_404(Job.objects.all(), job_id=job_id)
        elif id:
            job = get_object_or_404(Job.objects.all(), id=id)
        else:
            return
        comments = Comment.objects.filter(job=job)
        comment_serializer = CommentSerializer(comments, many=True)

        job = {
            "title": job.title,
            "description": job.description,
            "skills": job.skills,
            "is_payment_verified": job.is_payment_verified,
            "client_location": job.client_location,
            "pricing_details": job.pricing_details,
            "rating": job.rating,
        }

        comments = []

        for comment in comment_serializer.data:
            comment = {
                # "rating": comment["rating"],
                # "billed_amount": comment["billed_amount"],
                "job_title": comment["job_title"],
                "description": comment["description"],
                "freelancer_feedback": comment["freelancer_feedback"],
                "posted_on": comment["posted_on"],
            }
            comments.append(comment)

        data = {"job": job, "old_jobs": comments}

        llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
        try:
            messages = [{"role": "system", "content": prompt + json.dumps(data)}]
            response = llm.invoke(messages)
            response = sanitize_json_string(response.content)
            response = response.replace("```", "")
            response = response.replace("json", "")
            response = json.loads(response)
            return {
                "success": True,
                **response,
            }
        except Exception as e:
            print(e)
            return {"error": "An error occurred while processing the request.", "success": False}

    except Exception as e:
        print(e)
        return {"success": False}

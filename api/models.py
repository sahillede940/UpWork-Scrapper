from django.db import models
from datetime import date


class Job_List(models.Model):
    job_id = models.CharField(max_length=200, default="184064313115", unique=True)
    title = models.CharField(max_length=200)
    posted_time = models.CharField(max_length=200)
    payment_verified = models.BooleanField(default=False)
    total_spent = models.FloatField(default=0.0)
    location = models.CharField(max_length=200)
    rating = models.FloatField(null=True)
    job_type = models.JSONField(default=dict)
    description = models.TextField(null=True)
    skills = models.JSONField(default=list)
    proposals = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)  # Created at
    updated_at = models.DateTimeField(auto_now=True)  # Updated at

    def __str__(self):
        return self.title


class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    skills = models.JSONField(default=list, blank=True, null=True)
    is_payment_verified = models.BooleanField(default=False)
    client_location = models.CharField(max_length=200, null=True, blank=True)
    job_url = models.URLField(null=True, blank=True)
    job_id = models.CharField(max_length=200, unique=True)
    pricing_details = models.JSONField(default=dict)
    rating = models.FloatField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)  # Created at
    updated_at = models.DateTimeField(auto_now=True)  # Updated at

    def __str__(self):
        return self.title


class Comment(models.Model):
    job = models.ForeignKey(Job, related_name="comments", on_delete=models.CASCADE)
    url = models.URLField(null=True, blank=True)
    rating = models.FloatField(blank=True, null=True)
    billed_amount = models.CharField(default="0.0", max_length=200, null=True, blank=True)
    job_title = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    client_feedback = models.TextField(blank=True, null=True)
    freelancer_feedback = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.job_title

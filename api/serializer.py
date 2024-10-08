from rest_framework import serializers

from .models import Job_List, Job, Comment


class JobListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job_List
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

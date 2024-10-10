# Generated by Django 5.1.1 on 2024-10-10 16:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_comment_posted_on'),
    ]

    operations = [
        migrations.CreateModel(
            name='LLMResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('keywords', models.JSONField(blank=True, default=list, null=True)),
                ('company', models.CharField(blank=True, max_length=200, null=True)),
                ('data', models.JSONField(blank=True, default=dict, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='llm_responses', to='api.job')),
            ],
        ),
    ]

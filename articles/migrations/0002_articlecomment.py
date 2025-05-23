# Generated by Django 5.1.7 on 2025-04-06 20:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Comment')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Posted')),
                ('approved', models.BooleanField(default=True, verbose_name='Approved')),
                ('moderator_attention_needed', models.BooleanField(default=False, verbose_name='Needs Attention')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='articles.article')),
                ('flagged_by', models.ManyToManyField(blank=True, related_name='flagged_article_comments', to=settings.AUTH_USER_MODEL, verbose_name='Flagged By')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='article_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Article Comment',
                'verbose_name_plural': 'Article Comments',
                'ordering': ['created_date'],
            },
        ),
    ]

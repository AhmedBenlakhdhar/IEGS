# Generated by Django 5.1.7 on 2025-04-02 15:04

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_alter_article_options_article_header_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='author_name',
            field=models.CharField(blank=True, help_text='Display author name (if not linked to user)', max_length=100, verbose_name='Author Name'),
        ),
        migrations.AlterField(
            model_name='article',
            name='content',
            field=models.TextField(verbose_name='Content'),
        ),
        migrations.AlterField(
            model_name='article',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created Date'),
        ),
        migrations.AlterField(
            model_name='article',
            name='header_image_url',
            field=models.URLField(blank=True, help_text='URL for an image to display at the top of the article.', max_length=300, null=True, verbose_name='Header Image URL'),
        ),
        migrations.AlterField(
            model_name='article',
            name='published_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Published Date'),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=250, verbose_name='Title'),
        ),
        migrations.AlterField(
            model_name='article',
            name='updated_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated Date'),
        ),
    ]

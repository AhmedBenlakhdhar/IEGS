# Generated by Django 5.1.7 on 2025-04-04 17:47

import ckeditor_uploader.fields
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Title')),
                ('title_en', models.CharField(max_length=250, null=True, verbose_name='Title')),
                ('title_ar', models.CharField(max_length=250, null=True, verbose_name='Title')),
                ('slug', models.SlugField(blank=True, help_text='Unique URL-friendly name. Leave blank to auto-generate from title.', max_length=270, unique=True)),
                ('header_image_url', models.URLField(blank=True, help_text='URL for an image to display at the top of the article.', max_length=300, null=True, verbose_name='Header Image URL')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Content')),
                ('content_en', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='Content')),
                ('content_ar', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='Content')),
                ('author_name', models.CharField(blank=True, help_text='Display author name (if not linked to user)', max_length=100, verbose_name='Author Name')),
                ('author_name_en', models.CharField(blank=True, help_text='Display author name (if not linked to user)', max_length=100, null=True, verbose_name='Author Name')),
                ('author_name_ar', models.CharField(blank=True, help_text='Display author name (if not linked to user)', max_length=100, null=True, verbose_name='Author Name')),
                ('published_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Published Date')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Created Date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Updated Date')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
                'ordering': ['-published_date'],
            },
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Category Name')),
                ('name_en', models.CharField(max_length=100, null=True, unique=True, verbose_name='Category Name')),
                ('name_ar', models.CharField(max_length=100, null=True, unique=True, verbose_name='Category Name')),
                ('slug', models.SlugField(blank=True, help_text='URL-friendly name, leave blank to auto-generate.', max_length=110, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('description_en', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('description_ar', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
            options={
                'verbose_name': 'Article Category',
                'verbose_name_plural': 'Article Categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ArticleCategoryMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.article')),
                ('articlecategory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.articlecategory')),
            ],
            options={
                'unique_together': {('article', 'articlecategory')},
            },
        ),
        migrations.AddField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(blank=True, related_name='articles', through='articles.ArticleCategoryMembership', to='articles.articlecategory', verbose_name='Categories'),
        ),
    ]

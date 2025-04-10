# Generated by Django 5.1.7 on 2025-04-10 04:04

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0006_alter_ratingtier_color_hex_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhyMGCPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Why MGC?', max_length=200, verbose_name='Page Title')),
                ('title_en', models.CharField(default='Why MGC?', max_length=200, null=True, verbose_name='Page Title')),
                ('title_ar', models.CharField(default='Why MGC?', max_length=200, null=True, verbose_name='Page Title')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Page Content')),
                ('content_en', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='Page Content')),
                ('content_ar', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='Page Content')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
            ],
            options={
                'verbose_name': 'Why MGC Page',
                'verbose_name_plural': 'Why MGC Page',
            },
        ),
    ]

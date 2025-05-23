# Generated by Django 5.1.7 on 2025-04-17 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0013_alter_flag_options_remove_game_rationale_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='boycott_reason',
            field=models.TextField(blank=True, help_text='Reason for the game-specific boycott (if applicable).', null=True, verbose_name='Game Boycott Reason'),
        ),
        migrations.AddField(
            model_name='game',
            name='is_boycotted',
            field=models.BooleanField(default=False, help_text='Check this if the game itself is subject to a specific boycott, independent of developer/publisher.', verbose_name='Is Game Specifically Boycotted?'),
        ),
        migrations.CreateModel(
            name='BoycottedEntity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Exact name of the developer or publisher.', max_length=150, verbose_name='Entity Name')),
                ('slug', models.SlugField(blank=True, help_text='Leave blank to auto-generate.', max_length=160, unique=True)),
                ('entity_type', models.CharField(choices=[('DEVELOPER', 'Developer'), ('PUBLISHER', 'Publisher')], max_length=10, verbose_name='Entity Type')),
                ('reason', models.TextField(blank=True, help_text='Optional: Briefly explain the reason.', verbose_name='Reason for Boycott')),
                ('is_active', models.BooleanField(default=True, help_text='Uncheck to disable this boycott notice without deleting.', verbose_name='Boycott Active')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='Date Added')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
            ],
            options={
                'verbose_name': 'Boycotted Entity',
                'verbose_name_plural': 'Boycotted Entities',
                'ordering': ['name'],
                'unique_together': {('name', 'entity_type')},
            },
        ),
    ]

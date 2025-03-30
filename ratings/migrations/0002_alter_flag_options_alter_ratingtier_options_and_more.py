# Generated by Django 5.1.7 on 2025-03-30 13:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flag',
            options={'verbose_name': 'Content Flag', 'verbose_name_plural': 'Content Flags'},
        ),
        migrations.AlterModelOptions(
            name='ratingtier',
            options={'ordering': ['order'], 'verbose_name': 'Rating Tier', 'verbose_name_plural': 'Rating Tiers'},
        ),
        migrations.AddField(
            model_name='game',
            name='aqidah_details',
            field=models.TextField(blank=True, help_text='Specific examples related to Aqidah concerns (magic, deities, ideologies etc).'),
        ),
        migrations.AddField(
            model_name='game',
            name='aqidah_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='audio_music_details',
            field=models.TextField(blank=True, help_text='Details about background music, lyrics, ability to mute.'),
        ),
        migrations.AddField(
            model_name='game',
            name='audio_music_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='immorality_details',
            field=models.TextField(blank=True, help_text="Examples of 'Awrah, suggestive themes, promotion of impermissible relationships, bad language/conduct."),
        ),
        migrations.AddField(
            model_name='game',
            name='immorality_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='online_conduct_details',
            field=models.TextField(blank=True, help_text='Risks related to online chat, community toxicity, moderation.'),
        ),
        migrations.AddField(
            model_name='game',
            name='online_conduct_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='substances_gambling_details',
            field=models.TextField(blank=True, help_text='Examples of substance use/promotion, gambling mechanics.'),
        ),
        migrations.AddField(
            model_name='game',
            name='substances_gambling_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='time_addiction_details',
            field=models.TextField(blank=True, help_text='Notes on addictive mechanics, time investment required, potential for neglecting duties.'),
        ),
        migrations.AddField(
            model_name='game',
            name='time_addiction_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AddField(
            model_name='game',
            name='violence_details',
            field=models.TextField(blank=True, help_text='Specific examples of violence, gore, context.'),
        ),
        migrations.AddField(
            model_name='game',
            name='violence_severity',
            field=models.CharField(choices=[('N', 'None'), ('L', 'Low'), ('M', 'Medium'), ('H', 'High'), ('P', 'Prohibited')], default='N', max_length=1),
        ),
        migrations.AlterField(
            model_name='game',
            name='flags',
            field=models.ManyToManyField(blank=True, help_text='Quick visual indicators for potential content types.', related_name='games', to='ratings.flag'),
        ),
        migrations.AlterField(
            model_name='game',
            name='rating_tier',
            field=models.ForeignKey(help_text='Overall IEGS Rating based on detailed assessment.', on_delete=django.db.models.deletion.PROTECT, related_name='games', to='ratings.ratingtier'),
        ),
        migrations.AlterField(
            model_name='game',
            name='rationale',
            field=models.TextField(blank=True, help_text='General rationale summary (optional).'),
        ),
    ]

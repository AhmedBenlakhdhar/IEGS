# Generated by Django 5.1.7 on 2025-03-30 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_alter_flag_options_alter_ratingtier_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='description_image_url',
            field=models.URLField(blank=True, help_text='URL for an image to display within the game details/description area.', max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='is_adjustable',
            field=models.BooleanField(default=False, help_text='Tick if potentially impermissible elements can be fully disabled/avoided.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='aqidah_details',
            field=models.TextField(blank=True, help_text='Specific examples: Magic, deities, ideologies etc.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='audio_music_details',
            field=models.TextField(blank=True, help_text='Details: Background music, lyrics, mutability.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='cover_image_url',
            field=models.URLField(blank=True, help_text="URL for the game's COVER image (used in lists/header).", max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='immorality_details',
            field=models.TextField(blank=True, help_text="Examples: 'Awrah, suggestive themes, bad language/conduct."),
        ),
        migrations.AlterField(
            model_name='game',
            name='online_conduct_details',
            field=models.TextField(blank=True, help_text='Risks: Online chat, community toxicity, moderation.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='rationale',
            field=models.TextField(blank=True, help_text='**Overall justification** for the assigned Halal/Mashbouh/Haram/Kufr rating tier.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='substances_gambling_details',
            field=models.TextField(blank=True, help_text='Examples: Substance use, gambling mechanics.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='time_addiction_details',
            field=models.TextField(blank=True, help_text='Notes: Addictive mechanics, time investment, neglecting duties.'),
        ),
        migrations.AlterField(
            model_name='game',
            name='violence_details',
            field=models.TextField(blank=True, help_text='Specific examples: Violence, gore, context.'),
        ),
        migrations.AlterField(
            model_name='ratingtier',
            name='tier_code',
            field=models.CharField(choices=[('HAL', '✅ Halal / Mubah'), ('MSH', '⚠️ Mashbouh'), ('HRM', '❌ Haram'), ('KFR', '🛑 Kufr')], max_length=3, primary_key=True, serialize=False, unique=True),
        ),
    ]

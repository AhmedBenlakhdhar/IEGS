# Generated by Django 5.1.7 on 2025-04-06 22:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='original_rating_tier',
            field=models.ForeignKey(blank=True, help_text="The game's rating before required adjustments were applied. Only set if 'Requires Adjustment' is True.", null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='games_originally_this_tier', to='ratings.ratingtier', verbose_name='Original Rating Tier (Before Adjustment)'),
        ),
        migrations.AlterField(
            model_name='game',
            name='rating_tier',
            field=models.ForeignKey(help_text='Overall MGC Rating based on detailed assessment (AFTER adjustment, if any).', on_delete=django.db.models.deletion.PROTECT, related_name='games_final_tier', to='ratings.ratingtier', verbose_name='Rating Tier (Final)'),
        ),
    ]

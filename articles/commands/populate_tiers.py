# ratings/management/commands/populate_tiers.py

from django.core.management.base import BaseCommand
from ratings.models import RatingTier
from django.db import transaction
from django.utils.translation import gettext_lazy as _ # For default display names

# Define initial tier data (Match tier_code with GAME_DATA in populate_games)
# Ensure display_name matches what you want translated later or use _() here
TIER_DATA = [
    {'tier_code': 'HAL', 'display_name': 'Halal',      'icon_name': 'check_circle', 'color_hex': '#00e676', 'order': 0, 'description': 'Permissible.'},
    {'tier_code': 'MSH', 'display_name': 'Mashbouh',   'icon_name': 'warning',      'color_hex': '#ffc107', 'order': 1, 'description': 'Doubtful / Caution Advised.'},
    {'tier_code': 'HRM', 'display_name': 'Haram',      'icon_name': 'cancel',       'color_hex': '#ff5252', 'order': 2, 'description': 'Impermissible.'},
    {'tier_code': 'KFR', 'display_name': 'Kufr',       'icon_name': 'gpp_bad',      'color_hex': '#78909c', 'order': 3, 'description': 'Disbelief / Polytheism.'},
    # Add others if needed
]

class Command(BaseCommand):
    help = 'Populates the database with initial RatingTier data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating rating tiers..."))
        created_count = 0
        updated_count = 0

        for tier_info in TIER_DATA:
            tier, created = RatingTier.objects.update_or_create(
                tier_code=tier_info['tier_code'],
                defaults={
                    'display_name': tier_info['display_name'],
                    'icon_name': tier_info['icon_name'],
                    'color_hex': tier_info['color_hex'],
                    'order': tier_info['order'],
                    'description': tier_info['description'],
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  CREATED Tier: {tier.tier_code} - {tier.display_name}"))
                created_count += 1
            else:
                self.stdout.write(f"  Checked/Updated Tier: {tier.tier_code}")
                updated_count += 1

        self.stdout.write(self.style.SUCCESS("Finished rating tier population."))
        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}")
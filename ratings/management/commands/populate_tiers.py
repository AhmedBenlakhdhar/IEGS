# ratings/management/commands/populate_tiers.py

from django.core.management.base import BaseCommand
from ratings.models import RatingTier
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# --- UPDATED Tier Data with new descriptions ---
TIER_DATA = [
    {'tier_code': 'HAL', 'display_name': _('Acceptable'),   'icon_name': 'check_circle', 'color_hex': '#00e676', 'order': 0, 'description': _('Permissible. Meets criteria for Acceptable based on severity breakdown.')},
    {'tier_code': 'MSH', 'display_name': _('Doubtful'),     'icon_name': 'warning',      'color_hex': '#ffc107', 'order': 1, 'description': _('Contains elements requiring caution. Meets criteria for Doubtful based on severity breakdown.')},
    {'tier_code': 'HRM', 'display_name': _('Haram'),        'icon_name': 'cancel',       'color_hex': '#ff5252', 'order': 2, 'description': _('Impermissible due to Haram content. Meets criteria for Haram based on severity breakdown.')},
    {'tier_code': 'KFR', 'display_name': _('Kufr/Shirk'),   'icon_name': 'gpp_bad',      'color_hex': '#78909c', 'order': 3, 'description': _('Impermissible due to Kufr/Shirk. Meets criteria for Kufr/Shirk based on severity breakdown.')},
]

class Command(BaseCommand):
    help = 'Populates the database with initial RatingTier data (Updated Descriptions).' # Updated help text

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating rating tiers (Updated Descriptions)...")) # Updated notice
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
                    'description': tier_info['description'], # Use the updated description
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  CREATED Tier: {tier.tier_code} - {tier.display_name}"))
                created_count += 1
            else:
                # Check if description changed
                tier_check = RatingTier.objects.get(tier_code=tier_info['tier_code'])
                updated_flag = False
                if tier_check.display_name != tier_info['display_name']: updated_flag = True
                if tier_check.description != tier_info['description']: updated_flag = True # Check description
                if tier_check.icon_name != tier_info['icon_name'] or \
                   tier_check.color_hex != tier_info['color_hex'] or \
                   tier_check.order != tier_info['order']: updated_flag = True

                if updated_flag:
                     self.stdout.write(f"  UPDATED Tier: {tier.tier_code} to {tier.display_name}")
                else:
                     self.stdout.write(f"  Checked/Existing Tier: {tier.tier_code}")
                updated_count += 1

        self.stdout.write(self.style.SUCCESS("Finished rating tier population."))
        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}")
# ratings/management/commands/populate_flags.py

from django.core.management.base import BaseCommand, CommandError
from ratings.models import Flag
from django.db import transaction

# --- CORRECTED FLAG DATA (Material Symbols icon names) ---
FLAG_DATA = [
    # === Critical Haram/Mashbouh Warnings ===
    # Use gpp_bad for the most severe Aqidah/Shirk/Kufr elements identified
    {"symbol": "gpp_bad", "description": "Contains Kufr/Shirk Elements"},

    # Specific flag for nudity/explicit 'Awrah issues
    {"symbol": "visibility_off", "description": "Explicit 'Awrah / Nudity"},

    # Flag for games heavily promoting lifestyles/ideologies against Islamic values
    {"symbol": "record_voice_over", "description": "Promotes Haram Lifestyles/Ideologies"}, # Was: Anti-Islamic

    # === Specific Haram/Mashbouh Mechanics ===
    # Flag for any simulated gambling, paid or not
    {"symbol": "casino", "description": "Contains Gambling Mechanics (Simulated/Paid)"}, # Merged casino/paid

    # Flag for significant presence of Haram substances
    {"symbol": "local_bar", "description": "Depicts/Promotes Haram Substances"}, # Replaces 'grass', more general

    # Flag for significant issues with Music/Audio based on assessment
    {"symbol": "music_off", "description": "Contains Impermissible Music/Audio"}, # Specific Audio concern

    # === Interaction & Time Warnings ===
    # Flag for risky online interactions
    {"symbol": "forum", "description": "Risky Online Interaction"}, # Kept 'forum', description clearer

    # Flag for high time sink / addiction potential
    {"symbol": "hourglass_top", "description": "High Time/Addiction Risk"}, # Kept
]


class Command(BaseCommand):
    help = 'Populates the database with initial Flag data (Material Symbols names and descriptions).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting flag population with Material Symbols names...")) # Updated notice

        created_count = 0
        updated_count = 0
        errors = 0

        for flag_item in FLAG_DATA:
            symbol_name = flag_item.get('symbol') # This is the icon NAME
            description = flag_item.get('description')

            if not symbol_name or not description:
                self.stderr.write(self.style.ERROR(f"Skipping invalid flag data item: {flag_item}"))
                errors += 1
                continue

            try:
                # Use update_or_create based on the icon name (which is stored in the 'symbol' field)
                flag, created = Flag.objects.update_or_create(
                    symbol=symbol_name, # Store the NAME in the 'symbol' field
                    defaults={'description': description}
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED Flag: {flag.symbol} - {flag.description}"))
                    created_count += 1
                else:
                    # Check if description actually changed before claiming update
                    # Fetch again to compare, or just count as checked
                     flag_check = Flag.objects.get(symbol=symbol_name)
                     if flag_check.description != description:
                         self.stdout.write(f"  UPDATED Flag Description for: {flag.symbol}")
                         # No need to call save(), update_or_create already did
                     # else:
                         # self.stdout.write(f"  Checked/Existing Flag: {flag.symbol}") # Optional: be more verbose
                     updated_count += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing flag '{symbol_name}': {e}"))
                errors += 1

        total = created_count + updated_count
        if errors > 0:
             self.stdout.write(self.style.WARNING(f"Finished flag population with {errors} errors."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished flag population successfully."))

        self.stdout.write(f"Summary: Created={created_count}, Updated/Existing={updated_count}, Errors={errors}, Total Processed={len(FLAG_DATA)-errors}")
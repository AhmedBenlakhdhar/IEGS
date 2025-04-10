# ratings/management/commands/populate_flags.py

from django.core.management.base import BaseCommand, CommandError
from ratings.models import Flag
from django.db import transaction
from django.utils.translation import gettext_lazy as _

# --- NEW FLAG DATA (v2.0 - Using Material Symbols Icons) ---
# Symbols are Material Symbols names. Descriptions are the translatable concern names.
FLAG_DATA = [
    # 1. Aqidah & Ideology
    {"symbol": "gpp_bad", "description": _('Forced Shirk/Kufr Action')},
    {"symbol": "hub", "description": _('Presence/Promotion of Shirk/Kufr')}, # 'hub' for interconnected false beliefs/pantheons
    {"symbol": "report_problem", "description": _('Insulting Islam')},
    {"symbol": "cloud_off", "description": _('Tampering/Depicting Unseen')}, # 'cloud_off' distinct from nudity
    {"symbol": "auto_fix_high", "description": _('Magic & Sorcery')}, # Sparkles icon
    {"symbol": "record_voice_over", "description": _('Contradictory Ideologies')}, # Promoting conflicting narratives/worldviews

    # 2. Haram Actions & Scenes
    {"symbol": "visibility_off", "description": _('Nudity & Lewd Scenes')}, # Hidden/Covered 'Awrah
    {"symbol": "music_off", "description": _('Forbidden Music/Instruments')},
    {"symbol": "casino", "description": _('Engaging in Gambling/Maysir')},
    {"symbol": "front_hand", "description": _('Intentional Lying (by Player)')}, # Hiding the truth

    # 3. Simulation & Normalization
    {"symbol": "swords", "description": _('Simulating Unjustified Aggression')}, # Represents combat/violence
    {"symbol": "local_police", "description": _('Simulating Theft & Crime')}, # Represents law-breaking
    {"symbol": "heart_broken", "description": _('Normalizing Forbidden Relationships')},
    {"symbol": "local_bar", "description": _('Normalizing Alcohol/Drugs')}, # Covers alcohol, general substances
    {"symbol": "speaker_notes_off", "description": _('Profanity/Obscenity')}, # Censored/forbidden speech

    # 4. Effects & Risks
    {"symbol": "hourglass_top", "description": _('Excessive Time Wasting')},
    {"symbol": "monetization_on", "description": _('Financial Extravagance (Microtransactions)')}, # Spending money
    {"symbol": "forum", "description": _('Online Communication Risks')}, # Online interaction
    {"symbol": "extension", "description": _('User-Generated Content Risks')}, # Add-ons/Mods
]

class Command(BaseCommand):
    help = 'Populates the database with initial Flag data (v2.0 - Material Symbols names).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting flag population (v2.0 - Material Symbols)..."))

        created_count = 0
        updated_count = 0
        errors = 0

        for flag_item in FLAG_DATA:
            symbol_name = flag_item.get('symbol') # This is the icon NAME
            description = flag_item.get('description') # This is the translatable concern text

            if not symbol_name or not description:
                self.stderr.write(self.style.ERROR(f"Skipping invalid flag data item: {flag_item}"))
                errors += 1
                continue

            try:
                # Use update_or_create based on the icon name (symbol)
                flag, created = Flag.objects.update_or_create(
                    symbol=symbol_name, # The icon name is stored in the 'symbol' field
                    defaults={'description': description} # Store the translatable description
                )

                if created:
                    # Use .description for display (will show translated if available)
                    self.stdout.write(self.style.SUCCESS(f"  CREATED Flag: {flag.symbol} - {flag.description}"))
                    created_count += 1
                else:
                    # Check if description actually changed before claiming update
                    flag_check = Flag.objects.get(symbol=symbol_name)
                    # Comparing lazy translation objects should work correctly
                    if flag_check.description != description:
                        self.stdout.write(f"  UPDATED Flag Description for: {flag.symbol}")
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
# ratings/management/commands/populate_flags.py

from django.core.management.base import BaseCommand, CommandError
from ratings.models import Flag
from django.db import transaction

# --- CORRECTED FLAG DATA (Material Symbols icon names) ---
FLAG_DATA = [
    # Using Material Symbols Names for 'symbol' field
    {"symbol": "music_note", "description": "Contains Music"},
    {"symbol": "forum", "description": "Online Interaction / Chat"},
    {"symbol": "paid", "description": "Microtransactions / Loot Boxes"},
    {"symbol": "bloodtype", "description": "Significant Violence / Gore"},
    {"symbol": "warning", "description": "Mature Themes (General)"},
    {"symbol": "hourglass_top", "description": "High Addiction Potential / Time Sink"},
    {"symbol": "school", "description": "Educational Content"},
    {"symbol": "psychology", "description": "Puzzle / Strategy Focus"},
    {"symbol": "sports_soccer", "description": "Sports"},
    {"symbol": "history_edu", "description": "Historical Setting"},
    {"symbol": "flare", "description": "Supernatural / Fantasy Themes (Non-Shirk)"},
    {"symbol": "casino", "description": "Simulated Gambling Mechanics"},
    {"symbol": "grass", "description": "Drug / Substance References"},
    {"symbol": "favorite", "description": "Promotes Impermissible Relationships / Lifestyles"}, # Still needs better icon/term
    {"symbol": "sentiment_dissatisfied", "description": "Excessive Foul Language"},
    {"symbol": "auto_fix_high", "description": "Magic / Sorcery Themes (Assess Aqidah)"},
    {"symbol": "no_adult_content", "description": "Sexual Content / Nudity ('Awrah)"},
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
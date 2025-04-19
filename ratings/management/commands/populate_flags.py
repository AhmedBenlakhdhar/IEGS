# ratings/management/commands/populate_flags.py

from django.core.management.base import BaseCommand, CommandError
from ratings.models import Flag
from django.db import transaction
from django.utils.translation import gettext_lazy as _ # Keep for potential future use

# --- FLAG DATA (v3.2 - Unique Icons, English Only Descriptors) ---
# Assigning distinct icons for each descriptor based on previous structure.
# Using English directly as _() wrapper seemed premature here since models aren't translated yet.
FLAG_DATA = [
    # A. Risks to Faith
    {"symbol": "history_edu", "description": 'Distorting Islam'},
    {"symbol": "hub", "description": 'Promoting Kufr/Shirk'},
    {"symbol": "stars", "description": 'Assuming Divinity'},
    {"symbol": "visibility", "description": 'Tampering Ghaib'},
    {"symbol": "balance", "description": 'Deviant Ideologies'},

    # B. Prohibition Exposure
    {"symbol": "casino", "description": 'Gambling'},
    {"symbol": "front_hand", "description": 'Lying'},
    {"symbol": "visibility_off", "description": 'Indecency'},
    {"symbol": "music_off", "description": 'Music'},
    {"symbol": "hourglass_top", "description": 'Time Waste'},

    # C. Normalization Risks
    {"symbol": "sentiment_dissatisfied", "description": 'Disdain/Arrogance'},
    {"symbol": "auto_fix_high", "description": 'Magic'},
    {"symbol": "local_bar", "description": 'Intoxicants'},
    {"symbol": "local_police", "description": 'Crime/Violence'},
    {"symbol": "speaker_notes_off", "description": 'Profanity'},

    # D. Player Risks
    {"symbol": "report", "description": 'Horror/Fear'},
    {"symbol": "sentiment_sad", "description": 'Despair'},
    {"symbol": "monetization_on", "description": 'Spending'},
    {"symbol": "forum", "description": 'Online Interactions'},
    {"symbol": "extension", "description": 'User Content'},
]


class Command(BaseCommand):
    help = 'Populates/Synchronizes the database with Flag data (v3.2 - Descriptors).' # Updated help

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting flag population/sync (v3.2 - Descriptors)...")) # Updated notice

        created_count = 0
        updated_count = 0
        checked_count = 0 # Count existing flags that didn't need updating
        errors = 0
        deleted_count = 0 # Track deletions

        current_symbols_in_code = {item['symbol'] for item in FLAG_DATA}
        existing_symbols_in_db = set(Flag.objects.values_list('symbol', flat=True))

        # --- 1. Update or Create flags from FLAG_DATA ---
        for flag_item in FLAG_DATA:
            symbol_name = flag_item.get('symbol')
            description = flag_item.get('description')

            if not symbol_name or not description:
                self.stderr.write(self.style.ERROR(f"Skipping invalid flag data item: {flag_item}"))
                errors += 1
                continue

            try:
                # Use update_or_create based on the symbol (which is unique)
                flag, created = Flag.objects.update_or_create(
                    symbol=symbol_name,
                    defaults={'description': description} # Update description if needed
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED Flag: {flag.symbol} - '{flag.description}'"))
                    created_count += 1
                else:
                    # Check if the description actually changed during the update_or_create call
                    # Need to fetch original state if we want precise "updated" vs "checked"
                    # For simplicity, we can assume update_or_create tried to update.
                    # A more accurate way:
                    try:
                        original_flag = Flag.objects.get(symbol=symbol_name) # Get before potential update
                        if original_flag.description != description:
                             # The description was different, so it was updated.
                             self.stdout.write(f"  UPDATED Flag Description for: {flag.symbol} to '{description}'")
                             updated_count += 1
                        else:
                             # Description was the same, so it existed but wasn't updated.
                             self.stdout.write(f"  Checked/Existing Flag: {flag.symbol}")
                             checked_count += 1
                    except Flag.DoesNotExist: # Should not happen if created is False, but safety check
                         self.stderr.write(self.style.ERROR(f"Consistency Error: Flag '{symbol_name}' reported as existing but not found."))
                         errors += 1


            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing flag '{symbol_name}': {e}"))
                errors += 1

        # --- 2. Delete flags that are in DB but no longer in FLAG_DATA ---
        symbols_to_delete = existing_symbols_in_db - current_symbols_in_code
        if symbols_to_delete:
            deleted_flags = Flag.objects.filter(symbol__in=symbols_to_delete)
            deleted_count, _ = deleted_flags.delete()
            if deleted_count > 0:
                self.stdout.write(self.style.WARNING(f"  DELETED {deleted_count} obsolete flags: {', '.join(symbols_to_delete)}"))

        # --- 3. Final summary ---
        if errors > 0:
             self.stdout.write(self.style.WARNING(f"Finished flag population with {errors} errors."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished flag population/sync successfully."))

        total_final = Flag.objects.count()
        self.stdout.write(
            f"Summary: Created={created_count}, Updated={updated_count}, Checked/Existing={checked_count}, "
            f"Deleted={deleted_count}, Errors={errors}. Total Flags in DB: {total_final}"
        )
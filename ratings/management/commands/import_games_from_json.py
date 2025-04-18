# ratings/management/commands/import_games_from_json.py
import json
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from ratings.models import Game, RatingTier
from django.db import transaction, IntegrityError
import traceback

class Command(BaseCommand):
    help = 'Imports game rating data from a specified JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='Path to the JSON file containing game data.')

    @transaction.atomic
    def handle(self, *args, **options):
        json_file_path = options['json_file']
        self.stdout.write(self.style.NOTICE(f"Starting game import from: {json_file_path}"))

        try:
            RatingTier.objects.get(tier_code='MSH') # Check if default tier exists
        except RatingTier.DoesNotExist:
            raise CommandError("CRITICAL: Default RatingTier 'MSH' not found. Run populate_tiers first.")

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                game_data_list = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"Error: JSON file not found at '{json_file_path}'")
        except json.JSONDecodeError as e:
            raise CommandError(f"Error: Invalid JSON format in '{json_file_path}': {e}")
        except Exception as e:
            raise CommandError(f"Error reading file '{json_file_path}': {e}")

        if not isinstance(game_data_list, list):
             raise CommandError("Error: JSON file must contain a list of game objects.")

        created_count = 0
        updated_count = 0
        skipped_count = 0
        errors = 0

        for game_data_item in game_data_list:
            if not isinstance(game_data_item, dict):
                self.stderr.write(self.style.WARNING(f"Skipping invalid item (not a dictionary): {game_data_item}"))
                skipped_count += 1
                continue

            title = game_data_item.get('title')
            if not title:
                self.stderr.write(self.style.ERROR(f"Skipping entry with missing title: {game_data_item}"))
                errors += 1
                continue

            defaults = {}
            # --- Populate Defaults (Careful with types and missing keys) ---
            defaults['developer'] = game_data_item.get('developer', '')
            defaults['publisher'] = game_data_item.get('publisher', '')
            defaults['summary'] = game_data_item.get('summary', '')
            defaults['developer_slug'] = slugify(defaults['developer'])
            defaults['publisher_slug'] = slugify(defaults['publisher'])

            # Availability flags
            for field in ['pc', 'ps5', 'ps4', 'xbox_series', 'xbox_one', 'switch', 'android', 'ios', 'quest']:
                defaults[f'available_{field}'] = game_data_item.get(f'available_{field}', False)

            # Links
            for link in ['steam_link', 'epic_link', 'gog_link', 'other_store_link']:
                defaults[link] = game_data_item.get(link) or None

            # Date parsing
            release_date_str = game_data_item.get('release_date')
            if release_date_str:
                try:
                    # Ensure the date string matches 'YYYY-MM-DD' format
                    defaults['release_date'] = datetime.date.fromisoformat(release_date_str)
                except ValueError:
                    self.stderr.write(self.style.ERROR(f"Invalid date format for '{title}': '{release_date_str}'. Expected YYYY-MM-DD. Skipping date."))
                    defaults['release_date'] = None
                    errors += 1 # Count as an error or just skip? Let's count it.
            else:
                defaults['release_date'] = None

            # Severity fields
            valid_severities = dict(Game.SEVERITY_CHOICES).keys()
            for field_name in Game.ALL_DESCRIPTOR_FIELDS_IN_ORDER:
                severity_value = game_data_item.get(field_name, 'N')
                # Validate severity code
                defaults[field_name] = severity_value if severity_value in valid_severities else 'N'
                if severity_value not in valid_severities:
                     self.stderr.write(self.style.WARNING(f"Invalid severity '{severity_value}' for '{field_name}' in game '{title}'. Defaulting to 'N'."))


            # --- Database Operation ---
            try:
                game, created = Game.objects.update_or_create(
                    title=title,
                    defaults=defaults
                )

                game.save() # Explicitly call save to trigger tier/flag calculation
                game.refresh_from_db()

                final_tier_code = game.rating_tier.tier_code if game.rating_tier else 'N/A'
                if created:
                    self.stdout.write(self.style.SUCCESS(f"  CREATED: {game.title} -> Calculated Rating: {final_tier_code}"))
                    created_count += 1
                else:
                    self.stdout.write(f"  Checked/Updated: {game.title} -> Calculated Rating: {final_tier_code}")
                    updated_count += 1

            except IntegrityError as e:
                 self.stderr.write(self.style.ERROR(f"Integrity error processing '{title}': {e}."))
                 errors += 1
            except Exception as e:
                 self.stderr.write(self.style.ERROR(f"General error processing '{title}': {e}\n{traceback.format_exc()}"))
                 errors += 1

        # --- Final Summary ---
        if errors > 0 or skipped_count > 0:
             self.stdout.write(self.style.WARNING(f"Finished game import with {errors} errors and {skipped_count} skipped entries."))
        else:
            self.stdout.write(self.style.SUCCESS("Finished game import successfully."))

        self.stdout.write(
            f"Summary: Created={created_count}, Updated/Existing={updated_count}, "
            f"Skipped={skipped_count}, Errors={errors}, Total Items in JSON={len(game_data_list)}"
        )
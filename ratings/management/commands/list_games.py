# ratings/management/commands/list_games.py
from django.core.management.base import BaseCommand
from ratings.models import Game

class Command(BaseCommand):
    help = 'Lists all games currently stored in the database.'

    def add_arguments(self, parser):
        # Optional: Add arguments for filtering or sorting if needed later
        parser.add_argument(
            '--sort',
            type=str,
            default='title',
            choices=['title', 'id', 'release_date', 'developer', 'publisher'], # Add more fields if needed
            help='Field to sort the games by. Default is title.',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None, # No limit by default
            help='Limit the number of games listed.',
        )

    def handle(self, *args, **options):
        sort_by = options['sort']
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(f"Fetching games from the database (sorted by {sort_by})..."))

        # Query the database
        games_query = Game.objects.select_related('rating_tier').order_by(sort_by)

        if limit:
            games_query = games_query[:limit]
            self.stdout.write(self.style.NOTICE(f"Limiting output to {limit} games."))

        games = list(games_query) # Execute the query

        if not games:
            self.stdout.write(self.style.WARNING("No games found in the database."))
            return

        self.stdout.write(self.style.SUCCESS(f"Found {len(games)} game(s):"))
        self.stdout.write("-" * 30)

        for game in games:
            # Safely get related tier code
            tier_code = game.rating_tier.tier_code if game.rating_tier else 'N/A'
            # Format release date or show placeholder
            release_str = game.release_date.strftime('%Y-%m-%d') if game.release_date else 'N/A'

            # Basic info line
            self.stdout.write(
                f"ID: {game.id:<5} | Title: {game.title:<40} | Tier: {tier_code:<5} | Released: {release_str:<10}"
            )
            # Optional: Add more details if needed
            # self.stdout.write(f"  Developer: {game.developer or 'N/A'}")
            # self.stdout.write(f"  Publisher: {game.publisher or 'N/A'}")
            # self.stdout.write("-" * 20) # Separator between games

        self.stdout.write("-" * 30)
        self.stdout.write(self.style.SUCCESS(f"Finished listing {len(games)} game(s)."))
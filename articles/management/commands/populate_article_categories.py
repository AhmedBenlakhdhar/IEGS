# articles/management/commands/populate_article_categories.py
from django.core.management.base import BaseCommand
from articles.models import ArticleCategory
from ...models import ArticleCategory
from django.db import transaction
from django.utils.text import slugify

CATEGORY_DATA = [
    "MGC Insights & Methodology",
    "Islamic Perspectives on Gaming",
    "Content Analysis Deep Dives",
    "Halal Gaming & Alternatives",
    "Guides & Practical Advice",
    "Community & Online Conduct",
    "News & Announcements",
    "Featured Game Analysis",
]

class Command(BaseCommand):
    help = 'Populates the database with initial ArticleCategory data.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Populating article categories..."))
        created_count = 0
        for name in CATEGORY_DATA:
            category, created = ArticleCategory.objects.get_or_create(
                name=name,
                defaults={'slug': slugify(name)} # Basic slug generation
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  CREATED Category: {name}"))
                created_count += 1
            else:
                # Check if slug needs update (optional)
                if not category.slug:
                    category.slug = slugify(name)
                    category.save()
                    self.stdout.write(f"  Updated slug for existing Category: {name}")
                else:
                     self.stdout.write(f"  Existing Category: {name}")


        self.stdout.write(self.style.SUCCESS(f"Finished article category population. Created {created_count} new categories."))
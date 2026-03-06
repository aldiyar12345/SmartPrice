from django.core.management.base import BaseCommand
from products.models import MarketplaceOffer
from products.parser_service import get_parser
from django.utils import timezone

class Command(BaseCommand):
    help = "Update prices for all marketplace offers that have a URL"

    def handle(self, *args, **options):
        offers = MarketplaceOffer.objects.exclude(url__isnull=True).exclude(url="")
        
        if not offers.exists():
            self.stdout.write(self.style.WARNING("No offers with URLs found."))
            return

        self.stdout.write(f"Starting price update for {offers.count()} offers...")

        updated_count = 0
        failed_count = 0

        for offer in offers:
            parser = get_parser(offer.marketplace)
            
            if not parser:
                self.stdout.write(self.style.WARNING(f"  [!] No parser for marketplace: {offer.marketplace}"))
                continue

            self.stdout.write(f"  [*] Updating {offer.product.name} on {offer.marketplace}...")
            
            new_price = parser.parse(offer.url)
            
            if new_price:
                old_price = offer.price
                offer.price = new_price
                offer.last_updated_at = timezone.now()
                offer.save()
                
                diff = new_price - old_price
                status = "UP" if diff > 0 else "DOWN" if diff < 0 else "SAME"
                self.stdout.write(
                    self.style.SUCCESS(f"    [+] Updated: {old_price} -> {new_price} ({status} {abs(diff)})")
                )
                updated_count += 1
            else:
                self.stdout.write(self.style.ERROR(f"    [-] Failed to parse price from {offer.url}"))
                failed_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done! Updated: {updated_count}, Failed: {failed_count}")
        )

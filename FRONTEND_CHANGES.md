# AURA — Sir's Frontend Changes

This version keeps the original AURA catalog and image URLs intact.

## Implemented storefront changes
- Homepage hero slider with three promotional slides.
- Flash/limited-stock promotional banner.
- Category-first browsing.
- Category → subcategory navigation chips.
- Category-wise horizontal product rails.
- Existing AURA products reused across all sections; no original product was replaced.
- Existing product images are preserved.
- Product cards now show a second existing gallery image on hover when available.
- Gallery image count badge.
- Category and subcategory shown together on product cards.
- Responsive horizontal scrolling on mobile.
- Existing search, filters, wishlist, cart and product detail flows preserved.

## Existing catalog
The original `seed_data.py` is retained. It contains the original AURA categories, subcategories, eight sample products and their existing image/gallery URLs.

## Run
Extract the project and double-click `START_AURA_IN_EDGE.bat`.
The launcher installs dependencies, migrates the database, seeds the existing catalog, starts Django and opens the storefront in Microsoft Edge.

Local demo admin:
- Username: `admin`
- Password: `Admin@12345`

Change credentials before any production deployment.

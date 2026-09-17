from fastapi import APIRouter

from app.modules.brands.router import router as brands_router
from app.modules.categories.router import router as categories_router
from app.modules.colors.router import router as colors_router
from app.modules.territories.router import router as territories_router
from app.modules.stores.router import router as stores_router
from app.modules.price_lists.router import router as price_lists_router
from app.modules.motorcycles.router import router as motorcycles_router
from app.modules.motorcycle_aliases.router import (
    router as motorcycle_aliases_router,
)
from app.modules.motorcycle_variants.router import (
    router as motorcycle_variants_router,
)
from app.modules.variant_prices.router import (
    router as variant_prices_router,
)
from app.modules.inventory.router import (
    router as inventory_router,
)
from app.modules.specification_definitions.router import (
    router as specification_definitions_router,
)
from app.modules.model_spec_values.router import (
    router as model_spec_values_router,
)
from app.modules.promotion_funding_sources.router import (
    router as promotion_funding_sources_router,
)
from app.modules.promotion_campaigns.router import (
    router as promotion_campaigns_router,
)
from app.modules.promotion_campaign_brands.router import (
    router as promotion_campaign_brands_router,
)
from app.modules.promotion_rules.router import (
    router as promotion_rules_router,
)
from app.modules.promotion_rule_models.router import (
    router as promotion_rule_models_router,
)
from app.modules.promotion_rule_variants.router import (
    router as promotion_rule_variants_router,
)
from app.modules.promotion_rule_years.router import (
    router as promotion_rule_years_router,
)
from app.modules.promotion_rule_colors.router import (
    router as promotion_rule_colors_router,
)
from app.modules.promotion_rule_territories.router import (
    router as promotion_rule_territories_router,
)
from app.modules.promotion_rule_funding.router import (
    router as promotion_rule_funding_router,
)
from app.modules.promotion_documents.router import (
    router as promotion_documents_router,
)
from app.modules.model_documents.router import (
    router as model_documents_router,
)


router = APIRouter(
    prefix="/api/v1/admin",
)


router.include_router(brands_router)
router.include_router(categories_router)
router.include_router(colors_router)
router.include_router(territories_router)
router.include_router(stores_router)
router.include_router(price_lists_router)
router.include_router(motorcycles_router)
router.include_router(motorcycle_aliases_router)
router.include_router(motorcycle_variants_router)
router.include_router(variant_prices_router)
router.include_router(inventory_router)
router.include_router(specification_definitions_router)
router.include_router(model_spec_values_router)
router.include_router(promotion_funding_sources_router)
router.include_router(promotion_campaigns_router)
router.include_router(promotion_campaign_brands_router)
router.include_router(promotion_rules_router)
router.include_router(promotion_rule_models_router)
router.include_router(promotion_rule_variants_router)
router.include_router(promotion_rule_years_router)
router.include_router(promotion_rule_colors_router)
router.include_router(promotion_rule_territories_router)
router.include_router(promotion_rule_funding_router)
router.include_router(promotion_documents_router)
router.include_router(model_documents_router)


@router.get(
    "/health",
    tags=["Admin"],
)
async def health():
    return {
        "status": "ok",
        "service": "admin",
    }

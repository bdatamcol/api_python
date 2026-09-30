import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.brands.repository import BrandRepository
from app.modules.colors.repository import ColorRepository
from app.modules.motorcycles.repository import MotorcycleRepository
from app.modules.motorcycle_variants.repository import (
    MotorcycleVariantRepository,
)
from app.modules.territories.repository import TerritoryRepository

from app.modules.promotion_funding_sources.repository import (
    PromotionFundingSourceRepository,
)

from app.modules.promotion_campaigns.model import (
    PromotionCampaign,
)
from app.modules.promotion_campaign_brands.model import (
    PromotionCampaignBrand,
)
from app.modules.promotion_rules.model import (
    PromotionRule,
)
from app.modules.promotion_rule_models.model import (
    PromotionRuleModel,
)
from app.modules.promotion_rule_variants.model import (
    PromotionRuleVariant,
)
from app.modules.promotion_rule_years.model import (
    PromotionRuleYear,
)
from app.modules.promotion_rule_colors.model import (
    PromotionRuleColor,
)
from app.modules.promotion_rule_territories.model import (
    PromotionRuleTerritory,
)
from app.modules.promotion_rule_funding.model import (
    PromotionRuleFunding,
)
from app.modules.promotion_documents.model import (
    PromotionDocument,
)

from app.modules.promotions.repository import (
    PromotionRepository,
)

from app.modules.promotions.schemas import (
    PromotionBrandDetail,
    PromotionCampaignDetail,
    PromotionColorDetail,
    PromotionCreateRequest,
    PromotionCreateResponse,
    PromotionDetailResponse,
    PromotionDocumentDetail,
    PromotionFundingDetail,
    PromotionModelDetail,
    PromotionRuleDetail,
    PromotionTerritoryDetail,
    PromotionVariantDetail,
)


class PromotionService:

    def __init__(self, db: AsyncSession):
        self.db = db

        # ========================================================
        # REPOSITORY AGREGADO (LECTURA COMPLETA)
        # ========================================================

        self.promotion_repository = PromotionRepository(
            db
        )

        # ========================================================
        # REPOSITORIES PARA VALIDAR REFERENCIAS
        # ========================================================

        self.brand_repository = BrandRepository(db)

        self.motorcycle_repository = MotorcycleRepository(db)

        self.variant_repository = MotorcycleVariantRepository(db)

        self.color_repository = ColorRepository(db)

        self.territory_repository = TerritoryRepository(db)

        self.funding_source_repository = PromotionFundingSourceRepository(db)

    # ============================================================
    # CREAR PROMOCION COMPLETA
    #
    # IMPORTANTE:
    #
    # Este método realiza UN SOLO COMMIT.
    #
    # Si cualquier operación falla:
    #
    # ROLLBACK COMPLETO
    # ============================================================

    async def create(
        self,
        data: PromotionCreateRequest,
    ) -> PromotionCreateResponse:

        try:

            # ====================================================
            # 1. VALIDAR TODAS LAS REFERENCIAS
            #
            # Hacemos esto ANTES de insertar cualquier cosa.
            # ====================================================

            await self._validate_references(data)

            # ====================================================
            # 2. CREAR CAMPAÑA
            # ====================================================

            campaign = PromotionCampaign(
                name=data.campaign.name,
                description=data.campaign.description,
                start_date=data.campaign.start_date,
                end_date=data.campaign.end_date,
                status=data.campaign.status,
                stackable=data.campaign.stackable,
            )

            self.db.add(campaign)

            # Necesitamos campaign.id para las tablas hijas.
            await self.db.flush()

            # ====================================================
            # 3. ASOCIAR MARCAS A LA CAMPAÑA
            # ====================================================

            campaign_brands = [
                PromotionCampaignBrand(
                    campaign_id=campaign.id,
                    brand_id=brand_id,
                )
                for brand_id in data.brand_ids
            ]

            if campaign_brands:
                self.db.add_all(campaign_brands)

            # ====================================================
            # 4. CREAR REGLAS
            # ====================================================

            rules: list[PromotionRule] = []

            for rule_data in data.rules:

                rule = PromotionRule(
                    campaign_id=campaign.id,
                    name=rule_data.name,
                    benefit_type=rule_data.benefit_type,
                    benefit_amount=rule_data.benefit_amount,
                    benefit_percentage=rule_data.benefit_percentage,
                    gift_description=rule_data.gift_description,
                    terms=rule_data.terms,
                    priority=rule_data.priority,
                    active=rule_data.active,
                )

                rules.append(rule)

            if rules:
                self.db.add_all(rules)

                # Necesitamos los UUID generados para crear
                # promotion_rule_models, years, colors, etc.
                await self.db.flush()

            # ====================================================
            # 5. CREAR COBERTURA DE CADA REGLA
            # ====================================================

            for rule, rule_data in zip(
                rules,
                data.rules,
                strict=True,
            ):

                # ------------------------------------------------
                # MODELOS
                # ------------------------------------------------

                rule_models = [
                    PromotionRuleModel(
                        promotion_rule_id=rule.id,
                        model_id=model_id,
                    )
                    for model_id in rule_data.model_ids
                ]

                if rule_models:
                    self.db.add_all(rule_models)

                # ------------------------------------------------
                # VARIANTES EXACTAS
                # ------------------------------------------------

                rule_variants = [
                    PromotionRuleVariant(
                        promotion_rule_id=rule.id,
                        variant_id=variant_id,
                    )
                    for variant_id in rule_data.variant_ids
                ]

                if rule_variants:
                    self.db.add_all(rule_variants)

                # ------------------------------------------------
                # AÑOS
                # ------------------------------------------------

                rule_years = [
                    PromotionRuleYear(
                        promotion_rule_id=rule.id,
                        model_year=model_year,
                    )
                    for model_year in rule_data.years
                ]

                if rule_years:
                    self.db.add_all(rule_years)

                # ------------------------------------------------
                # COLORES
                # ------------------------------------------------

                rule_colors = [
                    PromotionRuleColor(
                        promotion_rule_id=rule.id,
                        color_id=color_id,
                    )
                    for color_id in rule_data.color_ids
                ]

                if rule_colors:
                    self.db.add_all(rule_colors)

                # ------------------------------------------------
                # TERRITORIOS
                # ------------------------------------------------

                rule_territories = [
                    PromotionRuleTerritory(
                        promotion_rule_id=rule.id,
                        territory_id=territory_id,
                    )
                    for territory_id in rule_data.territory_ids
                ]

                if rule_territories:
                    self.db.add_all(rule_territories)

                # ------------------------------------------------
                # FUNDING
                # ------------------------------------------------

                rule_funding = [
                    PromotionRuleFunding(
                        promotion_rule_id=rule.id,
                        funding_source_id=(funding.funding_source_id),
                        amount=funding.amount,
                        percentage=funding.percentage,
                    )
                    for funding in rule_data.funding
                ]

                if rule_funding:
                    self.db.add_all(rule_funding)

            # ====================================================
            # 6. DOCUMENTOS DE LA CAMPAÑA
            # ====================================================

            documents: list[PromotionDocument] = []

            for document_data in data.documents:

                document = PromotionDocument(
                    campaign_id=campaign.id,
                    document_type=(document_data.document_type),
                    original_name=(document_data.original_name),
                    storage_key=(document_data.storage_key),
                    source_url=(document_data.source_url),
                    received_at=(document_data.received_at),
                    notes=document_data.notes,
                    # SQLAlchemy:
                    # metadata_json
                    #
                    # PostgreSQL:
                    # metadata
                    metadata_json=(document_data.metadata),
                )

                documents.append(document)

            if documents:
                self.db.add_all(documents)

            # ====================================================
            # 7. FLUSH FINAL
            #
            # Aquí PostgreSQL valida:
            #
            # FK
            # PK
            # CHECK
            # UNIQUE
            # etc.
            # ====================================================

            await self.db.flush()

            # ====================================================
            # 8. GUARDAR TODO
            #
            # ÚNICO COMMIT DE TODA LA OPERACIÓN.
            # ====================================================

            await self.db.commit()

            # ====================================================
            # 9. RESPUESTA
            # ====================================================

            return PromotionCreateResponse(
                campaign_id=campaign.id,
                rule_ids=[rule.id for rule in rules],
                document_ids=[document.id for document in documents],
            )

        except IntegrityError as exc:

            await self.db.rollback()

            raise ValueError(
                "No fue posible crear la promoción. "
                "La información viola una restricción "
                "de la base de datos."
            ) from exc

        except Exception:

            await self.db.rollback()

            raise

    # ============================================================
    # OBTENER PROMOCION COMPLETA POR ID
    #
    # Devuelve:
    #
    # campaign
    # brands
    # rules
    #   ├── models
    #   ├── variants
    #   ├── years
    #   ├── colors
    #   ├── territories
    #   └── funding
    #
    # documents
    # ============================================================

    async def find_by_id(
        self,
        campaign_id: uuid.UUID,
    ) -> PromotionDetailResponse:

        # ========================================================
        # 1. CAMPAÑA
        # ========================================================

        campaign = (
            await self.promotion_repository.find_campaign_by_id(
                campaign_id
            )
        )

        if campaign is None:
            raise LookupError(
                "La promoción no existe"
            )

        # ========================================================
        # 2. MARCAS
        # ========================================================

        brands = (
            await self.promotion_repository.find_brands_by_campaign(
                campaign_id
            )
        )

        # ========================================================
        # 3. REGLAS
        # ========================================================

        rules = (
            await self.promotion_repository.find_rules_by_campaign(
                campaign_id
            )
        )

        # ========================================================
        # 4. DOCUMENTOS
        # ========================================================

        documents = (
            await self.promotion_repository.find_documents_by_campaign(
                campaign_id
            )
        )

        # ========================================================
        # 5. IDS DE TODAS LAS REGLAS
        # ========================================================

        rule_ids = [
            rule.id
            for rule in rules
        ]

        # ========================================================
        # 6. TRAER TODAS LAS RELACIONES EN BLOQUE
        #
        # No hacemos consultas dentro del for de cada regla.
        # ========================================================

        model_rows = (
            await self.promotion_repository.find_models_by_rule_ids(
                rule_ids
            )
        )

        variant_rows = (
            await self.promotion_repository.find_variants_by_rule_ids(
                rule_ids
            )
        )

        year_rows = (
            await self.promotion_repository.find_years_by_rule_ids(
                rule_ids
            )
        )

        color_rows = (
            await self.promotion_repository.find_colors_by_rule_ids(
                rule_ids
            )
        )

        territory_rows = (
            await self.promotion_repository.find_territories_by_rule_ids(
                rule_ids
            )
        )

        funding_rows = (
            await self.promotion_repository.find_funding_by_rule_ids(
                rule_ids
            )
        )

        # ========================================================
        # 7. PREPARAR CONTENEDORES POR RULE_ID
        # ========================================================

        models_by_rule: dict[
            uuid.UUID,
            list[PromotionModelDetail],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        variants_by_rule: dict[
            uuid.UUID,
            list[PromotionVariantDetail],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        years_by_rule: dict[
            uuid.UUID,
            list[int],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        colors_by_rule: dict[
            uuid.UUID,
            list[PromotionColorDetail],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        territories_by_rule: dict[
            uuid.UUID,
            list[PromotionTerritoryDetail],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        funding_by_rule: dict[
            uuid.UUID,
            list[PromotionFundingDetail],
        ] = {
            rule_id: []
            for rule_id in rule_ids
        }

        # ========================================================
        # 8. AGRUPAR MODELOS
        #
        # Cada fila:
        #
        # promotion_rule_id
        # MotorcycleModel
        # ========================================================

        for (
            promotion_rule_id,
            motorcycle,
        ) in model_rows:

            models_by_rule[
                promotion_rule_id
            ].append(
                PromotionModelDetail.model_validate(
                    motorcycle
                )
            )

        # ========================================================
        # 9. AGRUPAR VARIANTES
        # ========================================================

        for (
            promotion_rule_id,
            variant,
        ) in variant_rows:

            variants_by_rule[
                promotion_rule_id
            ].append(
                PromotionVariantDetail.model_validate(
                    variant
                )
            )

        # ========================================================
        # 10. AGRUPAR AÑOS
        # ========================================================

        for (
            promotion_rule_id,
            model_year,
        ) in year_rows:

            years_by_rule[
                promotion_rule_id
            ].append(
                model_year
            )

        # ========================================================
        # 11. AGRUPAR COLORES
        # ========================================================

        for (
            promotion_rule_id,
            color,
        ) in color_rows:

            colors_by_rule[
                promotion_rule_id
            ].append(
                PromotionColorDetail.model_validate(
                    color
                )
            )

        # ========================================================
        # 12. AGRUPAR TERRITORIOS
        # ========================================================

        for (
            promotion_rule_id,
            territory,
        ) in territory_rows:

            territories_by_rule[
                promotion_rule_id
            ].append(
                PromotionTerritoryDetail.model_validate(
                    territory
                )
            )

        # ========================================================
        # 13. AGRUPAR FUNDING
        #
        # Cada fila contiene:
        #
        # promotion_rule_id
        # PromotionRuleFunding
        # PromotionFundingSource
        # ========================================================

        for (
            promotion_rule_id,
            funding,
            funding_source,
        ) in funding_rows:

            funding_by_rule[
                promotion_rule_id
            ].append(
                PromotionFundingDetail(
                    funding_source_id=(
                        funding_source.id
                    ),
                    name=funding_source.name,
                    code=funding_source.code,
                    amount=funding.amount,
                    percentage=funding.percentage,
                    active=funding_source.active,
                )
            )

        # ========================================================
        # 14. CONSTRUIR REGLAS COMPLETAS
        # ========================================================

        rule_details: list[
            PromotionRuleDetail
        ] = []

        for rule in rules:

            rule_details.append(
                PromotionRuleDetail(
                    id=rule.id,
                    name=rule.name,
                    benefit_type=rule.benefit_type,
                    benefit_amount=rule.benefit_amount,
                    benefit_percentage=(
                        rule.benefit_percentage
                    ),
                    gift_description=(
                        rule.gift_description
                    ),
                    terms=rule.terms,
                    priority=rule.priority,
                    active=rule.active,
                    created_at=rule.created_at,
                    updated_at=rule.updated_at,

                    models=models_by_rule[
                        rule.id
                    ],

                    variants=variants_by_rule[
                        rule.id
                    ],

                    years=years_by_rule[
                        rule.id
                    ],

                    colors=colors_by_rule[
                        rule.id
                    ],

                    territories=territories_by_rule[
                        rule.id
                    ],

                    funding=funding_by_rule[
                        rule.id
                    ],
                )
            )

        # ========================================================
        # 15. DOCUMENTOS
        #
        # Aquí debemos mapear metadata_json -> metadata
        # ========================================================

        document_details = [
            PromotionDocumentDetail(
                id=document.id,
                document_type=document.document_type,
                original_name=document.original_name,
                storage_key=document.storage_key,
                source_url=document.source_url,
                received_at=document.received_at,
                notes=document.notes,
                metadata=document.metadata_json,
                created_at=document.created_at,
            )
            for document in documents
        ]

        # ========================================================
        # 16. RESPUESTA FINAL
        # ========================================================

        return PromotionDetailResponse(
            campaign=(
                PromotionCampaignDetail.model_validate(
                    campaign
                )
            ),

            brands=[
                PromotionBrandDetail.model_validate(
                    brand
                )
                for brand in brands
            ],

            rules=rule_details,

            documents=document_details,
        )

    # ============================================================
    # VALIDAR TODAS LAS REFERENCIAS DEL REQUEST
    #
    # Aquí NO insertamos nada.
    #
    # Verificamos:
    #
    # marcas
    # modelos
    # variantes
    # colores
    # territorios
    # fuentes de financiación
    #
    # También verificamos coherencia:
    #
    # variante -> modelo seleccionado
    # modelo -> marca seleccionada
    # variante -> marca seleccionada
    # ============================================================

    async def _validate_references(
        self,
        data: PromotionCreateRequest,
    ) -> None:

        # ========================================================
        # CACHE
        #
        # Una promoción puede mencionar el mismo modelo,
        # color, territorio, etc. en varias reglas.
        #
        # No queremos consultar PostgreSQL repetidamente.
        # ========================================================

        brands_cache: dict[uuid.UUID, object] = {}
        models_cache: dict[uuid.UUID, object] = {}
        variants_cache: dict[uuid.UUID, object] = {}
        colors_cache: dict[uuid.UUID, object] = {}
        territories_cache: dict[uuid.UUID, object] = {}
        funding_cache: dict[uuid.UUID, object] = {}

        selected_brand_ids = set(data.brand_ids)

        # ========================================================
        # MARCAS DE LA CAMPAÑA
        # ========================================================

        for brand_id in data.brand_ids:

            brand = await self._get_active_brand(
                brand_id=brand_id,
                cache=brands_cache,
            )

            brands_cache[brand_id] = brand

        # ========================================================
        # REGLAS
        # ========================================================

        for index, rule in enumerate(
            data.rules,
            start=1,
        ):

            selected_model_ids = set(rule.model_ids)

            # ====================================================
            # MODELOS
            # ====================================================

            for model_id in rule.model_ids:

                motorcycle = await self._get_active_model(
                    model_id=model_id,
                    cache=models_cache,
                )

                # -----------------------------------------------
                # Si la campaña tiene marcas definidas,
                # el modelo debe pertenecer a una de ellas.
                # -----------------------------------------------

                if selected_brand_ids and motorcycle.brand_id not in selected_brand_ids:
                    raise ValueError(
                        f"La regla {index} contiene el modelo "
                        f"{model_id}, pero su marca no está "
                        "incluida en brand_ids"
                    )

            # ====================================================
            # VARIANTES
            # ====================================================

            for variant_id in rule.variant_ids:

                variant = await self._get_active_variant(
                    variant_id=variant_id,
                    cache=variants_cache,
                )

                # -----------------------------------------------
                # Si la regla declara model_ids y variant_ids,
                # cada variante debe pertenecer a alguno de los
                # modelos seleccionados.
                # -----------------------------------------------

                if selected_model_ids and variant.model_id not in selected_model_ids:
                    raise ValueError(
                        f"La variante {variant_id} de la "
                        f"regla {index} no pertenece a ninguno "
                        "de los model_ids seleccionados"
                    )

                # -----------------------------------------------
                # Obtener modelo padre de la variante.
                #
                # Esto también comprueba que el modelo siga
                # existiendo y activo.
                # -----------------------------------------------

                motorcycle = await self._get_active_model(
                    model_id=variant.model_id,
                    cache=models_cache,
                )

                # -----------------------------------------------
                # Si la campaña restringe marcas, la variante
                # también debe pertenecer a una de esas marcas.
                # -----------------------------------------------

                if selected_brand_ids and motorcycle.brand_id not in selected_brand_ids:
                    raise ValueError(
                        f"La variante {variant_id} de la "
                        f"regla {index} pertenece a una marca "
                        "que no está incluida en brand_ids"
                    )

            # ====================================================
            # COLORES
            # ====================================================

            for color_id in rule.color_ids:

                await self._get_active_color(
                    color_id=color_id,
                    cache=colors_cache,
                )

            # ====================================================
            # TERRITORIOS
            # ====================================================

            for territory_id in rule.territory_ids:

                await self._get_active_territory(
                    territory_id=territory_id,
                    cache=territories_cache,
                )

            # ====================================================
            # FUENTES DE FINANCIACION
            # ====================================================

            for funding in rule.funding:

                await self._get_active_funding_source(
                    funding_source_id=(funding.funding_source_id),
                    cache=funding_cache,
                )

        # ========================================================
        # NOTA:
        #
        # years ya fue validado por Pydantic:
        #
        # 1990 <= year <= 2100
        #
        # Los beneficios también fueron validados por schemas.py.
        # ========================================================

    # ============================================================
    # MARCA ACTIVA
    # ============================================================

    async def _get_active_brand(
        self,
        brand_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if brand_id in cache:
            return cache[brand_id]

        brand = await self.brand_repository.find_by_id(brand_id)

        if brand is None:
            raise ValueError(f"La marca {brand_id} no existe")

        if not brand.active:
            raise ValueError(f"La marca {brand_id} está inactiva")

        cache[brand_id] = brand

        return brand

    # ============================================================
    # MODELO ACTIVO
    # ============================================================

    async def _get_active_model(
        self,
        model_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if model_id in cache:
            return cache[model_id]

        motorcycle = await self.motorcycle_repository.find_by_id(model_id)

        if motorcycle is None:
            raise ValueError(f"El modelo {model_id} no existe")

        if not motorcycle.active:
            raise ValueError(f"El modelo {model_id} está inactivo")

        cache[model_id] = motorcycle

        return motorcycle

    # ============================================================
    # VARIANTE ACTIVA
    # ============================================================

    async def _get_active_variant(
        self,
        variant_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if variant_id in cache:
            return cache[variant_id]

        variant = await self.variant_repository.find_by_id(variant_id)

        if variant is None:
            raise ValueError(f"La variante {variant_id} no existe")

        if not variant.active:
            raise ValueError(f"La variante {variant_id} está inactiva")

        cache[variant_id] = variant

        return variant

    # ============================================================
    # COLOR ACTIVO
    # ============================================================

    async def _get_active_color(
        self,
        color_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if color_id in cache:
            return cache[color_id]

        color = await self.color_repository.find_by_id(color_id)

        if color is None:
            raise ValueError(f"El color {color_id} no existe")

        if not color.active:
            raise ValueError(f"El color {color_id} está inactivo")

        cache[color_id] = color

        return color

    # ============================================================
    # TERRITORIO ACTIVO
    # ============================================================

    async def _get_active_territory(
        self,
        territory_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if territory_id in cache:
            return cache[territory_id]

        territory = await self.territory_repository.find_by_id(territory_id)

        if territory is None:
            raise ValueError(f"El territorio {territory_id} no existe")

        if not territory.active:
            raise ValueError(f"El territorio {territory_id} está inactivo")

        cache[territory_id] = territory

        return territory

    # ============================================================
    # FUENTE DE FINANCIACION ACTIVA
    # ============================================================

    async def _get_active_funding_source(
        self,
        funding_source_id: uuid.UUID,
        cache: dict[uuid.UUID, object],
    ):

        if funding_source_id in cache:
            return cache[funding_source_id]

        funding_source = await self.funding_source_repository.find_by_id(
            funding_source_id
        )

        if funding_source is None:
            raise ValueError(
                f"La fuente de financiación " f"{funding_source_id} no existe"
            )

        if not funding_source.active:
            raise ValueError(
                f"La fuente de financiación " f"{funding_source_id} está inactiva"
            )

        cache[funding_source_id] = funding_source

        return funding_source

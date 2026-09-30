import uuid

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


# ============================================================
# TIPOS
# ============================================================

PromotionCampaignStatus = Literal[
    "DRAFT",
    "ACTIVE",
    "EXPIRED",
    "CANCELLED",
]


PromotionBenefitType = Literal[
    "FIXED_DISCOUNT",
    "PERCENTAGE_DISCOUNT",
    "BONUS",
    "CASHBACK",
    "GIFT",
]


PromotionDocumentType = Literal[
    "IMAGE",
    "PDF",
    "EXCEL",
    "EMAIL",
    "WORD",
    "OTHER",
]


ModelYear = Annotated[
    int,
    Field(
        ge=1990,
        le=2100,
    ),
]


# ============================================================
# CAMPAÑA
#
# Se convertirá internamente en:
#
# promotion_campaigns
# ============================================================

class PromotionCampaignInput(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=220,
    )

    description: str | None = None

    start_date: date
    end_date: date

    status: PromotionCampaignStatus = "DRAFT"

    stackable: bool = False

    @model_validator(mode="after")
    def validate_dates(self):

        self.name = self.name.strip()

        if not self.name:
            raise ValueError(
                "El nombre de la campaña no puede estar vacío"
            )

        if self.end_date < self.start_date:
            raise ValueError(
                "end_date no puede ser anterior a start_date"
            )

        return self


# ============================================================
# FINANCIACION / DISTRIBUCION DE BENEFICIO
#
# Se convertirá internamente en:
#
# promotion_rule_funding
# ============================================================

class PromotionFundingInput(BaseModel):

    funding_source_id: uuid.UUID

    amount: int | None = Field(
        default=None,
        ge=0,
    )

    percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=7,
        decimal_places=3,
    )

    @model_validator(mode="after")
    def validate_values(self):

        if (
            self.amount is None
            and self.percentage is None
        ):
            raise ValueError(
                "Cada fuente debe tener amount, percentage o ambos"
            )

        return self


# ============================================================
# DOCUMENTO DE LA CAMPAÑA
#
# Se convertirá internamente en:
#
# promotion_documents
#
# campaign_id NO viene aquí porque será generado al crear
# promotion_campaigns.
# ============================================================

class PromotionDocumentInput(BaseModel):

    document_type: PromotionDocumentType

    original_name: str | None = Field(
        default=None,
        max_length=255,
    )

    storage_key: str | None = None

    source_url: str | None = None

    received_at: datetime | None = None

    notes: str | None = None

    metadata: Any | None = None


# ============================================================
# REGLA PROMOCIONAL COMPLETA
#
# Esta estructura alimentará:
#
# promotion_rules
# promotion_rule_models
# promotion_rule_variants
# promotion_rule_years
# promotion_rule_colors
# promotion_rule_territories
# promotion_rule_funding
# ============================================================

class PromotionRuleInput(BaseModel):

    name: str | None = Field(
        default=None,
        max_length=220,
    )

    benefit_type: PromotionBenefitType

    benefit_amount: int | None = Field(
        default=None,
        ge=0,
    )

    benefit_percentage: Decimal | None = Field(
        default=None,
        ge=Decimal("0"),
        le=Decimal("100"),
        max_digits=7,
        decimal_places=3,
    )

    gift_description: str | None = None

    terms: str | None = None

    priority: int = 100

    active: bool = True

    # ========================================================
    # APLICABILIDAD
    # ========================================================

    model_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    variant_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    years: list[ModelYear] = Field(
        default_factory=list
    )

    color_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    territory_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    funding: list[PromotionFundingInput] = Field(
        default_factory=list
    )

    # ========================================================
    # VALIDACION DEL TIPO DE BENEFICIO
    # ========================================================

    @model_validator(mode="after")
    def validate_benefit(self):

        if self.name is not None:
            self.name = self.name.strip() or None

        # ----------------------------------------------------
        # DESCUENTO FIJO / BONO / CASHBACK
        # ----------------------------------------------------

        if self.benefit_type in {
            "FIXED_DISCOUNT",
            "BONUS",
            "CASHBACK",
        }:

            if self.benefit_amount is None:
                raise ValueError(
                    f"{self.benefit_type} requiere benefit_amount"
                )

            if self.benefit_percentage is not None:
                raise ValueError(
                    f"{self.benefit_type} no utiliza "
                    "benefit_percentage"
                )

            if self.gift_description is not None:
                raise ValueError(
                    f"{self.benefit_type} no utiliza "
                    "gift_description"
                )

        # ----------------------------------------------------
        # DESCUENTO PORCENTUAL
        # ----------------------------------------------------

        elif self.benefit_type == "PERCENTAGE_DISCOUNT":

            if self.benefit_percentage is None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT requiere "
                    "benefit_percentage"
                )

            if self.benefit_amount is not None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT no utiliza "
                    "benefit_amount"
                )

            if self.gift_description is not None:
                raise ValueError(
                    "PERCENTAGE_DISCOUNT no utiliza "
                    "gift_description"
                )

        # ----------------------------------------------------
        # OBSEQUIO
        # ----------------------------------------------------

        elif self.benefit_type == "GIFT":

            if (
                self.gift_description is None
                or not self.gift_description.strip()
            ):
                raise ValueError(
                    "GIFT requiere gift_description"
                )

            self.gift_description = (
                self.gift_description.strip()
            )

            if self.benefit_amount is not None:
                raise ValueError(
                    "GIFT no utiliza benefit_amount"
                )

            if self.benefit_percentage is not None:
                raise ValueError(
                    "GIFT no utiliza benefit_percentage"
                )

        return self

    # ========================================================
    # EVITAR DUPLICADOS DENTRO DEL MISMO REQUEST
    #
    # Esto evita llegar a errores por las PK compuestas.
    # ========================================================

    @model_validator(mode="after")
    def validate_duplicates(self):

        self._ensure_unique(
            self.model_ids,
            "model_ids",
        )

        self._ensure_unique(
            self.variant_ids,
            "variant_ids",
        )

        self._ensure_unique(
            self.years,
            "years",
        )

        self._ensure_unique(
            self.color_ids,
            "color_ids",
        )

        self._ensure_unique(
            self.territory_ids,
            "territory_ids",
        )

        funding_source_ids = [
            item.funding_source_id
            for item in self.funding
        ]

        self._ensure_unique(
            funding_source_ids,
            "funding",
        )

        return self

    @staticmethod
    def _ensure_unique(
        values: list,
        field_name: str,
    ) -> None:

        if len(values) != len(set(values)):
            raise ValueError(
                f"{field_name} contiene valores duplicados"
            )


# ============================================================
# CREACION COMPLETA DE UNA PROMOCION
#
# Este será el body de:
#
# POST /api/v1/admin/promotions
# ============================================================

class PromotionCreateRequest(BaseModel):

    campaign: PromotionCampaignInput

    # --------------------------------------------------------
    # promotion_campaign_brands
    # --------------------------------------------------------

    brand_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # promotion_rules + tablas dependientes
    # --------------------------------------------------------

    rules: list[PromotionRuleInput] = Field(
        default_factory=list
    )

    # --------------------------------------------------------
    # promotion_documents
    # --------------------------------------------------------

    documents: list[PromotionDocumentInput] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_duplicates(self):

        if len(self.brand_ids) != len(
            set(self.brand_ids)
        ):
            raise ValueError(
                "brand_ids contiene marcas duplicadas"
            )

        return self


# ============================================================
# RESPUESTA INICIAL DEL POST
#
# Más adelante tendremos un GET detallado de la promoción.
# Para la creación nos interesa confirmar los IDs generados.
# ============================================================

class PromotionCreateResponse(BaseModel):

    campaign_id: uuid.UUID

    rule_ids: list[uuid.UUID] = Field(
        default_factory=list
    )

    document_ids: list[uuid.UUID] = Field(
        default_factory=list
    )


# ============================================================
# RESPUESTAS DETALLADAS
#
# Estas estructuras se utilizarán para:
#
# GET /api/v1/admin/promotions/{campaign_id}
#
# El objetivo es que el frontend NO tenga que consultar
# individualmente todas las tablas de promociones.
# ============================================================


# ============================================================
# CAMPAÑA
# ============================================================

class PromotionCampaignDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    name: str
    description: str | None

    start_date: date
    end_date: date

    status: PromotionCampaignStatus

    stackable: bool

    created_at: datetime
    updated_at: datetime


# ============================================================
# MARCA
# ============================================================

class PromotionBrandDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    name: str
    slug: str

    active: bool


# ============================================================
# MODELO DE MOTOCICLETA
# ============================================================

class PromotionModelDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    brand_id: uuid.UUID
    category_id: uuid.UUID | None

    name: str
    slug: str

    active: bool


# ============================================================
# VARIANTE
# ============================================================

class PromotionVariantDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    model_id: uuid.UUID
    color_id: uuid.UUID | None

    sku: str | None

    model_year: int | None

    commercial_name: str | None

    active: bool


# ============================================================
# COLOR
# ============================================================

class PromotionColorDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    name: str
    slug: str

    hex_code: str | None

    active: bool


# ============================================================
# TERRITORIO
# ============================================================

class PromotionTerritoryDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: uuid.UUID

    parent_id: uuid.UUID | None

    name: str
    type: str

    code: str | None

    active: bool


# ============================================================
# DISTRIBUCION DEL BENEFICIO
#
# Aquí devolvemos también el nombre y código de la fuente,
# para que el frontend no tenga que hacer otra consulta.
# ============================================================

class PromotionFundingDetail(BaseModel):

    funding_source_id: uuid.UUID

    name: str
    code: str

    amount: int | None

    percentage: Decimal | None

    active: bool


# ============================================================
# DOCUMENTO DE LA CAMPAÑA
# ============================================================

class PromotionDocumentDetail(BaseModel):

    id: uuid.UUID

    document_type: PromotionDocumentType

    original_name: str | None

    storage_key: str | None
    source_url: str | None

    received_at: datetime | None

    notes: str | None

    metadata: Any | None

    created_at: datetime


# ============================================================
# REGLA COMPLETA
# ============================================================

class PromotionRuleDetail(BaseModel):

    id: uuid.UUID

    name: str | None

    benefit_type: PromotionBenefitType

    benefit_amount: int | None

    benefit_percentage: Decimal | None

    gift_description: str | None

    terms: str | None

    priority: int

    active: bool

    created_at: datetime
    updated_at: datetime

    # --------------------------------------------------------
    # APLICABILIDAD
    # --------------------------------------------------------

    models: list[PromotionModelDetail] = Field(
        default_factory=list
    )

    variants: list[PromotionVariantDetail] = Field(
        default_factory=list
    )

    years: list[int] = Field(
        default_factory=list
    )

    colors: list[PromotionColorDetail] = Field(
        default_factory=list
    )

    territories: list[PromotionTerritoryDetail] = Field(
        default_factory=list
    )

    funding: list[PromotionFundingDetail] = Field(
        default_factory=list
    )


# ============================================================
# PROMOCION COMPLETA
#
# Respuesta final de:
#
# GET /api/v1/admin/promotions/{campaign_id}
# ============================================================

class PromotionDetailResponse(BaseModel):

    campaign: PromotionCampaignDetail

    brands: list[PromotionBrandDetail] = Field(
        default_factory=list
    )

    rules: list[PromotionRuleDetail] = Field(
        default_factory=list
    )

    documents: list[PromotionDocumentDetail] = Field(
        default_factory=list
    )

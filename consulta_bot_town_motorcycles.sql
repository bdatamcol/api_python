-- ============================================================
-- JAPOLANDIA AI - DATABASE V1
-- PostgreSQL
--
-- Modulos iniciales:
-- 1. Catalogo
-- 2. Variantes
-- 3. Especificaciones
-- 4. Territorios y sedes
-- 5. Precios
-- 6. Inventario
-- 7. Promociones
-- 8. Documentos fuente
-- ============================================================


-- ============================================================
-- EXTENSIONES
-- ============================================================

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gist;


-- ============================================================
-- FUNCION GENERAL updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- 1. MARCAS
-- ============================================================

CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT brands_name_unique UNIQUE (name)
);

CREATE TRIGGER brands_set_updated_at
BEFORE UPDATE ON brands
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 2. CATEGORIAS
-- ============================================================

CREATE TABLE motorcycle_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,

    description TEXT,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT motorcycle_categories_name_unique UNIQUE (name)
);

CREATE TRIGGER motorcycle_categories_set_updated_at
BEFORE UPDATE ON motorcycle_categories
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 3. MODELOS
--
-- Ejemplo:
-- marca: VICTORY
-- modelo: SWITCH 125
-- categoria: TRABAJO
--
-- Aqui NO se guarda color, año ni SKU.
-- ============================================================

CREATE TABLE motorcycle_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    brand_id UUID NOT NULL,
    category_id UUID,

    name VARCHAR(160) NOT NULL,
    slug VARCHAR(220) NOT NULL UNIQUE,

    short_description TEXT,
    description TEXT,

    engine_cc NUMERIC(7,2),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_motorcycle_models_brand
        FOREIGN KEY (brand_id)
        REFERENCES brands(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_motorcycle_models_category
        FOREIGN KEY (category_id)
        REFERENCES motorcycle_categories(id)
        ON DELETE SET NULL,

    CONSTRAINT motorcycle_models_brand_name_unique
        UNIQUE (brand_id, name),

    CONSTRAINT motorcycle_models_engine_cc_check
        CHECK (engine_cc IS NULL OR engine_cc > 0)
);

CREATE TRIGGER motorcycle_models_set_updated_at
BEFORE UPDATE ON motorcycle_models
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


CREATE INDEX idx_motorcycle_models_brand
ON motorcycle_models (brand_id);

CREATE INDEX idx_motorcycle_models_category
ON motorcycle_models (category_id);

CREATE INDEX idx_motorcycle_models_active
ON motorcycle_models (active);

CREATE INDEX idx_motorcycle_models_name_trgm
ON motorcycle_models
USING GIN (name gin_trgm_ops);


-- ============================================================
-- 4. ALIAS DE MODELOS
--
-- Muy importante para IA.
--
-- Ej:
-- "apache"
-- "apache 160"
-- "rtr 160"
-- "tvs apache"
-- ============================================================

CREATE TABLE motorcycle_aliases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_id UUID NOT NULL,

    alias VARCHAR(200) NOT NULL,
    normalized_alias VARCHAR(200) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_motorcycle_aliases_model
        FOREIGN KEY (model_id)
        REFERENCES motorcycle_models(id)
        ON DELETE CASCADE,

    CONSTRAINT motorcycle_aliases_unique
        UNIQUE (model_id, normalized_alias)
);

CREATE INDEX idx_motorcycle_aliases_model
ON motorcycle_aliases (model_id);

CREATE INDEX idx_motorcycle_aliases_normalized_trgm
ON motorcycle_aliases
USING GIN (normalized_alias gin_trgm_ops);


-- ============================================================
-- 5. COLORES
-- ============================================================

CREATE TABLE colors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(120) NOT NULL,
    slug VARCHAR(150) NOT NULL UNIQUE,

    hex_code VARCHAR(7),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT colors_name_unique UNIQUE (name)
);

CREATE TRIGGER colors_set_updated_at
BEFORE UPDATE ON colors
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 6. VARIANTES
--
-- Representa la moto realmente comercializable.
--
-- Ej:
-- SWITCH 125
-- 2026
-- NEGRO MATE
-- SKU 60005599
-- ============================================================

CREATE TABLE motorcycle_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_id UUID NOT NULL,
    color_id UUID,

    sku VARCHAR(100),

    model_year SMALLINT,

    commercial_name VARCHAR(250),

    source_system VARCHAR(50) NOT NULL DEFAULT 'MANUAL',
    external_code VARCHAR(100),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_motorcycle_variants_model
        FOREIGN KEY (model_id)
        REFERENCES motorcycle_models(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_motorcycle_variants_color
        FOREIGN KEY (color_id)
        REFERENCES colors(id)
        ON DELETE SET NULL,

    CONSTRAINT motorcycle_variants_year_check
        CHECK (
            model_year IS NULL
            OR model_year BETWEEN 1990 AND 2100
        )
);

CREATE UNIQUE INDEX idx_motorcycle_variants_sku_unique
ON motorcycle_variants (sku)
WHERE sku IS NOT NULL;

CREATE INDEX idx_motorcycle_variants_model
ON motorcycle_variants (model_id);

CREATE INDEX idx_motorcycle_variants_color
ON motorcycle_variants (color_id);

CREATE INDEX idx_motorcycle_variants_year
ON motorcycle_variants (model_year);

CREATE INDEX idx_motorcycle_variants_active
ON motorcycle_variants (active);


CREATE TRIGGER motorcycle_variants_set_updated_at
BEFORE UPDATE ON motorcycle_variants
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 7. DEFINICION DE ESPECIFICACIONES
--
-- Ej:
-- Cilindraje
-- Potencia
-- Torque
-- Peso
-- ABS
-- Capacidad tanque
-- ============================================================

CREATE TABLE specification_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(150) NOT NULL,
    slug VARCHAR(170) NOT NULL UNIQUE,

    unit VARCHAR(50),

    data_type VARCHAR(20) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT specification_definitions_type_check
        CHECK (
            data_type IN (
                'TEXT',
                'NUMBER',
                'BOOLEAN',
                'JSON'
            )
        )
);


-- ============================================================
-- 8. VALORES DE ESPECIFICACIONES
-- ============================================================

CREATE TABLE model_spec_values (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_id UUID NOT NULL,
    specification_id UUID NOT NULL,

    value_text TEXT,
    value_number NUMERIC(18,4),
    value_boolean BOOLEAN,
    value_json JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_model_spec_values_model
        FOREIGN KEY (model_id)
        REFERENCES motorcycle_models(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_model_spec_values_specification
        FOREIGN KEY (specification_id)
        REFERENCES specification_definitions(id)
        ON DELETE CASCADE,

    CONSTRAINT model_spec_values_unique
        UNIQUE (model_id, specification_id),

    CONSTRAINT model_spec_values_only_one_value
        CHECK (
            num_nonnulls(
                value_text,
                value_number,
                value_boolean,
                value_json
            ) = 1
        )
);

CREATE INDEX idx_model_spec_values_model
ON model_spec_values (model_id);


CREATE TRIGGER model_spec_values_set_updated_at
BEFORE UPDATE ON model_spec_values
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 9. TERRITORIOS
--
-- Permite:
--
-- Colombia
--   -> Norte de Santander
--       -> Cucuta
--
-- y posteriormente zonas comerciales.
-- ============================================================

CREATE TABLE territories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    parent_id UUID,

    name VARCHAR(150) NOT NULL,

    type VARCHAR(30) NOT NULL,

    code VARCHAR(50),

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_territories_parent
        FOREIGN KEY (parent_id)
        REFERENCES territories(id)
        ON DELETE RESTRICT,

    CONSTRAINT territories_type_check
        CHECK (
            type IN (
                'COUNTRY',
                'DEPARTMENT',
                'CITY',
                'ZONE'
            )
        )
);

CREATE UNIQUE INDEX idx_territories_code_unique
ON territories (code)
WHERE code IS NOT NULL;

CREATE INDEX idx_territories_parent
ON territories (parent_id);


CREATE TRIGGER territories_set_updated_at
BEFORE UPDATE ON territories
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 10. SEDES
-- ============================================================

CREATE TABLE stores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    territory_id UUID NOT NULL,

    name VARCHAR(180) NOT NULL,
    code VARCHAR(80) NOT NULL UNIQUE,

    address TEXT,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_stores_territory
        FOREIGN KEY (territory_id)
        REFERENCES territories(id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_stores_territory
ON stores (territory_id);


CREATE TRIGGER stores_set_updated_at
BEFORE UPDATE ON stores
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 11. LISTAS DE PRECIOS
--
-- Permite tener:
--
-- Precio general
-- Precio Cucuta
-- Lista ERP 29
-- Precio tienda especifica
-- ============================================================

CREATE TABLE price_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    territory_id UUID,
    store_id UUID,

    name VARCHAR(160) NOT NULL,
    code VARCHAR(80) NOT NULL UNIQUE,

    currency CHAR(3) NOT NULL DEFAULT 'COP',

    priority INTEGER NOT NULL DEFAULT 100,

    source_system VARCHAR(50) NOT NULL DEFAULT 'MANUAL',

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_price_lists_territory
        FOREIGN KEY (territory_id)
        REFERENCES territories(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_price_lists_store
        FOREIGN KEY (store_id)
        REFERENCES stores(id)
        ON DELETE RESTRICT,

    CONSTRAINT price_lists_location_check
        CHECK (
            num_nonnulls(
                territory_id,
                store_id
            ) <= 1
        )
);

CREATE INDEX idx_price_lists_territory
ON price_lists (territory_id);

CREATE INDEX idx_price_lists_store
ON price_lists (store_id);


CREATE TRIGGER price_lists_set_updated_at
BEFORE UPDATE ON price_lists
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 12. HISTORIAL DE PRECIOS
--
-- Valores almacenados en pesos.
-- Sin puntos.
--
-- Ej:
-- 7449000
-- ============================================================

CREATE TABLE variant_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    price_list_id UUID NOT NULL,
    variant_id UUID NOT NULL,

    amount BIGINT NOT NULL,

    valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
    valid_until DATE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    source_reference VARCHAR(150),

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    validity DATERANGE GENERATED ALWAYS AS (
        daterange(
            valid_from,
            COALESCE(valid_until + 1, 'infinity'::DATE),
            '[)'
        )
    ) STORED,

    CONSTRAINT fk_variant_prices_price_list
        FOREIGN KEY (price_list_id)
        REFERENCES price_lists(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_variant_prices_variant
        FOREIGN KEY (variant_id)
        REFERENCES motorcycle_variants(id)
        ON DELETE RESTRICT,

    CONSTRAINT variant_prices_amount_check
        CHECK (amount > 0),

    CONSTRAINT variant_prices_dates_check
        CHECK (
            valid_until IS NULL
            OR valid_until >= valid_from
        )
);


-- Impide tener dos precios activos solapados para
-- la misma variante dentro de la misma lista.
ALTER TABLE variant_prices
ADD CONSTRAINT variant_prices_no_overlap
EXCLUDE USING gist (
    price_list_id WITH =,
    variant_id WITH =,
    validity WITH &&
)
WHERE (active);


CREATE INDEX idx_variant_prices_variant
ON variant_prices (variant_id);

CREATE INDEX idx_variant_prices_price_list
ON variant_prices (price_list_id);

CREATE INDEX idx_variant_prices_active
ON variant_prices (active);


CREATE TRIGGER variant_prices_set_updated_at
BEFORE UPDATE ON variant_prices
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 13. INVENTARIO
-- ============================================================

CREATE TABLE inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    variant_id UUID NOT NULL,
    store_id UUID NOT NULL,

    quantity INTEGER NOT NULL DEFAULT 0,
    reserved_quantity INTEGER NOT NULL DEFAULT 0,

    available_quantity INTEGER GENERATED ALWAYS AS (
        quantity - reserved_quantity
    ) STORED,

    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_inventory_variant
        FOREIGN KEY (variant_id)
        REFERENCES motorcycle_variants(id)
        ON DELETE RESTRICT,

    CONSTRAINT fk_inventory_store
        FOREIGN KEY (store_id)
        REFERENCES stores(id)
        ON DELETE RESTRICT,

    CONSTRAINT inventory_variant_store_unique
        UNIQUE (variant_id, store_id),

    CONSTRAINT inventory_quantity_check
        CHECK (quantity >= 0),

    CONSTRAINT inventory_reserved_check
        CHECK (
            reserved_quantity >= 0
            AND reserved_quantity <= quantity
        )
);

CREATE INDEX idx_inventory_store
ON inventory (store_id);

CREATE INDEX idx_inventory_variant
ON inventory (variant_id);


CREATE TRIGGER inventory_set_updated_at
BEFORE UPDATE ON inventory
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 14. CAMPAÑAS PROMOCIONALES
--
-- Ej:
-- Bonos Septiembre TVS
-- Descuentos especiales Bajaj 2026
-- ============================================================

CREATE TABLE promotion_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(220) NOT NULL,
    description TEXT,

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',

    stackable BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT promotion_campaigns_dates_check
        CHECK (end_date >= start_date),

    CONSTRAINT promotion_campaigns_status_check
        CHECK (
            status IN (
                'DRAFT',
                'ACTIVE',
                'EXPIRED',
                'CANCELLED'
            )
        )
);

CREATE INDEX idx_promotion_campaigns_dates
ON promotion_campaigns (
    start_date,
    end_date
);

CREATE INDEX idx_promotion_campaigns_status
ON promotion_campaigns (status);


CREATE TRIGGER promotion_campaigns_set_updated_at
BEFORE UPDATE ON promotion_campaigns
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 15. MARCAS DE UNA CAMPAÑA
--
-- Una campaña puede incluir una o varias marcas.
-- ============================================================

CREATE TABLE promotion_campaign_brands (
    campaign_id UUID NOT NULL,
    brand_id UUID NOT NULL,

    PRIMARY KEY (
        campaign_id,
        brand_id
    ),

    CONSTRAINT fk_promotion_campaign_brands_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES promotion_campaigns(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_campaign_brands_brand
        FOREIGN KEY (brand_id)
        REFERENCES brands(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_promotion_campaign_brands_brand
ON promotion_campaign_brands (brand_id);


-- ============================================================
-- 16. REGLAS PROMOCIONALES
--
-- Una campaña puede tener multiples reglas.
--
-- Ej:
-- Apache 310 -> bono 1.000.000
-- Raider -> bono 200.000
-- Ntorq -> bono 300.000
-- ============================================================

CREATE TABLE promotion_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    campaign_id UUID NOT NULL,

    name VARCHAR(220),

    benefit_type VARCHAR(30) NOT NULL,

    benefit_amount BIGINT,
    benefit_percentage NUMERIC(7,3),
    gift_description TEXT,

    terms TEXT,

    priority INTEGER NOT NULL DEFAULT 100,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_promotion_rules_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES promotion_campaigns(id)
        ON DELETE CASCADE,

    CONSTRAINT promotion_rules_type_check
        CHECK (
            benefit_type IN (
                'FIXED_DISCOUNT',
                'PERCENTAGE_DISCOUNT',
                'BONUS',
                'CASHBACK',
                'GIFT'
            )
        ),

    CONSTRAINT promotion_rules_amount_check
        CHECK (
            benefit_amount IS NULL
            OR benefit_amount >= 0
        ),

    CONSTRAINT promotion_rules_percentage_check
        CHECK (
            benefit_percentage IS NULL
            OR (
                benefit_percentage >= 0
                AND benefit_percentage <= 100
            )
        ),

    CONSTRAINT promotion_rules_value_check
        CHECK (
            (
                benefit_type IN (
                    'FIXED_DISCOUNT',
                    'BONUS',
                    'CASHBACK'
                )
                AND benefit_amount IS NOT NULL
            )
            OR
            (
                benefit_type = 'PERCENTAGE_DISCOUNT'
                AND benefit_percentage IS NOT NULL
            )
            OR
            (
                benefit_type = 'GIFT'
                AND gift_description IS NOT NULL
            )
        )
);

CREATE INDEX idx_promotion_rules_campaign
ON promotion_rules (campaign_id);

CREATE INDEX idx_promotion_rules_active
ON promotion_rules (active);


CREATE TRIGGER promotion_rules_set_updated_at
BEFORE UPDATE ON promotion_rules
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- 17. MODELOS A LOS QUE APLICA LA REGLA
-- ============================================================

CREATE TABLE promotion_rule_models (
    promotion_rule_id UUID NOT NULL,
    model_id UUID NOT NULL,

    PRIMARY KEY (
        promotion_rule_id,
        model_id
    ),

    CONSTRAINT fk_promotion_rule_models_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_rule_models_model
        FOREIGN KEY (model_id)
        REFERENCES motorcycle_models(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_promotion_rule_models_model
ON promotion_rule_models (model_id);


-- ============================================================
-- 18. VARIANTES EXACTAS A LAS QUE APLICA
-- ============================================================

CREATE TABLE promotion_rule_variants (
    promotion_rule_id UUID NOT NULL,
    variant_id UUID NOT NULL,

    PRIMARY KEY (
        promotion_rule_id,
        variant_id
    ),

    CONSTRAINT fk_promotion_rule_variants_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_rule_variants_variant
        FOREIGN KEY (variant_id)
        REFERENCES motorcycle_variants(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_promotion_rule_variants_variant
ON promotion_rule_variants (variant_id);


-- ============================================================
-- 19. AÑOS MODELO A LOS QUE APLICA
-- ============================================================

CREATE TABLE promotion_rule_years (
    promotion_rule_id UUID NOT NULL,
    model_year SMALLINT NOT NULL,

    PRIMARY KEY (
        promotion_rule_id,
        model_year
    ),

    CONSTRAINT fk_promotion_rule_years_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT promotion_rule_years_check
        CHECK (
            model_year BETWEEN 1990 AND 2100
        )
);


-- ============================================================
-- 20. COLORES A LOS QUE APLICA
-- ============================================================

CREATE TABLE promotion_rule_colors (
    promotion_rule_id UUID NOT NULL,
    color_id UUID NOT NULL,

    PRIMARY KEY (
        promotion_rule_id,
        color_id
    ),

    CONSTRAINT fk_promotion_rule_colors_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_rule_colors_color
        FOREIGN KEY (color_id)
        REFERENCES colors(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_promotion_rule_colors_color
ON promotion_rule_colors (color_id);


-- ============================================================
-- 21. TERRITORIOS DONDE APLICA
--
-- Ej:
-- Colombia = Nacional
-- Cucuta = solamente Cucuta
--
-- Si una regla no tiene territorios registrados,
-- se puede interpretar desde la API como "sin restriccion".
-- ============================================================

CREATE TABLE promotion_rule_territories (
    promotion_rule_id UUID NOT NULL,
    territory_id UUID NOT NULL,

    PRIMARY KEY (
        promotion_rule_id,
        territory_id
    ),

    CONSTRAINT fk_promotion_rule_territories_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_rule_territories_territory
        FOREIGN KEY (territory_id)
        REFERENCES territories(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_promotion_rule_territories_territory
ON promotion_rule_territories (territory_id);


-- ============================================================
-- 22. FUENTES DE FINANCIACION DE LA PROMOCION
--
-- Ej:
-- UMA
-- PDV
-- Fabricante
-- Concesionario
-- ============================================================

CREATE TABLE promotion_funding_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT promotion_funding_sources_name_unique
        UNIQUE (name)
);


-- ============================================================
-- 23. DISTRIBUCION DEL BONO
--
-- Ej:
--
-- Bono total: 1.000.000
--
-- UMA: 500.000
-- PDV: 500.000
-- ============================================================

CREATE TABLE promotion_rule_funding (
    promotion_rule_id UUID NOT NULL,
    funding_source_id UUID NOT NULL,

    amount BIGINT,
    percentage NUMERIC(7,3),

    PRIMARY KEY (
        promotion_rule_id,
        funding_source_id
    ),

    CONSTRAINT fk_promotion_rule_funding_rule
        FOREIGN KEY (promotion_rule_id)
        REFERENCES promotion_rules(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_promotion_rule_funding_source
        FOREIGN KEY (funding_source_id)
        REFERENCES promotion_funding_sources(id)
        ON DELETE CASCADE,

    CONSTRAINT promotion_rule_funding_value_check
        CHECK (
            amount IS NOT NULL
            OR percentage IS NOT NULL
        ),

    CONSTRAINT promotion_rule_funding_amount_check
        CHECK (
            amount IS NULL
            OR amount >= 0
        ),

    CONSTRAINT promotion_rule_funding_percentage_check
        CHECK (
            percentage IS NULL
            OR (
                percentage >= 0
                AND percentage <= 100
            )
        )
);

CREATE INDEX idx_promotion_rule_funding_source
ON promotion_rule_funding (funding_source_id);


-- ============================================================
-- 24. DOCUMENTOS ORIGEN DE LA PROMOCION
--
-- Aqui guardaremos referencia al PDF, imagen, Excel,
-- correo o comunicado original.
--
-- Ideal posteriormente para MinIO/S3.
-- ============================================================

CREATE TABLE promotion_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    campaign_id UUID NOT NULL,

    document_type VARCHAR(30) NOT NULL,

    original_name VARCHAR(255),

    storage_key TEXT,
    source_url TEXT,

    received_at TIMESTAMPTZ,

    notes TEXT,

    metadata JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_promotion_documents_campaign
        FOREIGN KEY (campaign_id)
        REFERENCES promotion_campaigns(id)
        ON DELETE CASCADE,

    CONSTRAINT promotion_documents_type_check
        CHECK (
            document_type IN (
                'IMAGE',
                'PDF',
                'EXCEL',
                'EMAIL',
                'WORD',
                'OTHER'
            )
        )
);

CREATE INDEX idx_promotion_documents_campaign
ON promotion_documents (campaign_id);


-- ============================================================
-- 25. DOCUMENTOS/FICHAS DE LAS MOTOS
--
-- Esto nos servira posteriormente para RAG.
--
-- Manual
-- ficha tecnica
-- brochure
-- catalogo
-- ============================================================

CREATE TABLE model_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    model_id UUID NOT NULL,

    title VARCHAR(250) NOT NULL,

    document_type VARCHAR(40),

    storage_key TEXT,
    source_url TEXT,

    metadata JSONB,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_model_documents_model
        FOREIGN KEY (model_id)
        REFERENCES motorcycle_models(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_model_documents_model
ON model_documents (model_id);


-- ============================================================
-- VISTAS
-- ============================================================


-- ============================================================
-- PRECIO ACTUAL
-- ============================================================

CREATE VIEW v_current_variant_prices AS
SELECT
    vp.id,
    vp.variant_id,
    vp.price_list_id,
    vp.amount,
    vp.valid_from,
    vp.valid_until
FROM variant_prices vp
WHERE
    vp.active = TRUE
    AND vp.valid_from <= CURRENT_DATE
    AND (
        vp.valid_until IS NULL
        OR vp.valid_until >= CURRENT_DATE
    );


-- ============================================================
-- INVENTARIO DISPONIBLE
-- ============================================================

CREATE VIEW v_available_inventory AS
SELECT
    i.id,
    i.variant_id,
    i.store_id,
    i.quantity,
    i.reserved_quantity,
    i.available_quantity,
    i.updated_at
FROM inventory i
WHERE i.available_quantity > 0;
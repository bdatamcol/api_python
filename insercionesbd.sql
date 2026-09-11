INSERT INTO brands (name, slug)
VALUES
    ('BAJAJ', 'bajaj'),
    ('TVS', 'tvs'),
    ('VICTORY', 'victory'),
    ('KAWASAKI', 'kawasaki');

SELECT * FROM brands;

INSERT INTO motorcycle_categories (
    name,
    slug,
    description
)
VALUES
    (
        'Scooter',
        'scooter',
        'Motocicletas tipo scooter'
    ),
    (
        'Sport',
        'sport',
        'Motocicletas deportivas y street'
    ),
    (
        'Trabajo',
        'trabajo',
        'Motocicletas orientadas al trabajo y uso diario'
    ),
    (
        'Enduro',
        'enduro',
        'Motocicletas doble propósito y enduro'
    ),
    (
        'Eléctrica',
        'electrica',
        'Motocicletas con motorización eléctrica'
    ),
    (
        'Motocarro',
        'motocarro',
        'Vehículos de tres ruedas para carga o pasajeros'
    );

SELECT * FROM motorcycle_categories;


INSERT INTO territories (
    name,
    type,
    code
)
VALUES (
    'Colombia',
    'COUNTRY',
    'CO'
);

SELECT * FROM territories;

INSERT INTO territories (
    parent_id,
    name,
    type,
    code
)
SELECT
    id,
    'Norte de Santander',
    'DEPARTMENT',
    'CO-NSA'
FROM territories
WHERE code = 'CO';

INSERT INTO territories (
    parent_id,
    name,
    type,
    code
)
SELECT
    id,
    'Cúcuta',
    'CITY',
    'CO-NSA-CUC'
FROM territories
WHERE code = 'CO-NSA';


INSERT INTO price_lists (
    territory_id,
    name,
    code,
    currency,
    priority,
    source_system
)
SELECT
    id,
    'Precio Comercial Cúcuta',
    'CUCUTA-RETAIL',
    'COP',
    10,
    'MANUAL'
FROM territories
WHERE code = 'CO-NSA-CUC';

SELECT * FROM price_lists;


SELECT * FROM promotion_funding_sources;
INSERT INTO promotion_funding_sources (
    name,
    code
)
VALUES
    ('UMA', 'UMA'),
    ('PDV', 'PDV'),
    ('Fabricante', 'MANUFACTURER'),
    ('Concesionario', 'DEALER');


INSERT INTO motorcycle_models (
    brand_id,
    category_id,
    name,
    slug,
    engine_cc
)
SELECT
    b.id,
    c.id,
    'SWITCH 125',
    'victory-switch-125',
    125
FROM brands b
JOIN motorcycle_categories c
    ON c.slug = 'trabajo'
WHERE b.slug = 'victory';

SELECT * FROM motorcycle_models;

INSERT INTO colors (
    name,
    slug
)
VALUES (
    'Negro Mate Calca Dorada',
    'negro-mate-calca-dorada'
);

SELECT * FROM colors;


INSERT INTO motorcycle_variants (
    model_id,
    color_id,
    sku,
    model_year,
    commercial_name,
    source_system,
    external_code
)
SELECT
    m.id,
    c.id,
    '60005599',
    2026,
    'VICTORY SWITCH 125 NEGRO MATE CALCA DORADA 2026',
    'ERP',
    '60005599'
FROM motorcycle_models m
JOIN colors c
    ON c.slug = 'negro-mate-calca-dorada'
WHERE m.slug = 'victory-switch-125';

SELECT * FROM motorcycle_variants;


INSERT INTO variant_prices (
    price_list_id,
    variant_id,
    amount,
    valid_from,
    source_reference
)
SELECT
    pl.id,
    mv.id,
    7449000,
    CURRENT_DATE,
    'Carga inicial'
FROM price_lists pl
JOIN motorcycle_variants mv
    ON mv.sku = '60005599'
WHERE pl.code = 'CUCUTA-RETAIL';

SELECT * FROM variant_prices;
SELECT * FROM price_lists;

INSERT INTO motorcycle_aliases (
    model_id,
    alias,
    normalized_alias
)
SELECT
    id,
    'switch',
    'switch'
FROM motorcycle_models
WHERE slug = 'victory-switch-125';

SELECT * FROM motorcycle_aliases;


INSERT INTO motorcycle_aliases (
    model_id,
    alias,
    normalized_alias
)
SELECT
    id,
    'switch 125',
    'switch 125'
FROM motorcycle_models
WHERE slug = 'victory-switch-125';

INSERT INTO motorcycle_aliases (
    model_id,
    alias,
    normalized_alias
)
SELECT
    id,
    'victory switch',
    'victory switch'
FROM motorcycle_models
WHERE slug = 'victory-switch-125';


INSERT INTO motorcycle_aliases (
    model_id,
    alias,
    normalized_alias
)
SELECT
    id,
    'victory switch 125',
    'victory switch 125'
FROM motorcycle_models
WHERE slug = 'victory-switch-125';
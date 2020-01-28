CREATE OR REPLACE VIEW public.nuevo_setup_products_template
AS SELECT p.name,
    p.image_url,
    string_agg(DISTINCT p.family::text, ','::text) AS formats,
    string_agg(DISTINCT p.framing::text, ','::text) AS framings,
    string_agg(DISTINCT p.finishing::text, ','::text) AS finishings
   FROM products p
  WHERE p.status::text = 'IN CATALOGUE'::text AND p.image_url::text <> 'http://miniature.yellowkorner.com/'::text
  GROUP BY p.name, p.image_url
  ORDER BY p.name;

-- Permissions

ALTER TABLE public.nuevo_setup_products_template OWNER TO postgres;
GRANT ALL ON TABLE public.nuevo_setup_products_template TO postgres;

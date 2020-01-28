CREATE OR REPLACE VIEW public.notas_credito_odoo
AS SELECT oai.odoo_id,
    oai.create_date,
    oai.date_invoice,
    oai.reference,
    oai.number,
    oai.date_due,
    oai.origin,
    oai.amount_total_signed,
    oai.state,
    oai.vendor_display_name
   FROM odoo_account_invoice oai
  WHERE oai.number::text ~~ 'NC%'::text;

-- Permissions

ALTER TABLE public.notas_credito_odoo OWNER TO postgres;
GRANT ALL ON TABLE public.notas_credito_odoo TO postgres;
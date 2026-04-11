-- Playground tenant seed (idempotent).
-- After first run, get the UUID for .env:
--   SELECT id, name FROM public.tenants WHERE name = 'bartek-playground';
--
-- Non-idempotent one-liner (manual / SQL editor only):
--   INSERT INTO public.tenants (id, name) VALUES (gen_random_uuid(), 'bartek-playground');

INSERT INTO public.tenants (id, name)
SELECT gen_random_uuid(), 'bartek-playground'
WHERE NOT EXISTS (
  SELECT 1 FROM public.tenants t WHERE t.name = 'bartek-playground'
);

-- Copy the printed id into COMPILORE_DEFAULT_TENANT_ID in your .env:
-- SELECT id FROM public.tenants WHERE name = 'bartek-playground';

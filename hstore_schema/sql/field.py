CREATE INDEX field_name_trigrams
ON hstore_schema_field
USING gist (name gist_trgm_ops)
;

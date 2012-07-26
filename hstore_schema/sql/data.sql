DROP VIEW IF EXISTS hstore_schema_fieldsample;


DROP VIEW IF EXISTS hstore_schema_field;


CREATE VIEW hstore_schema_field AS
SELECT row_number() OVER (ORDER BY source_id, field) AS id, * FROM (
	SELECT DISTINCT source_id, version, skeys(DATA) AS field
	FROM hstore_schema_data
) AS f;


CREATE VIEW hstore_schema_fieldsample AS
SELECT source_id, version, field,
    (SELECT array_agg(value)
     FROM
         (SELECT data->field AS value
          FROM hstore_schema_data
          WHERE hstore_schema_data.source_id = hstore_schema_field.source_id
          ORDER BY random() LIMIT 10) AS hstore_schema_values) AS sample
FROM hstore_schema_field;

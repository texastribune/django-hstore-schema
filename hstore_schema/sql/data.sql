DROP VIEW IF EXISTS hstore_schema_fieldsample;


DROP VIEW IF EXISTS hstore_schema_field;


CREATE VIEW hstore_schema_field AS
SELECT DISTINCT SOURCE, VERSION, skeys(DATA) AS field
FROM hstore_schema_data;


CREATE VIEW hstore_schema_fieldsample AS
SELECT SOURCE, field,

    (SELECT array_agg(value)
     FROM
         (SELECT DATA->field AS value
          FROM hstore_schema_data
          WHERE hstore_schema_data.SOURCE = hstore_schema_field.SOURCE
          ORDER BY random() LIMIT 10) AS hstore_schema_values) AS sample
FROM hstore_schema_field;

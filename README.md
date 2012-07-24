# Django Hstore Schema

## Problems solved

Provides a generic model for storing pk-key-values and a way to build convenient schemas on top of them for querying.

Solves these problems and more:

* Add schema mappings as you need the data

	SCHEMA(raw_source, raw_version, raw_field)
		=> VIEW(mapped_source, mapped_version, mapped_field)

* Data can be mapped to create secondary data:

	MAP(AEIS, 2010, students_by_program_special_education_2009, raw_value)
		=> DATA(AEIS, 2009, students_by_program_special_education, raw_value)

* The same data point is provided from multiple (possibly conflicting) sources

	MAP(FAST, any_version, average_teacher_salary_district, raw_value)
		=> DATA(FAST, raw_version, average_teacher_salary, raw_value)

	MAP(FAST, any_version, average_teacher_salary_campus, raw_value)
		=> DATA(FAST, raw_version, average_teacher_salary, raw_value)

	REDUCE(FAST, any_version, average_tacher_salary, *raw_values)
		=> DATA(FAST, raw_version, average_tacher_salary, coalesce(*raw_values))

* Data is formulated differently for different versions

	MAP(AEIS, 2011, students_asian, raw_value)
		=> DATA(AEIS, 2011, students_asian_pacific_islander, raw_value)

	MAP(AEIS, 2011, students_pacific_islander, raw_value)
		=> DATA(AEIS, 2011, students_asian_pacific_islander, raw_value)

	REDUCE(AEIS, 2011, students_asian_pacific_islander, *raw_values)
		=> DATA(AEIS, raw_version, students_asian_pacific_islander, sum(*raw_values))


## Workflow

1. Load primary data
2. MapReduce secondary data
3. Create schema from data
4. Profit

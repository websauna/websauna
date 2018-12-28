"""PostgreSQL helpers."""

# Use pgcrypto, instead of uuid-ossp
# Also create a function uuid_generate_v4 for backward compatibility
UUID_SUPPORT_STMT = """CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE OR REPLACE FUNCTION uuid_generate_v4()
RETURNS uuid
AS '
BEGIN
RETURN gen_random_uuid();
END'
LANGUAGE 'plpgsql';
"""

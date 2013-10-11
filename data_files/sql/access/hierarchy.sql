CREATE TABLE "collorg.access"."hierarchy" (
   cog_oid C_OID UNIQUE NOT NULL,
   FOREIGN KEY(cog_oid) REFERENCES "collorg.core".oid_table(cog_oid)
      INITIALLY DEFERRED,
   cog_fqtn C_FQTN
      DEFAULT 'collorg.access.hierarchy'
      CHECK( cog_fqtn = 'collorg.access.hierarchy' ),
   parent C_OID NOT NULL,
   FOREIGN KEY(parent) REFERENCES "collorg.core".oid_table(cog_oid),
   child C_OID NOT NULL,
   FOREIGN KEY(child) REFERENCES "collorg.core".oid_table(cog_oid),
   PRIMARY KEY(parent, child)
) INHERITS("collorg.core".base_table) ;


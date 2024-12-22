docker run \
    -р 7474:7474 -р 7687:7687 \
    --rm \
    --name neo4j-apoc \
    -e NEO4j_apoc_export_file_enabled=true \
    -e NEO4j_apoc_import_file_enabled=true \
    -e NEO4j_apoc_import_file_use__neo4j__config=true \
    -e NEO4j_PLUGINS=\[\"apoc\"\]  \
neo4j:5.21.2
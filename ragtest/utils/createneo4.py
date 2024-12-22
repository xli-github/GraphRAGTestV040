import pandas as pd
entities = pd.read_parquet('artifact/create_final_entities.parquet')
relationships = pd.read_parquet('artifact/create_final_relationships.parquet')
text_units = pd.read_parquet('artifact/create_final_text_units.parquet')
communities = pd.read_parquet('artifact/create_final_communities.parquet')
community_reports = pd.read_parquet('artifact/create_final_community_reports.parquet')

# Display the first 2 rows of the test units data
test_units.head(2)

from neo4j import GraphDatabase
import time


# 数据库连接相关参数配置
NEO4J_URI="neo4j://localhost"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="neo4j123"
NEO4J_DATABASE="neo4j"


# 实例化一个图数据库实例
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

def import_data(cypher, df, batch_size=1000):
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i: min(i + batch_size, len(df))]
        result = driver.execute_query(
            "UNWIND $rows AS value " + cypher,
            rows=batch.to_dict("records"),
            database=NEO4J_DATABASE
        )
        print(result.summary.counters)
    return

# Text units
cypher_text_units = """
MERGE (c:__Chunk__ {id:value.id})
SET c += value {.text, .n_tokens}
WITH c, value
UNWIND value.document_ids AS document
MATCH (d:__Document__ {id:document})
MERGE (c)-[:PART_OF]->(d)
"""

import_data(cypher_text_units, text_units)

# Entities
cypher_entities = """
MERGE (e:__Entity__ {id:value.id})
SET e += value {.human_readable_id, .description, name:replace(value.name, '"', '')}
WITH e, value
CALL db.create.setNodeVectorProperty(e, "description_embedding", value.description_embedding)
CALL apoc.create.addLabels(e, 
    CASE 
        WHEN coalesce(value.type, '') = '' THEN [] 
        ELSE [apoc.text.upperCamelCase(replace(value.type, '*', ''))]
    END
) YIELD node
UNWIND value.text_unit_ids AS text_unit
MATCH (c:__Chunk__ {id:text_unit})
MERGE (c)-[:HAS_ENTITY]->(e)
"""

import_data(cypher_entities, entities)

# Communities
cypher_communities = """
MERGE (c:_Community_ {community: value.id})
SET c += value {.level, .title}
/"
UNWIND value.text_unit_ids AS text_unit_id
MATCH (t:_Chunk_ {id: text_unit_id})
MERGE (c)-[:HAS_CHUNK]->(t)
WITH DISTINCT c, value
"/
WITH "
UNWIND value.relationship_ids AS rel_id
MATCH (start:_Entity_)-[:RELATED {id: rel_id}]->(end:_Entity_)
MERGE (start)-[:IN_COMMUNITY]->(c)
MERGE (end)-[:IN_COMMUNITY]->(c)
RETURN count(DISTINCT c) AS createdCommunities
"""

import_data(cypher_communities, communities)

# Community reports
cypher_community_reports = """
MATCH (c:_Community__ {community: value.community})
SET c += value {.level, .title, .rank, .rank_explanation, .full_content, .summary}
WITH c, value
UNWIND range(0, size(value.findings) - 1) AS finding_idx
WITH c, value, finding_idx, value.findings[finding_idx] AS finding
MERGE (c)-[:HAS_FINDING]->(f:Finding {id: finding_idx})
SET f += finding
"""

import_data(cypher_community_reports, community_reports)
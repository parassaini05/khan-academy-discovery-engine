// Neo4j Schema Setup & Cypher Ontology: Khan Academy Algebra & Linear Equations DAG
// Defines Node Constraints, Indexes, and Prerequisite Relationship Queries

// 1. Uniqueness Constraints
CREATE CONSTRAINT skill_id_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT concept_id_unique IF NOT EXISTS FOR (c:Concept) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT misconception_id_unique IF NOT EXISTS FOR (m:CommonMisconception) REQUIRE m.id IS UNIQUE;
CREATE CONSTRAINT rule_id_unique IF NOT EXISTS FOR (r:PrerequisiteRule) REQUIRE r.id IS UNIQUE;

// 2. Indexes for Low-Latency Traversal Queries (<15ms)
CREATE INDEX skill_slug_idx IF NOT EXISTS FOR (s:Skill) ON (s.slug);
CREATE INDEX skill_grade_idx IF NOT EXISTS FOR (s:Skill) ON (s.grade_level);
CREATE INDEX misconception_cat_idx IF NOT EXISTS FOR (m:CommonMisconception) ON (m.failure_mode);

// 3. Core Cypher Traversal Queries

// Query A: Find Direct & 2-Hop Prerequisites of a Failed Skill (Enforcing Depth <= 2)
// PARAMETER: $skill_id (e.g., 'MATH-EQ-MULTISTEP')
MATCH (target:Skill {id: $skill_id})
MATCH path = (target)-[:REQUIRES_PREREQUISITE*1..2]->(prereq:Skill)
RETURN prereq.id AS prerequisite_id,
       prereq.name AS prerequisite_name,
       prereq.grade_level AS grade_level,
       length(path) AS graph_hop_distance
ORDER BY graph_hop_distance ASC;

// Query B: Identify Most Foundational Prerequisite (Root Bottleneck)
// PARAMETER: $skill_id
MATCH (target:Skill {id: $skill_id})-[:REQUIRES_PREREQUISITE*1..3]->(ancestor:Skill)
WHERE NOT (ancestor)-[:REQUIRES_PREREQUISITE]->()
RETURN ancestor.id AS root_foundation_id,
       ancestor.name AS root_foundation_name,
       ancestor.grade_level AS grade_level
LIMIT 1;

// Query C: Trace Misconception to Root Prerequisite Node
// PARAMETER: $misconception_id (e.g., 'MISC-DISTRIB-PARTIAL')
MATCH (m:CommonMisconception {id: $misconception_id})-[:MANIFESTS_IN]->(c:Concept)
MATCH (c)-[:GOVERNS_SKILL]->(s:Skill)
OPTIONAL MATCH (s)-[:REQUIRES_PREREQUISITE]->(prereq:Skill)
RETURN m.id AS misconception_id,
       m.description AS misconception_name,
       c.id AS violated_concept_id,
       s.id AS immediate_skill_id,
       prereq.id AS prerequisite_repair_id;

from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# 从 .env 文件加载环境变量
load_dotenv()
uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
username = os.getenv("NEO4J_USERNAME", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "password")

# 建立连接到 Neo4j 数据库
driver = GraphDatabase.driver(uri, auth=(username, password))


# 添加政党节点的函数
def add_party(tx, name, ideology):
    query = "CREATE (p:Party {name: $name, ideology: $ideology}) RETURN p"
    result = tx.run(query, name=name, ideology=ideology)
    return result.peek()[0]


# 添加政府部门节点的函数
def add_government_branch(tx, name, description):
    query = "CREATE (g:Government {name: $name, description: $description}) RETURN g"
    result = tx.run(query, name=name, description=description)
    return result.peek()[0]


# 创建政党与政府部门之间的关系
def add_influence(tx, party_name, branch_name, influence_level):
    query = (
        "MATCH (p:Party {name: $party_name}), (g:Government {name: $branch_name}) "
        "CREATE (p)-[r:INFLUENCES {level: $influence_level}]->(g) "
        "RETURN type(r)"
    )
    result = tx.run(query, party_name=party_name, branch_name=branch_name, influence_level=influence_level)
    return result.peek()[0]


# 在会话中执行数据库操作
with driver.session() as session:
    # 添加政党
    session.execute_write(add_party, "Democratic", "Liberal")
    session.execute_write(add_party, "Republican", "Conservative")

    # 添加政府部门
    session.execute_write(add_government_branch, "Executive", "执行部门")
    session.execute_write(add_government_branch, "Legislative", "立法部门")
    session.execute_write(add_government_branch, "Judicial", "司法部门")

    # 创建影响力关系
    session.execute_write(add_influence, "Democratic", "Executive", "Strong")
    session.execute_write(add_influence, "Republican", "Legislative", "Strong")
    session.execute_write(add_influence, "Democratic", "Judicial", "Moderate")
    session.execute_write(add_influence, "Republican", "Executive", "Moderate")

# 关闭数据库连接
driver.close()

# 查看关系 MATCH (n)-[r]->(m) RETURN n, r, m
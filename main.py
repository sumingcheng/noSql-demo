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


# 添加员工节点的函数
def add_employee(tx, name, job_title):
    query = "CREATE (e:Employee {name: $name, jobTitle: $job_title}) RETURN e"
    result = tx.run(query, name=name, job_title=job_title)
    return result.peek()[0]  # 使用 peek() 以避免异常，仍旧假定返回至少一条记录


# 创建两个员工之间的关系
def add_relationship(tx, name1, name2, relationship_type):
    query = (
        "MATCH (e1:Employee {name: $name1}), (e2:Employee {name: $name2}) "
        "CREATE (e1)-[r:RELATIONSHIP {type: $relationship_type}]->(e2) "
        "RETURN type(r)"
    )
    result = tx.run(query, name1=name1, name2=name2, relationship_type=relationship_type)
    return result.peek()[0]  # 使用 peek() 代替 single()


# 通过姓名查找员工并返回其详细信息
def find_employee(tx, name):
    query = "MATCH (e:Employee {name: $name}) RETURN e.name, e.jobTitle"
    result = tx.run(query, name=name)
    return result.data()  # 使用 data() 以处理可能的多条记录


# 更新员工的职位信息
def update_job_title(tx, name, job_title):
    query = "MATCH (e:Employee {name: $name}) SET e.jobTitle = $job_title RETURN e"
    result = tx.run(query, name=name, job_title=job_title)
    return result.peek()[0]  # 使用 peek() 代替 single()


# 删除一个员工节点及其所有关系
def delete_employee(tx, name):
    query = "MATCH (e:Employee {name: $name}) DETACH DELETE e"
    result = tx.run(query, name=name)
    return result.summary().counters


# 在会话中执行数据库操作
with driver.session() as session:
    session.execute_write(add_employee, "Alice", "Developer")
    session.execute_write(add_employee, "Bob", "Analyst")
    session.execute_write(add_relationship, "Alice", "Bob", "COLLEAGUE")
    alice = session.execute_read(find_employee, "Alice")
    session.execute_write(update_job_title, "Bob", "Senior Analyst")
    bob = session.execute_read(find_employee, "Bob")

# 关闭数据库连接
driver.close()

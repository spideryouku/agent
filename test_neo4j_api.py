import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import requests

# 加载环境变量
load_dotenv()

#NEO4J_URI=https://api.neo4j.io/v1/instances
#NEO4J_USERNAME=neo4j
#NEO4J_PASSWORD=suckuQnSlmyVipWtC6dU_FfAtnaAoLsgs9bmZi9tiRY

class Neo4jTester:
    def __init__(self):
        self.uri = "neo4j+s://12566f3f.databases.neo4j.io"
        self.username = "neo4j"
        self.password = "suckuQnSlmyVipWtC6dU_FfAtnaAoLsgs9bmZi9tiRY"
        
    def test_db_connection(self):
        """测试 Neo4j 数据库连接 (Bolt 协议)"""
        print(f"\n--- Testing Database Connection (Bolt) ---")
        print(f"URI: {self.uri}")
        print(f"User: {self.username}")
        
        try:
            # 尝试连接
            driver = GraphDatabase.driver(self.uri, auth=(self.username, self.password))
            driver.verify_connectivity()
            print("✅ Database Connection successful!")
            
            # 简单的查询测试
            with driver.session() as session:
                result = session.run("RETURN 'Hello Neo4j' AS greeting")
                record = result.single()
                print(f"Query Result: {record['greeting']}")
                
            driver.close()
        except Exception as e:
            print(f"❌ Database Connection failed: {str(e)}")

    def test_management_api(self):
        """测试 Neo4j Aura Management API (HTTP)"""
        print(f"\n--- Testing Management API (HTTP) ---")
        
        # 检查是否是 API URL
        if not self.uri or "api.neo4j.io" not in self.uri:
            print("Skipping: NEO4J_URI does not look like a Management API URL.")
            return

        print(f"URL: {self.uri}")
        
        # 尝试使用密码作为 Bearer Token (通常需要专门的 Token，但按照用户可能的配置尝试)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.password}" 
        }
        
        try:
            response = requests.get(self.uri, headers=headers, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ API Request successful!")
                print(response.json())
            elif response.status_code == 401:
                print("❌ Unauthorized: The provided password is likely not a valid Bearer Token.")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ API Request failed: {str(e)}")

if __name__ == "__main__":
    tester = Neo4jTester()
    
    # 根据 URI 类型智能选择测试方式，或者都测
    tester.test_db_connection()
    tester.test_management_api()

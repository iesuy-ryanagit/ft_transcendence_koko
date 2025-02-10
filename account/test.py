import psycopg2
from psycopg2 import OperationalError

def connect_to_postgresql():
    try:
        # PostgreSQLコンテナへの接続設定
        connection = psycopg2.connect(
            host="db",  # PostgreSQLコンテナの名前
            database="account_db",       # 接続するデータベース名
            user="postgres",                # PostgreSQLのユーザー名
            password="postgres",            # PostgreSQLのパスワード
            port="5432"                       # デフォルトのPostgreSQLポート
        )
        cursor = connection.cursor()
        print("PostgreSQLに接続できました！")
        
        # クエリの実行（例えばバージョン情報の取得）
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"PostgreSQLのバージョン: {db_version}")

        # 接続終了
        cursor.close()
        connection.close()
    except OperationalError as e:
        print(f"エラーが発生しました: {e}")

# 実行
connect_to_postgresql()

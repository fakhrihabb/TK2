import psycopg2
from django.conf import settings

def test_query():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres.cvcodnolmjlcawbfcebn',
            password='KYX-6ri@DN8Q.wc',
            host='aws-0-us-east-1.pooler.supabase.com',
            port='5432',
        )
        cursor = conn.cursor()

        # Contoh query
        query = "SELECT * FROM subkategori_layanan_subkategori;"
        cursor.execute(query)
        results = cursor.fetchall()

        # Cetak hasil
        for row in results:
            print(row)

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_query()

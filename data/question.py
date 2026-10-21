import psycopg2

## Bu değeri localinde çalışırken kendi passwordün yap. Ama kodu pushlarken 'postgres' olarak bırak.
password = '3455'

def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=password
    )

def create_view_completed_orders():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE OR REPLACE VIEW completed_orders AS (
SELECT * FROM proje4.orders
WHERE status='completed'
);
""")
            conn.commit()

def create_view_electronics_products():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""CREATE OR REPLACE VIEW electronics_products AS(
SELECT * FROM proje4.products
WHERE category='Electronics'
);
""")
            conn.commit()

def total_spending_per_customer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""WITH with_total_prices AS(
SELECT c.full_name,
(p.price*o.quantity) AS "total_spending"
FROM proje4.customers AS c
JOIN proje4.orders AS o
ON c.customer_id=o.customer_id
JOIN proje4.products AS p
ON p.product_id=o.product_id
)
SELECT * FROM with_total_prices;
""")
            return cur.fetchall()

def order_details_with_total():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""WITH with_prices AS(
SELECT o.order_id,
c.full_name,
p.product_name,
(p.price*o.quantity) AS "total_price"
FROM proje4.customers AS c
JOIN proje4.orders AS o
ON c.customer_id=o.customer_id
JOIN proje4.products AS p
ON p.product_id=o.product_id
)
SELECT * FROM with_prices;
""")
            return cur.fetchall()

def get_customer_who_bought_most_expensive_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT c.full_name FROM proje4.customers AS c
JOIN proje4.orders AS o
ON c.customer_id=o.customer_id
JOIN proje4.products AS p
ON p.product_id=o.product_id
WHERE p.price=(
SELECT MAX(price) FROM proje4.products
);

""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 2. Sipariş durumlarına göre açıklama
def get_order_status_descriptions():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT order_id,status, 
CASE 
WHEN status='completed' THEN 'Tamamlandı'
WHEN status='cancelled' THEN 'İptal Edildi'
END AS "status_description"
FROM proje4.orders;

""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 3. Ortalama fiyatın üstündeki ürünler
def get_products_above_average_price():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT product_name,price FROM proje4.products
WHERE price>(
SELECT AVG(price)
FROM proje4.products
);
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 4. Müşteri kategorileri
def get_customer_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT full_name,
CASE 
WHEN COUNT(customer_id)>5 THEN 'Sadık Müşteri'
WHEN (5>COUNT(customer_id) AND COUNT(customer_id)>2) THEN 'Orta Seviye'
ELSE 'Yeni Müşteri'
END AS "customer_category"
FROM proje4.customers
GROUP BY full_name;
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 5. Son 30 gün içinde sipariş veren müşteriler
def get_recent_customers():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT full_name FROM proje4.customers
WHERE signup_date=(
SELECT order_date FROM proje4.orders
WHERE order_date BETWEEN '2026-10-21' AND '2026-09-21'
);
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 6. En çok sipariş verilen ürün
def get_most_ordered_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT p.product_name,
MAX(o.quantity) AS "total_orders"
FROM proje4.products AS p
JOIN proje4.orders AS o
ON p.product_id=o.product_id
GROUP BY p.product_name
ORDER BY MAX(o.quantity) DESC
LIMIT 1;
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 7. Ürün fiyatlarına göre etiketleme
def get_product_price_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""SELECT product_name,price,
CASE
WHEN price>1000 THEN 'Pahalı'
WHEN (price>500 AND 1000>price) THEN 'Orta'
ELSE 'Ucuz'
END AS "price_category"
FROM proje4.products;
""")
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
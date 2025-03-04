from applications.lib import PostgresDatabase

def get_data_merk(id):
    db = PostgresDatabase()
    query = """
        SELECT
            merk_id,
            merk_name
        FROM
            ms_merk
        WHERE
            category_id = %(category_id)s
    """
    param = {
        "category_id" : id
    }
    return db.execute(query, param)

def get_data_category():
    db = PostgresDatabase()
    query = """
        SELECT
            category_id,
            category_name
        FROM
            ms_category
    """
    return db.execute(query)

def get_data_outlet():
    db = PostgresDatabase()
    query = """
        SELECT
            outlet_id,
            outlet_name
        FROM
            ms_outlet
    """
    return db.execute(query)

def dt_data_product(search, offset, orderBy):
    db = PostgresDatabase()
    query = f"""
        SELECT
            sku,
            part_number,
            product_name,
            barcode,
            vehicle,
            merk_name,
            category_name,
            outlet_name,
            qty,
            harga_beli,
            harga_jual,
            mp.category_id
        FROM
            ms_product mp
            INNER JOIN ms_merk mm on mm.merk_id = mp.merk_id
            INNER JOIN ms_category mc on mc.category_id = mp.category_id
            INNER JOIN ms_outlet mo on mo.outlet_id = mp.outlet_id
        WHERE
            sku ILIKE %(search)s OR
            part_number ILIKE %(search)s OR
            product_name ILIKE %(search)s OR
            CAST(barcode AS TEXT) ILIKE %(search)s OR
            vehicle ILIKE %(search)s OR
            merk_name ILIKE %(search)s OR
            category_name ILIKE %(search)s OR
            outlet_name ILIKE %(search)s OR
            CAST(harga_beli AS TEXT) ILIKE %(search)s OR
            CAST(harga_jual AS TEXT) ILIKE %(search)s
        ORDER BY
            {orderBy};
    """
    param = {
        "search": f"%{search}%",
        "offset": offset
    }

    return db.execute_dt(query, param)


def update_data_product(data):
    db = PostgresDatabase()
    query = """
        UPDATE 
            ms_product
        SET
            part_number = %(part_number)s,
            product_name = %(product_name)s,
            vehicle = %(vehicle)s,
            merk_id = %(merk_id)s,
            category_id = %(category_id)s,
            outlet_id = %(outlet_id)s,
            qty = %(qty)s,
            harga_beli = %(harga_beli)s,
            harga_jual = %(harga_jual)s,
            barcode = %(barcode)s
        WHERE
            sku = %(sku)s
    """
    param = data

    return db.execute(query, param)

def delete_data_product(id):
    db = PostgresDatabase()
    query = """
        DELETE
        FROM 
            ms_product
        WHERE
            sku = %(sku)s
    """
    param = {
        "sku" : id
    }

    return db.execute(query, param)

def add_data_product(data):
    db = PostgresDatabase()
    query = """
        INSERT INTO 
            ms_product 
                (sku, part_number, product_name, vehicle, merk_id, category_id, outlet_id, qty, harga_beli, harga_jual, barcode) 
        VALUES 
                (%(sku)s, %(part_number)s, %(product_name)s, %(vehicle)s, %(merk_id)s, %(category_id)s, %(outlet_id)s, %(qty)s, %(harga_beli)s, %(harga_jual)s, %(barcode)s);
    """
    param = data

    return db.execute(query, param)

def check_id_product(id):
    db = PostgresDatabase()
    query = """
        SELECT
            sku
        FROM
            ms_product
        WHERE
            sku = %(sku)s
    """
    param = {'sku': id }
    return db.execute(query, param)

from applications.lib import PostgresDatabase
from applications.lib.globalFunc import generate_faktur,to_date,update_faktur
import datetime

def getDataOutlet():
    db = PostgresDatabase()
    query = """
        SELECT 
            outlet_id, 
            outlet_name
        FROM 
            ms_outlet;
    """
    return db.execute(query)

def getDataMember():
    db = PostgresDatabase()
    query = """
        SELECT
            member_id,
            member_name,
            address,
            phone
        FROM 
            ms_member;
    """
    return db.execute(query)

def getPaymentType():
    db = PostgresDatabase()
    query = """
        select * from ms_payment_type
    """
    return db.execute(query)

def getRekening(id=''):
    db = PostgresDatabase()
    param = ''
    if id:
        param = f"AND rek_no = {id}"
    query = f"""
        select rek_no,
            rek_name,
            rek_bank
        from ms_rekening
        where status = true
        {param}
        order by rek_bank;
    """
    return db.execute(query)

def getDataMemberById(id):
    db = PostgresDatabase()
    query = """
        SELECT
            member_id,
            member_name,
            address,
            phone
        FROM 
            ms_member
        WHERE member_id = %(id)s;
    """
    param = { "id" : id }
    return db.execute(query, param)

def getDataLovProduct():
    db = PostgresDatabase()
    query = """
        SELECT
            sku,
            product_name,
            merk_name
        FROM
            ms_product mp
        INNER JOIN ms_merk mm on mm.merk_id = mp.merk_id
    """
    return db.execute(query)

def getDataBySkuBarcode(search):
    db = PostgresDatabase()
    query = """
        SELECT
            sku,
            part_number,
            product_name,
            mp.merk_id,
            merk_name,
            harga_jual,
            harga_beli
        FROM
            ms_product mp
        INNER JOIN ms_merk mm on mm.merk_id = mp.merk_id
        WHERE
            UPPER(sku) = %(search)s OR
            CAST(barcode AS TEXT) =  %(search)s
    """
    param = {
        'search' : search
    }
    return db.execute(query, param)

def dt_data_dashboard(search, offset, orderBy):
    db = PostgresDatabase()
    query = f"""
        SELECT
            faktur,
            to_char(date_tx, 'dd-mm-yyyy') as date_tx,
            COALESCE(mm.member_name,'-') as member_name,
            total_faktur,
            CASE
                WHEN status = false THEN 'Draft'
                ELSE 'Done'
            END as status
        FROM tx_trans
        LEFT JOIN ms_member mm
            ON tx_trans.member_id = mm.member_id
        WHERE (member_name ILIKE %(search)s OR
              faktur ILIKE %(search)s OR
              to_char(date_tx, 'dd-mm-yyyy') ILIKE %(search)s)
              AND status = false
        ORDER BY
            {orderBy}
    """
    param = {
        "search": f"%{search}%",
        "offset": offset,
    }

    return db.execute_dt(query, param)


def update_data_category(data):
    db = PostgresDatabase()
    query = """
        UPDATE 
            ms_category
        SET
            category_name = %(category_name)s
        WHERE
            category_id = %(category_id)s
    """
    param = data

    return db.execute(query, param)

def delete_data_dashboard(faktur):
    try:
        db = PostgresDatabase()
        # Delete tx_trans
        query = """
            DELETE
            FROM 
                tx_trans
            WHERE
                faktur = %(faktur)s
        """
        param = {
            "faktur" : faktur
        }

        hasil = db.execute_preserve(query,param)
        if hasil.is_error:
            return hasil
        
        # Delete tx_trans_detail
        query = """
            DELETE
            FROM 
                tx_trans_detail
            WHERE
                faktur = %(faktur)s
        """
        param = {
            "faktur" : faktur
        }

        hasil = db.execute_preserve(query,param)
        if hasil.is_error:
            return hasil
        
        return db.commit()
    finally:
        db.release_connection()

def add_data_category(data):
    db = PostgresDatabase()
    print(data)
    query = """
        INSERT INTO 
            ms_category 
                (category_name) 
        VALUES 
                (%(category_name)s);
    """
    param = data

    return db.execute(query, param)

def save_order(data,type = 'draft'):
    db = PostgresDatabase()
    now = datetime.datetime.now()
    
    faktur = ''
    if "faktur" not in data:
        date = to_date(data['tanggal'])
        head = f"{data['outletId']}-{date.strftime('%d%m%y')}"
        faktur = generate_faktur(head)
        data['faktur'] = faktur
    else:
        faktur = data['faktur']

    try:
        query = """
            INSERT INTO
                tx_trans (faktur, date_tx, tx_type, due_date, member_id,
                        status, other_fee, other_note, update_date,
                        total_faktur, payment_id, payment_info, time_tx)
            VALUES
                (%(faktur)s, %(date_tx)s, %(tx_type)s, %(due_date)s, %(member_id)s,
                    %(status)s, %(other_fee)s, %(other_note)s, %(update_date)s,
                    %(total_faktur)s, %(payment_id)s, %(payment_info)s, %(time_tx)s)
            ON CONFLICT (faktur)
            DO UPDATE
            SET faktur = excluded.faktur, date_tx = excluded.date_tx, tx_type = excluded.tx_type,
                due_date = excluded.due_date, member_id = excluded.member_id, status = excluded.status,
                other_fee = excluded.other_fee, other_note = excluded.other_note, update_date = excluded.update_date,
                total_faktur = excluded.total_faktur, payment_id = excluded.payment_id,
                payment_info = excluded.payment_info, time_tx = excluded.time_tx;
        """
        param = {
                "faktur": data['faktur'], "date_tx":  data['tanggal'], "tx_type":  data['jenisFaktur'],
                "due_date":  data['jatuhTempo'], "member_id":  data['memberId'], "status":  data['status'],
                "other_fee":  data['ongkir'], "other_note":  data['keterangan'], "update_date":  now.strftime('%Y-%m-%d'),
                "total_faktur":  data['subtotal'], "payment_id":  data['payment_id'], "payment_info":  data['payment_info'],
                "time_tx":  now.strftime('%H:%M:%S')
            }
        hasil = db.execute_preserve(query,param)
        if hasil.is_error:
            return hasil

        # Delete 
        query = """
            DELETE 
            FROM 
                tx_trans_detail 
            WHERE 
                faktur = %(faktur)s
        """
        param = { "faktur": data['faktur']}
        hasil = db.execute_preserve(query,param)
        if hasil.is_error:
            return hasil

        # insert detail
        trans_detail = data['trans_detail']
        for i in trans_detail:
            query = """
                INSERT INTO
                    tx_trans_detail (faktur, sku, part_number, product_name, merk_name, qty, price)
                VALUES
                    (%(faktur)s, %(sku)s, %(part_number)s, %(product_name)s, %(merk_name)s, %(qty)s, %(price)s)
            """
            param = {
                    "faktur": data['faktur'], "sku":  i['sku'], "part_number":  i['part_number'],
                    "product_name":  i['product_name'], "merk_name":  i['merk_name'], "qty":  i['qty'],
                    "price":  i['price']
                }
            hasil = db.execute_preserve(query,param)
            if hasil.is_error:
                return hasil
            
            # Kalau fix dia ngurangin qty nya
            if type == 'invoice':
                hasil = update_qty_product(i['sku'], int(i['qty']), db)
                if hasil.is_error:
                    return hasil
                
        hasil = update_faktur(data['faktur'], db)
        if hasil.is_error:
            return hasil
        
        return db.commit(),faktur
    finally:
        db.release_connection()

def update_qty_product(sku, qty ,conn):
    query = """
        UPDATE ms_product mp
        SET qty = x.qty
        FROM 
            (SELECT qty-%(qty)s qty, sku,outlet_id from ms_product where sku = %(sku)s) x
        WHERE mp.sku = x.sku;
    """
    param = {
            "sku":  sku, 
            "qty":  qty
        }
    hasil = conn.execute_preserve(query,param)
    if hasil.is_error:
        return hasil    
    return hasil

def getTransDraftData(faktur):
    db = PostgresDatabase()
    dataFaktur={}
    query = """
        SELECT
            faktur,
            date_tx,
            tx_type,
            due_date,
            member_id,
            status,
            other_fee,
            other_note,
            update_date,
            total_faktur,
            payment_id,
            payment_info
        FROM
            tx_trans
        WHERE   
            faktur = %(faktur)s;
    """
    param = {
        "faktur": faktur,
    }
    dataFaktur = db.execute(query, param).result[0]

    query = """
        SELECT
            faktur, sku, part_number, product_name, merk_name, qty, price as harga_jual
        FROM
            tx_trans_detail
        WHERE   
            faktur = %(faktur)s;
    """
    param = {
        "faktur": faktur,
    }
    dataFaktur['product'] = db.execute(query, param).result

    return dataFaktur


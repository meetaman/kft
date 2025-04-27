from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
import mysql.connector
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import csv
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'kamal'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/product_master')
def product_master():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM prod_master')
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('product_master.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        hsn_code = request.form['hsn_code']
        type = request.form['type']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prod_master (name, hsn_code, type) VALUES (%s, %s, %s)',
                      (name, hsn_code, type))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product_master'))
    return render_template('add_product.html')

@app.route('/edit_product/<int:prod_id>', methods=['GET', 'POST'])
def edit_product(prod_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        hsn_code = request.form['hsn_code']
        type = request.form['type']
        
        cursor.execute('UPDATE prod_master SET name = %s, hsn_code = %s, type = %s WHERE prod_id = %s',
                      (name, hsn_code, type, prod_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product_master'))
    
    cursor.execute('SELECT * FROM prod_master WHERE prod_id = %s', (prod_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<int:prod_id>')
def delete_product(prod_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prod_master WHERE prod_id = %s', (prod_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product_master'))

@app.route('/party_master')
def party_master():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM party_master')
    parties = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('party_master.html', parties=parties)

@app.route('/add_party', methods=['GET', 'POST'])
def add_party():
    if request.method == 'POST':
        party = request.form['party']
        gstin = request.form['gstin']
        address = request.form['address']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO party_master (party, gstin, address) VALUES (%s, %s, %s)',
                      (party, gstin, address))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Party added successfully!', 'success')
        return redirect(url_for('party_master'))
    return render_template('add_party.html')

@app.route('/edit_party/<int:p_id>', methods=['GET', 'POST'])
def edit_party(p_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        party = request.form['party']
        gstin = request.form['gstin']
        address = request.form['address']
        
        cursor.execute('UPDATE party_master SET party = %s, gstin = %s, address = %s WHERE p_id = %s',
                      (party, gstin, address, p_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Party updated successfully!', 'success')
        return redirect(url_for('party_master'))
    
    cursor.execute('SELECT * FROM party_master WHERE p_id = %s', (p_id,))
    party = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_party.html', party=party)

@app.route('/delete_party/<int:p_id>')
def delete_party(p_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM party_master WHERE p_id = %s', (p_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Party deleted successfully!', 'success')
    return redirect(url_for('party_master'))

@app.route('/incoming_bills')
def incoming_bills():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT ib.*, pm.party 
        FROM incoming_bills ib
        JOIN party_master pm ON ib.party_id = pm.p_id
        ORDER BY ib.s_no DESC
    ''')
    bills = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('incoming_bills.html', bills=bills)

@app.route('/add_incoming_bill', methods=['GET', 'POST'])
def add_incoming_bill():
    if request.method == 'POST':
        try:
            inv_id = request.form['inv_id']
            party_id = request.form['party_id']
            bill_date = request.form['bill_date']
            account_id = request.form.get('account_id')  # Optional field
            
            # Handle TDS values - convert empty strings to None
            tds_percent = request.form.get('tds_percentage')
            tds_percent = float(tds_percent) if tds_percent and tds_percent.strip() else 0
            
            # Handle discount values
            discount_percent = request.form.get('discount_percent')
            discount_percent = float(discount_percent) if discount_percent and discount_percent.strip() else 0
            
            # Get remarks
            remarks = request.form.get('remarks', '').strip()
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Find the first available serial number for incoming_bills
            cursor.execute("""
                SELECT MIN(t1.s_no + 1) as next_id
                FROM incoming_bills t1
                LEFT JOIN incoming_bills t2 ON t1.s_no + 1 = t2.s_no
                WHERE t2.s_no IS NULL
            """)
            result = cursor.fetchone()
            next_serial = result[0] if result[0] is not None else 1
            
            # Calculate total sub-total first to determine discount amount
            items = request.form.getlist('items[]')
            total_sub_total = 0
            for i, product_id in enumerate(items):
                qty = float(request.form.getlist(f'item_{i}[]')[0])
                rate = float(request.form.getlist(f'item_{i}[]')[1])
                total_sub_total += qty * rate

            # Calculate discount amount based on total sub-total
            discount_amount = (total_sub_total * discount_percent) / 100 if discount_percent > 0 else 0
            
            # Insert bill header with the next available serial number
            cursor.execute("""
                INSERT INTO incoming_bills 
                (s_no, inv_id, party_id, bill_date, account_id, tds_percent, tds_amount, 
                discount_percent, discount_amount, remarks, final_amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (next_serial, inv_id, party_id, bill_date, account_id, tds_percent, None,
                  discount_percent, discount_amount, remarks, 0))
            bill_s_no = next_serial
            
            # Insert bill items with sequential item_id
            final_amount = 0
            total_gst = 0
            for i, product_id in enumerate(items):
                # Find the first available item_id for this bill
                cursor.execute("""
                    SELECT MIN(t1.item_id + 1) as next_id
                    FROM bill_items t1
                    LEFT JOIN bill_items t2 ON t1.item_id + 1 = t2.item_id
                    WHERE t2.item_id IS NULL AND t1.bill_s_no = %s
                """, (bill_s_no,))
                result = cursor.fetchone()
                next_item_id = result[0] if result[0] is not None else 1
                
                qty = float(request.form.getlist(f'item_{i}[]')[0])
                rate = float(request.form.getlist(f'item_{i}[]')[1])
                gst = float(request.form.getlist(f'item_{i}[]')[2])
                
                sub_total = qty * rate
                # Apply discount proportionally to this item's sub-total
                item_discount = (sub_total / total_sub_total) * discount_amount if total_sub_total > 0 else 0
                sub_total_after_discount = sub_total - item_discount
                
                gst_amount = (sub_total_after_discount * gst) / 100
                sgst_amount = cgst_amount = gst_amount / 2
                total_amount = sub_total_after_discount + gst_amount
                
                cursor.execute("""
                    INSERT INTO bill_items (item_id, bill_s_no, product_id, qty, rate, sub_total, 
                                          gst_percent, sgst_amount, cgst_amount, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_item_id, bill_s_no, product_id, qty, rate, sub_total, gst, 
                      sgst_amount, cgst_amount, total_amount))
                
                final_amount += total_amount
                total_gst += gst_amount
            
            # Calculate TDS on sub-total after discount
            sub_total_after_discount = total_sub_total - discount_amount
            tds_amount = (sub_total_after_discount * tds_percent / 100) if tds_percent else 0
            
            # Update the final amount and TDS amount
            # Note: Final amount includes GST but not TDS
            cursor.execute("""
                UPDATE incoming_bills 
                SET final_amount = %s, tds_amount = %s
                WHERE s_no = %s
            """, (final_amount, tds_amount, bill_s_no))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Bill added successfully!', 'success')
            return redirect(url_for('incoming_bills'))
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            flash(f'Error adding bill: {str(e)}', 'danger')
            return redirect(url_for('add_incoming_bill'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    parties = cursor.fetchall()
    
    cursor.execute("SELECT a_id, name, type FROM accounts ORDER BY name")
    accounts = cursor.fetchall()
    
    cursor.execute("SELECT prod_id, name, type FROM prod_master ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('add_incoming_bill.html', parties=parties, accounts=accounts, products=products)

@app.route('/view_bill/<int:s_no>')
def view_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get bill details with party and account names
        cursor.execute("""
            SELECT 
                ib.s_no, ib.inv_id, ib.bill_date, 
                p.party as party_name, a.name as account_name,
                ib.final_amount, ib.discount_percent, ib.discount_amount,
                ib.tds_percent, ib.tds_amount, ib.remarks,
                COALESCE((
                    SELECT SUM(bi.sgst_amount + bi.cgst_amount)
                    FROM bill_items bi
                    WHERE bi.bill_s_no = ib.s_no
                ), 0) as total_gst,
                COALESCE((
                    SELECT SUM(amount)
                    FROM payments
                    WHERE payment_type = 'vendor' 
                    AND vendor_id = ib.party_id
                    AND payment_date >= ib.bill_date
                ), 0) as total_payments,
                ib.final_amount - COALESCE((
                    SELECT SUM(amount)
                    FROM payments
                    WHERE payment_type = 'vendor' 
                    AND vendor_id = ib.party_id
                    AND payment_date >= ib.bill_date
                ), 0) as pending_amount
            FROM incoming_bills ib
            LEFT JOIN party_master p ON ib.party_id = p.p_id
            LEFT JOIN accounts a ON ib.account_id = a.a_id
            WHERE ib.s_no = %s
        """, (s_no,))
        bill = cursor.fetchone()
        
        # Get bill items with product names
        cursor.execute("""
            SELECT bi.item_id, bi.qty, bi.rate, bi.sub_total, 
                   bi.gst_percent, bi.sgst_amount, bi.cgst_amount, bi.total_amount,
                   pm.name as product_name
            FROM bill_items bi
            LEFT JOIN prod_master pm ON bi.product_id = pm.prod_id
            WHERE bi.bill_s_no = %s
        """, (s_no,))
        items = cursor.fetchall()
        
        # Get payments related to this party after bill date
        if bill:
            cursor.execute("""
                SELECT 
                    payment_date,
                    payment_mode,
                    amount,
                    narration
                FROM payments
                WHERE payment_type = 'vendor' 
                AND vendor_id = (
                    SELECT party_id FROM incoming_bills WHERE s_no = %s
                )
                AND payment_date >= (
                    SELECT bill_date FROM incoming_bills WHERE s_no = %s
                )
                ORDER BY payment_date
            """, (s_no, s_no))
            payments = cursor.fetchall()
        else:
            payments = []
        
        cursor.close()
        conn.close()
        
        if not bill:
            flash('Bill not found', 'danger')
            return redirect(url_for('incoming_bills'))
            
        return render_template('view_bill.html', bill=bill, items=items, payments=payments)
        
    except Exception as e:
        flash(f'Error viewing bill: {str(e)}', 'danger')
        return redirect(url_for('incoming_bills'))

@app.route('/delete_incoming_bill/<int:s_no>')
def delete_incoming_bill(s_no):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Start transaction
        cursor.execute("START TRANSACTION")
        
        # Delete bill items first (due to foreign key constraint)
        cursor.execute('DELETE FROM bill_items WHERE bill_s_no = %s', (s_no,))
        
        # Delete the bill
        cursor.execute('DELETE FROM incoming_bills WHERE s_no = %s', (s_no,))
        
        # Update serial numbers for incoming_bills
        cursor.execute("SET @counter = 0")
        cursor.execute("""
            UPDATE incoming_bills 
            SET s_no = (@counter := @counter + 1) 
            ORDER BY s_no
        """)
        
        # Reset auto-increment for incoming_bills
        cursor.execute("""
            SELECT MAX(s_no) + 1 FROM incoming_bills
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE incoming_bills AUTO_INCREMENT = {next_auto_increment}")
        
        # Update serial numbers for bill_items
        cursor.execute("""
            SET @counter = 0;
            UPDATE bill_items 
            SET item_id = (@counter := @counter + 1) 
            ORDER BY bill_s_no, item_id
        """)
        
        # Reset auto-increment for bill_items
        cursor.execute("""
            SELECT MAX(item_id) + 1 FROM bill_items
        """)
        next_auto_increment = cursor.fetchone()[0] or 1
        cursor.execute(f"ALTER TABLE bill_items AUTO_INCREMENT = {next_auto_increment}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Bill deleted successfully!', 'success')
        return redirect(url_for('incoming_bills'))
        
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            cursor.close()
            conn.close()
        flash(f'Error deleting bill: {str(e)}', 'danger')
        return redirect(url_for('incoming_bills'))

@app.route('/edit_incoming_bill/<int:s_no>', methods=['GET', 'POST'])
def edit_incoming_bill(s_no):
    if request.method == 'POST':
        try:
            inv_id = request.form['inv_id']
            party_id = request.form['party_id']
            bill_date = request.form['bill_date']
            account_id = request.form.get('account_id')  # Optional field
            
            # Handle TDS values - convert empty strings to None
            tds_percent = request.form.get('tds_percentage')
            tds_percent = float(tds_percent) if tds_percent and tds_percent.strip() else 0
            
            # Handle discount values
            discount_percent = request.form.get('discount_percent')
            discount_percent = float(discount_percent) if discount_percent and discount_percent.strip() else 0
            
            # Get remarks
            remarks = request.form.get('remarks', '').strip()
            
            conn = get_db_connection()
            cursor = conn.cursor()

            # Update bill header
            cursor.execute("""
                UPDATE incoming_bills 
                SET inv_id = %s, party_id = %s, bill_date = %s, 
                    account_id = %s, tds_percent = %s, discount_percent = %s,
                    remarks = %s
                WHERE s_no = %s
            """, (inv_id, party_id, bill_date, account_id, tds_percent, 
                  discount_percent, remarks, s_no))
            
            # Delete existing items
            cursor.execute('DELETE FROM bill_items WHERE bill_s_no = %s', (s_no,))
            
            # Calculate total sub-total first to determine discount amount
            items = request.form.getlist('items[]')
            total_sub_total = 0
            for i, product_id in enumerate(items):
                qty = float(request.form.getlist(f'item_{i}[]')[0])
                rate = float(request.form.getlist(f'item_{i}[]')[1])
                total_sub_total += qty * rate

            # Calculate discount amount based on total sub-total
            discount_amount = (total_sub_total * discount_percent) / 100 if discount_percent > 0 else 0
            
            # Insert bill items with sequential item_id
            final_amount = 0
            total_gst = 0
            for i, product_id in enumerate(items):
                # Find the first available item_id for this bill
                cursor.execute("""
                    SELECT MIN(t1.item_id + 1) as next_id
                    FROM bill_items t1
                    LEFT JOIN bill_items t2 ON t1.item_id + 1 = t2.item_id
                    WHERE t2.item_id IS NULL AND t1.bill_s_no = %s
                """, (s_no,))
                result = cursor.fetchone()
                next_item_id = result[0] if result[0] is not None else 1
                
                qty = float(request.form.getlist(f'item_{i}[]')[0])
                rate = float(request.form.getlist(f'item_{i}[]')[1])
                gst = float(request.form.getlist(f'item_{i}[]')[2])
                
                sub_total = qty * rate
                # Apply discount proportionally to this item's sub-total
                item_discount = (sub_total / total_sub_total) * discount_amount if total_sub_total > 0 else 0
                sub_total_after_discount = sub_total - item_discount
                
                gst_amount = (sub_total_after_discount * gst) / 100
                sgst_amount = cgst_amount = gst_amount / 2
                total_amount = sub_total_after_discount + gst_amount
                
                cursor.execute("""
                    INSERT INTO bill_items (item_id, bill_s_no, product_id, qty, rate, sub_total, 
                                          gst_percent, sgst_amount, cgst_amount, total_amount)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (next_item_id, s_no, product_id, qty, rate, sub_total, gst, 
                      sgst_amount, cgst_amount, total_amount))
                
                final_amount += total_amount
                total_gst += gst_amount
            
            # Calculate TDS on sub-total after discount
            sub_total_after_discount = total_sub_total - discount_amount
            tds_amount = (sub_total_after_discount * tds_percent / 100) if tds_percent else 0
            
            # Update the final amount and TDS amount
            cursor.execute("""
                UPDATE incoming_bills 
                SET final_amount = %s, tds_amount = %s, discount_amount = %s
                WHERE s_no = %s
            """, (final_amount, tds_amount, discount_amount, s_no))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Bill updated successfully!', 'success')
            return redirect(url_for('incoming_bills'))
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                cursor.close()
                conn.close()
            flash(f'Error updating bill: {str(e)}', 'danger')
            return redirect(url_for('edit_incoming_bill', s_no=s_no))
    
    # GET request - show form with existing data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get bill details
    cursor.execute("""
        SELECT * FROM incoming_bills 
        WHERE s_no = %s
    """, (s_no,))
    bill = cursor.fetchone()
    
    if not bill:
        flash('Bill not found', 'danger')
        return redirect(url_for('incoming_bills'))
    
    # Get bill items
    cursor.execute("""
        SELECT * FROM bill_items 
        WHERE bill_s_no = %s
        ORDER BY item_id
    """, (s_no,))
    items = cursor.fetchall()
    
    # Get dropdown data
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    parties = cursor.fetchall()
    
    cursor.execute("SELECT a_id, name, type FROM accounts ORDER BY name")
    accounts = cursor.fetchall()
    
    cursor.execute("SELECT prod_id, name, type FROM prod_master ORDER BY name")
    products = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_incoming_bill.html', 
                         bill=bill, 
                         items=items,
                         parties=parties, 
                         accounts=accounts, 
                         products=products)

@app.route('/accounts')
def accounts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM accounts')
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('accounts.html', accounts=accounts)

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        name = request.form['name']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO accounts (name) VALUES (%s)', (name,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account added successfully!', 'success')
        return redirect(url_for('accounts'))
    return render_template('add_account.html')

@app.route('/edit_account/<int:a_id>', methods=['GET', 'POST'])
def edit_account(a_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form['name']
        
        cursor.execute('UPDATE accounts SET name = %s WHERE a_id = %s',
                      (name, a_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('accounts'))
    
    cursor.execute('SELECT * FROM accounts WHERE a_id = %s', (a_id,))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('edit_account.html', account=account)

@app.route('/delete_account/<int:a_id>')
def delete_account(a_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM accounts WHERE a_id = %s', (a_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Account deleted successfully!', 'success')
    return redirect(url_for('accounts'))

@app.route('/party_ledger')
def party_ledger():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all parties
        cursor.execute("""
            SELECT p.p_id, p.party, 
                   COUNT(ib.s_no) as total_bills,
                   COALESCE(SUM(ib.final_amount), 0) as total_amount
            FROM party_master p
            LEFT JOIN incoming_bills ib ON p.p_id = ib.party_id
            GROUP BY p.p_id, p.party
            ORDER BY p.party
        """)
        parties = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('party_ledger.html', parties=parties)
        
    except Exception as e:
        flash(f'Error loading party ledger: {str(e)}', 'danger')
        return redirect(url_for('party_ledger'))

@app.route('/party_ledger/<int:party_id>')
def view_party_ledger(party_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get party details
        cursor.execute("""
            SELECT p.p_id, p.party
            FROM party_master p
            WHERE p.p_id = %s
        """, (party_id,))
        party = cursor.fetchone()
        
        if not party:
            flash('Party not found', 'danger')
            return redirect(url_for('party_ledger'))
        
        # Get all transactions for this party with running balance
        # Note: For incoming bills (purchases), we OWE money to the party (negative balance)
        # For outgoing bills (sales), the party OWES money to us (positive balance)
        # For payments made to vendor, it REDUCES our liability (positive balance)
        cursor.execute("""
            WITH all_transactions AS (
                -- Incoming Bills (Purchases) - Negative balance as we owe money
                SELECT 
                    ib.bill_date as transaction_date,
                    ib.inv_id as reference_no,
                    'Purchase' as transaction_type,
                    -ib.final_amount as amount,  -- Negative for purchases
                    NULL as payment_mode,
                    ib.remarks as narration,
                    ib.s_no  -- Added s_no for bill linking
                FROM incoming_bills ib
                WHERE ib.party_id = %s

                UNION ALL

                -- Outgoing Bills (Sales) - Positive balance as they owe us money
                SELECT 
                    ob.bill_date as transaction_date,
                    ob.bill_no as reference_no,
                    'Sale' as transaction_type,
                    ob.final_amount as amount,  -- Positive for sales
                    NULL as payment_mode,
                    NULL as narration,
                    ob.s_no  -- Added s_no for bill linking
                FROM outgoing_bills ob
                WHERE ob.party_id = %s

                UNION ALL

                -- Payments - Positive for payments made (reduces our liability)
                SELECT 
                    p.payment_date as transaction_date,
                    p.payment_id as reference_no,
                    'Payment' as transaction_type,
                    p.amount as amount,  -- Positive for payments made
                    p.payment_mode,
                    p.narration,
                    NULL as s_no  -- Added NULL s_no for consistency
                FROM payments p
                WHERE p.payment_type = 'vendor' AND p.vendor_id = %s
            )
            SELECT 
                *,
                @running_balance := @running_balance + amount as running_balance
            FROM all_transactions
            CROSS JOIN (SELECT @running_balance := 0) r
            ORDER BY transaction_date, transaction_type
        """, (party_id, party_id, party_id))
        transactions = cursor.fetchall()
        
        # Get summary statistics
        cursor.execute("""
            SELECT 
                -- Purchase Summary
                COUNT(CASE WHEN type = 'Purchase' THEN 1 END) as total_purchases,
                ABS(COALESCE(SUM(CASE WHEN type = 'Purchase' THEN amount END), 0)) as total_purchase_amount,
                
                -- Sales Summary
                COUNT(CASE WHEN type = 'Sale' THEN 1 END) as total_sales,
                COALESCE(SUM(CASE WHEN type = 'Sale' THEN amount END), 0) as total_sales_amount,
                
                -- Payment Summary
                COUNT(CASE WHEN type = 'Payment' THEN 1 END) as total_payments,
                COALESCE(SUM(CASE WHEN type = 'Payment' THEN amount END), 0) as total_payment_amount,
                
                -- Overall Balance
                COALESCE(SUM(amount), 0) as net_balance
            FROM (
                -- Purchases
                SELECT 'Purchase' as type, -ib.final_amount as amount
                FROM incoming_bills ib
                WHERE ib.party_id = %s
                
                UNION ALL
                
                -- Sales
                SELECT 'Sale' as type, ob.final_amount as amount
                FROM outgoing_bills ob
                WHERE ob.party_id = %s
                
                UNION ALL
                
                -- Payments
                SELECT 'Payment' as type, p.amount as amount
                FROM payments p
                WHERE p.payment_type = 'vendor' AND p.vendor_id = %s
            ) all_transactions
        """, (party_id, party_id, party_id))
        summary = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return render_template('view_party_ledger.html', 
                             party=party, 
                             transactions=transactions,
                             summary=summary)
        
    except Exception as e:
        flash(f'Error generating party-wise report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/product_wise')
def product_wise_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get product ID from query parameters
        product_id = request.args.get('product_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not product_id:
            # Show product selection if no product selected
            cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
            products = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template('product_wise_report.html', products=products)
        
        # Get product details
        cursor.execute("SELECT name FROM prod_master WHERE prod_id = %s", (product_id,))
        product = cursor.fetchone()
        
        # Base conditions for date filtering
        date_conditions = []
        params = []
        if start_date:
            date_conditions.append(" AND bill_date >= %s")
            params.append(start_date)
        if end_date:
            date_conditions.append(" AND bill_date <= %s")
            params.append(end_date)
        
        date_filter = ''.join(date_conditions)
        
        # Get purchase summary
        purchase_query = f"""
            SELECT 
                COUNT(DISTINCT ib.s_no) as total_bills,
                COALESCE(SUM(bi.qty), 0) as total_qty,
                COALESCE(SUM(bi.sub_total), 0) as total_amount,
                COALESCE(SUM(bi.sgst_amount + bi.cgst_amount), 0) as total_gst,
                COALESCE(SUM(bi.total_amount), 0) as total_with_gst
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            WHERE bi.product_id = %s {date_filter}
        """
        cursor.execute(purchase_query, [product_id] + params)
        purchase_summary = cursor.fetchone()
        
        # Get sales summary
        sales_query = f"""
            SELECT 
                COUNT(DISTINCT ob.s_no) as total_bills,
                COALESCE(SUM(obi.qty), 0) as total_qty,
                COALESCE(SUM(obi.sub_total), 0) as total_amount,
                COALESCE(SUM(obi.sgst_amount + obi.cgst_amount), 0) as total_gst,
                COALESCE(SUM(obi.total_amount), 0) as total_with_gst
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            WHERE obi.product_id = %s {date_filter}
        """
        cursor.execute(sales_query, [product_id] + params)
        sales_summary = cursor.fetchone()
        
        # Get incoming bills
        query = """
            SELECT 
                'Purchase' as type,
                ib.bill_date,
                ib.inv_id as bill_no,
                p.party as party_name,
                bi.qty,
                bi.rate,
                bi.sub_total,
                bi.gst_percent,
                bi.sgst_amount,
                bi.cgst_amount,
                bi.total_amount
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN party_master p ON ib.party_id = p.p_id
            WHERE bi.product_id = %s
        """
        params = [product_id]
        
        if start_date:
            query += " AND ib.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ib.bill_date <= %s"
            params.append(end_date)
            
        # Get outgoing bills
        query += """
            UNION ALL
            SELECT 
                'Sale' as type,
                ob.bill_date,
                ob.bill_no,
                p.party as party_name,
                obi.qty,
                obi.rate,
                obi.sub_total,
                obi.gst_percent,
                obi.sgst_amount,
                obi.cgst_amount,
                obi.total_amount
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE obi.product_id = %s
        """
        params.append(product_id)
        
        if start_date:
            query += " AND ob.bill_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND ob.bill_date <= %s"
            params.append(end_date)
            
        query += " ORDER BY bill_date DESC"
        
        cursor.execute(query, params)
        transactions = cursor.fetchall()
        
        # Get products for filter
        cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('product_wise_report.html',
                             product=product,
                             products=products,
                             transactions=transactions,
                             product_id=product_id,
                             start_date=start_date,
                             end_date=end_date,
                             purchase_summary=purchase_summary,
                             sales_summary=sales_summary)
        
    except Exception as e:
        flash(f'Error generating product-wise report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/gst')
def gst_report():
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        party_id = request.args.get('party_id')
        gst_percent = request.args.get('gst_percent')

        # Build base query conditions
        conditions = []
        params = []

        if start_date:
            conditions.append("b.bill_date >= %s")
            params.append(start_date)
        if end_date:
            conditions.append("b.bill_date <= %s")
            params.append(end_date)
        if party_id:
            conditions.append("b.party_id = %s")
            params.append(party_id)
        if gst_percent:
            conditions.append("i.gst_percent = %s")
            params.append(float(gst_percent))

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get database connection
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get parties for dropdown
        cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
        parties = cursor.fetchall()

        # Get input GST summary (purchases)
        cursor.execute(f"""
            SELECT 
                COUNT(DISTINCT b.inv_id) as total_bills,
                COALESCE(SUM(i.total_amount), 0) as total_amount,
                COALESCE(SUM(i.sgst_amount + i.cgst_amount), 0) as total_gst
            FROM incoming_bills b
            JOIN bill_items i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
        """, params)
        input_summary = cursor.fetchone()

        # Get output GST summary (sales)
        cursor.execute(f"""
            SELECT 
                COUNT(DISTINCT b.bill_no) as total_bills,
                COALESCE(SUM(i.total_amount), 0) as total_amount,
                COALESCE(SUM(i.sgst_amount + i.cgst_amount), 0) as total_gst
            FROM outgoing_bills b
            JOIN outgoing_bill_items i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
        """, params)
        output_summary = cursor.fetchone()

        # Calculate net amounts
        net_amount = (input_summary['total_amount'] or 0) - (output_summary['total_amount'] or 0)
        net_gst = (input_summary['total_gst'] or 0) - (output_summary['total_gst'] or 0)

        # Get GST rate-wise summary
        cursor.execute(f"""
            SELECT 
                i.gst_percent,
                COALESCE(SUM(CASE WHEN b.type = 'Purchase' THEN i.total_amount ELSE 0 END), 0) as input_amount,
                COALESCE(SUM(CASE WHEN b.type = 'Purchase' THEN (i.sgst_amount + i.cgst_amount) ELSE 0 END), 0) as input_gst,
                COALESCE(SUM(CASE WHEN b.type = 'Sale' THEN i.total_amount ELSE 0 END), 0) as output_amount,
                COALESCE(SUM(CASE WHEN b.type = 'Sale' THEN (i.sgst_amount + i.cgst_amount) ELSE 0 END), 0) as output_gst
            FROM (
                SELECT s_no, inv_id as bill_no, bill_date, party_id, 'Purchase' as type FROM incoming_bills
                UNION ALL
                SELECT s_no, bill_no, bill_date, party_id, 'Sale' as type FROM outgoing_bills
            ) b
            JOIN (
                SELECT bill_s_no, gst_percent, total_amount, sgst_amount, cgst_amount FROM bill_items
                UNION ALL
                SELECT bill_s_no, gst_percent, total_amount, sgst_amount, cgst_amount FROM outgoing_bill_items
            ) i ON b.s_no = i.bill_s_no
            WHERE {where_clause}
            GROUP BY i.gst_percent
            ORDER BY i.gst_percent
        """, params)
        gst_rates = cursor.fetchall()

        # Calculate net amounts for each rate
        for rate in gst_rates:
            rate['net_amount'] = (rate['input_amount'] or 0) - (rate['output_amount'] or 0)
            rate['net_gst'] = (rate['input_gst'] or 0) - (rate['output_gst'] or 0)

        # Get transaction details
        cursor.execute(f"""
            SELECT 
                b.bill_date,
                b.bill_no,
                b.type,
                p.party as party_name,
                pm.name as product_name,
                COALESCE(i.qty, 0) as qty,
                COALESCE(i.rate, 0) as rate,
                COALESCE(i.sub_total, 0) as sub_total,
                COALESCE(i.gst_percent, 0) as gst_percent,
                COALESCE(i.sgst_amount, 0) as sgst_amount,
                COALESCE(i.cgst_amount, 0) as cgst_amount,
                COALESCE(i.total_amount, 0) as total_amount
            FROM (
                SELECT s_no, inv_id as bill_no, bill_date, party_id, 'Purchase' as type FROM incoming_bills
                UNION ALL
                SELECT s_no, bill_no, bill_date, party_id, 'Sale' as type FROM outgoing_bills
            ) b
            JOIN (
                SELECT bill_s_no, product_id, qty, rate, sub_total, gst_percent, sgst_amount, cgst_amount, total_amount 
                FROM bill_items
                UNION ALL
                SELECT bill_s_no, product_id, qty, rate, sub_total, gst_percent, sgst_amount, cgst_amount, total_amount 
                FROM outgoing_bill_items
            ) i ON b.s_no = i.bill_s_no
            LEFT JOIN party_master p ON b.party_id = p.p_id
            LEFT JOIN prod_master pm ON i.product_id = pm.prod_id
            WHERE {where_clause}
            ORDER BY b.bill_date DESC, b.bill_no DESC
        """, params)
        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('gst_report.html',
                             start_date=start_date,
                             end_date=end_date,
                             party_id=party_id,
                             gst_percent=gst_percent,
                             parties=parties,
                             input_summary=input_summary,
                             output_summary=output_summary,
                             net_amount=net_amount,
                             net_gst=net_gst,
                             gst_rates=gst_rates,
                             transactions=transactions)

    except Exception as e:
        flash(f'Error generating GST report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/price_analysis')
def price_analysis():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get product ID from query parameters
        product_id = request.args.get('product_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Get all products for dropdown
        cursor.execute("SELECT prod_id, name FROM prod_master ORDER BY name")
        products = cursor.fetchall()
        
        if product_id:
            # Base query conditions
            conditions = ["bi.product_id = %s"]
            params = [product_id]
            
            if start_date:
                conditions.append("ib.bill_date >= %s")
                params.append(start_date)
            if end_date:
                conditions.append("ib.bill_date <= %s")
                params.append(end_date)
            
            where_clause = " AND ".join(conditions)
            
            # Get purchase price data with COALESCE
            cursor.execute(f"""
                SELECT 
                    ib.bill_date,
                    p.party as party_name,
                    CAST(COALESCE(bi.rate, 0) AS FLOAT) as price,
                    CAST(COALESCE(bi.qty, 0) AS FLOAT) as qty,
                    pm.name as product_name
                FROM incoming_bills ib
                JOIN bill_items bi ON ib.s_no = bi.bill_s_no
                JOIN party_master p ON ib.party_id = p.p_id
                JOIN prod_master pm ON bi.product_id = pm.prod_id
                WHERE {where_clause}
                ORDER BY ib.bill_date
            """, params)
            purchase_data = cursor.fetchall()
            
            # Get sale price data with COALESCE
            cursor.execute(f"""
                SELECT 
                    ob.bill_date,
                    p.party as party_name,
                    CAST(COALESCE(obi.rate, 0) AS FLOAT) as price,
                    CAST(COALESCE(obi.qty, 0) AS FLOAT) as qty,
                    pm.name as product_name
                FROM outgoing_bills ob
                JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
                JOIN party_master p ON ob.party_id = p.p_id
                JOIN prod_master pm ON obi.product_id = pm.prod_id
                WHERE {where_clause.replace('bi.', 'obi.')}
                ORDER BY ob.bill_date
            """, params)
            sale_data = cursor.fetchall()
            
            # Get price statistics with COALESCE
            cursor.execute(f"""
                SELECT 
                    'Purchase' as type,
                    CAST(COALESCE(MIN(NULLIF(bi.rate, 0)), 0) AS FLOAT) as min_price,
                    CAST(COALESCE(MAX(bi.rate), 0) AS FLOAT) as max_price,
                    CAST(COALESCE(AVG(NULLIF(bi.rate, 0)), 0) AS FLOAT) as avg_price,
                    COUNT(DISTINCT p.p_id) as unique_parties
                FROM incoming_bills ib
                JOIN bill_items bi ON ib.s_no = bi.bill_s_no
                JOIN party_master p ON ib.party_id = p.p_id
                WHERE {where_clause}
                
                UNION ALL
                
                SELECT 
                    'Sale' as type,
                    CAST(COALESCE(MIN(NULLIF(obi.rate, 0)), 0) AS FLOAT) as min_price,
                    CAST(COALESCE(MAX(obi.rate), 0) AS FLOAT) as max_price,
                    CAST(COALESCE(AVG(NULLIF(obi.rate, 0)), 0) AS FLOAT) as avg_price,
                    COUNT(DISTINCT p.p_id) as unique_parties
                FROM outgoing_bills ob
                JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
                JOIN party_master p ON ob.party_id = p.p_id
                WHERE {where_clause.replace('bi.', 'obi.')}
            """, params * 2)
            price_stats = cursor.fetchall()
            
            # Get party-wise average prices with COALESCE
            cursor.execute(f"""
                SELECT 
                    p.party as party_name,
                    'Purchase' as type,
                    CAST(COALESCE(MIN(NULLIF(bi.rate, 0)), 0) AS FLOAT) as min_price,
                    CAST(COALESCE(MAX(bi.rate), 0) AS FLOAT) as max_price,
                    CAST(COALESCE(AVG(NULLIF(bi.rate, 0)), 0) AS FLOAT) as avg_price,
                    COUNT(*) as transaction_count,
                    CAST(COALESCE(SUM(bi.qty), 0) AS FLOAT) as total_qty
                FROM incoming_bills ib
                JOIN bill_items bi ON ib.s_no = bi.bill_s_no
                JOIN party_master p ON ib.party_id = p.p_id
                WHERE {where_clause}
                GROUP BY p.party
                
                UNION ALL
                
                SELECT 
                    p.party as party_name,
                    'Sale' as type,
                    CAST(COALESCE(MIN(NULLIF(obi.rate, 0)), 0) AS FLOAT) as min_price,
                    CAST(COALESCE(MAX(obi.rate), 0) AS FLOAT) as max_price,
                    CAST(COALESCE(AVG(NULLIF(obi.rate, 0)), 0) AS FLOAT) as avg_price,
                    COUNT(*) as transaction_count,
                    CAST(COALESCE(SUM(obi.qty), 0) AS FLOAT) as total_qty
                FROM outgoing_bills ob
                JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
                JOIN party_master p ON ob.party_id = p.p_id
                WHERE {where_clause.replace('bi.', 'obi.')}
                GROUP BY p.party
                ORDER BY type, avg_price DESC
            """, params * 2)
            party_stats = cursor.fetchall()
        else:
            purchase_data = []
            sale_data = []
            price_stats = []
            party_stats = []
        
        cursor.close()
        conn.close()
        
        return render_template('price_analysis.html',
                             products=products,
                             product_id=product_id,
                             start_date=start_date,
                             end_date=end_date,
                             purchase_data=purchase_data,
                             sale_data=sale_data,
                             price_stats=price_stats,
                             party_stats=party_stats)
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        flash(f'Error generating price analysis: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/gstr3b')
def gstr3b_report():
    try:
        # Get filter parameters
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        # Convert month to date range
        start_date = f"{month}-01"
        end_date = (datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(months=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 3.1 Details of Outward Supplies and inward supplies liable to reverse charge
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    THEN obi.total_amount - (obi.sgst_amount + obi.cgst_amount)
                    ELSE 0 
                END), 0) as registered_taxable_value,
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    AND LEFT(p.gstin, 2) != '27'  -- Inter-state: different state code
                    THEN obi.sgst_amount + obi.cgst_amount
                    ELSE 0 
                END), 0) as registered_igst,
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    AND LEFT(p.gstin, 2) = '27'  -- Intra-state: same state code (27 for Maharashtra)
                    THEN obi.cgst_amount
                    ELSE 0 
                END), 0) as registered_cgst,
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    AND LEFT(p.gstin, 2) = '27'  -- Intra-state: same state code (27 for Maharashtra)
                    THEN obi.sgst_amount
                    ELSE 0 
                END), 0) as registered_sgst,
                COALESCE(SUM(CASE 
                    WHEN NOT p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    OR p.gstin IS NULL
                    THEN obi.total_amount - (obi.sgst_amount + obi.cgst_amount)
                    ELSE 0 
                END), 0) as unregistered_taxable_value,
                COALESCE(SUM(CASE 
                    WHEN (NOT p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' OR p.gstin IS NULL)
                    THEN obi.sgst_amount + obi.cgst_amount  -- For unregistered, treat all as IGST
                    ELSE 0 
                END), 0) as unregistered_igst
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE ob.bill_date BETWEEN %s AND %s
        """, (start_date, end_date))
        outward_supplies = cursor.fetchone()
        
        # 4. Eligible ITC
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) != '27'  -- Inter-state: different state code
                    THEN bi.sgst_amount + bi.cgst_amount
                    ELSE 0 
                END), 0) as total_igst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state: same state code
                    THEN bi.cgst_amount
                    ELSE 0 
                END), 0) as total_cgst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state: same state code
                    THEN bi.sgst_amount
                    ELSE 0 
                END), 0) as total_sgst
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN party_master p ON ib.party_id = p.p_id
            WHERE ib.bill_date BETWEEN %s AND %s
            AND p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        """, (start_date, end_date))
        eligible_itc = cursor.fetchone()
        
        # 5. Values of exempt, nil-rated and non-GST inward supplies
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN bi.gst_percent = 0 THEN bi.total_amount ELSE 0 END), 0) as exempt_supplies,
                COALESCE(SUM(CASE WHEN bi.gst_percent > 0 THEN bi.total_amount ELSE 0 END), 0) as taxable_supplies
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            WHERE ib.bill_date BETWEEN %s AND %s
        """, (start_date, end_date))
        exempt_supplies = cursor.fetchone()
        
        # 6.1 Payment of tax
        cursor.execute("""
            SELECT 
                COALESCE(SUM(bi.sgst_amount), 0) as total_sgst,
                COALESCE(SUM(bi.cgst_amount), 0) as total_cgst,
                COALESCE(SUM(bi.total_amount), 0) as total_amount
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            WHERE ib.bill_date BETWEEN %s AND %s
        """, (start_date, end_date))
        tax_payment = cursor.fetchone()
        
        # 6.2 TDS/TCS Credit
        cursor.execute("""
            SELECT 
                COALESCE(SUM(tds_amount), 0) as total_tds
            FROM incoming_bills
            WHERE bill_date BETWEEN %s AND %s
            AND tds_amount > 0
        """, (start_date, end_date))
        tds_credit = cursor.fetchone()
        
        # Get HSN summary with correct tax split
        cursor.execute("""
            SELECT 
                pm.hsn_code,
                pm.name as product_name,
                COALESCE(SUM(obi.qty), 0) as total_quantity,
                COALESCE(SUM(obi.total_amount - (obi.sgst_amount + obi.cgst_amount)), 0) as total_value,
                obi.gst_percent,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) != '27'  -- Inter-state
                    THEN obi.sgst_amount + obi.cgst_amount
                    ELSE 0 
                END), 0) as total_igst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state
                    THEN obi.cgst_amount
                    ELSE 0 
                END), 0) as total_cgst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state
                    THEN obi.sgst_amount
                    ELSE 0 
                END), 0) as total_sgst
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN prod_master pm ON obi.product_id = pm.prod_id
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE ob.bill_date BETWEEN %s AND %s
            GROUP BY pm.hsn_code, pm.name, obi.gst_percent
            ORDER BY pm.hsn_code, obi.gst_percent
        """, (start_date, end_date))
        hsn_summary = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('gstr3b.html',
                             month=month,
                             outward_supplies=outward_supplies,
                             eligible_itc=eligible_itc,
                             exempt_supplies=exempt_supplies,
                             tax_payment=tax_payment,
                             tds_credit=tds_credit,
                             hsn_summary=hsn_summary)
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        flash(f'Error generating GSTR-3B report: {str(e)}', 'danger')
        return redirect(url_for('reports'))

@app.route('/reports/gstr3b/download')
def download_gstr3b_report():
    try:
        # Get filter parameters
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        # Convert month to date range
        start_date = f"{month}-01"
        end_date = (datetime.strptime(start_date, '%Y-%m-%d') + relativedelta(months=1) - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['GSTR-3B Report', ''])
        writer.writerow(['Period:', month])
        writer.writerow([])
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 3.1 Outward Supplies
        writer.writerow(['3.1 Details of Outward Supplies and inward supplies liable to reverse charge'])
        writer.writerow(['Nature of Supplies', 'Total Taxable Value', 'Integrated Tax'])
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    THEN obi.total_amount 
                    ELSE 0 
                END), 0) as registered_sales,
                COALESCE(SUM(CASE 
                    WHEN p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    THEN obi.sgst_amount + obi.cgst_amount
                    ELSE 0 
                END), 0) as registered_gst,
                COALESCE(SUM(CASE 
                    WHEN NOT p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    OR p.gstin IS NULL
                    THEN obi.total_amount 
                    ELSE 0 
                END), 0) as unregistered_sales,
                COALESCE(SUM(CASE 
                    WHEN NOT p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' 
                    OR p.gstin IS NULL
                    THEN obi.sgst_amount + obi.cgst_amount
                    ELSE 0 
                END), 0) as unregistered_gst
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE ob.bill_date BETWEEN %s AND %s
        """, (start_date, end_date))
        outward_supplies = cursor.fetchone()
        
        writer.writerow(['(a) Outward taxable supplies (other than zero rated, nil rated and exempted)',
                        f"{outward_supplies['registered_sales']:.2f}",
                        f"{outward_supplies['registered_gst']:.2f}"])
        writer.writerow(['(b) Outward taxable supplies (zero rated)', '0.00', '0.00'])
        writer.writerow(['(c) Other outward supplies (Nil rated, exempted)',
                        f"{outward_supplies['unregistered_sales']:.2f}",
                        f"{outward_supplies['unregistered_gst']:.2f}"])
        writer.writerow([])
        
        # 3.2 Inter-State Supplies
        writer.writerow(['3.2 Details of inter-State supplies made to unregistered persons'])
        writer.writerow(['Rate', 'Taxable Value', 'Integrated Tax'])
        
        cursor.execute("""
            SELECT 
                obi.gst_percent,
                COALESCE(SUM(obi.total_amount), 0) as taxable_value,
                COALESCE(SUM(obi.sgst_amount + obi.cgst_amount), 0) as gst_amount
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE ob.bill_date BETWEEN %s AND %s
            AND (NOT p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$' OR p.gstin IS NULL)
            GROUP BY obi.gst_percent
            ORDER BY obi.gst_percent
        """, (start_date, end_date))
        unregistered_supplies = cursor.fetchall()
        
        for supply in unregistered_supplies:
            writer.writerow([f"{supply['gst_percent']}%",
                           f"{supply['taxable_value']:.2f}",
                           f"{supply['gst_amount']:.2f}"])
        writer.writerow([])
        
        # 4. Eligible ITC
        writer.writerow(['4. Eligible ITC'])
        writer.writerow(['Details', 'Integrated Tax', 'Central Tax', 'State/UT Tax'])
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(bi.total_amount), 0) as total_itc,
                COALESCE(SUM(bi.sgst_amount), 0) as total_sgst_itc,
                COALESCE(SUM(bi.cgst_amount), 0) as total_cgst_itc
            FROM incoming_bills ib
            JOIN bill_items bi ON ib.s_no = bi.bill_s_no
            JOIN party_master p ON ib.party_id = p.p_id
            WHERE ib.bill_date BETWEEN %s AND %s
            AND p.gstin REGEXP '^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
        """, (start_date, end_date))
        eligible_itc = cursor.fetchone()
        
        writer.writerow(['(A) ITC Available (whether in full or part)',
                        f"{eligible_itc['total_itc']:.2f}",
                        f"{eligible_itc['total_cgst_itc']:.2f}",
                        f"{eligible_itc['total_sgst_itc']:.2f}"])
        writer.writerow([])
        
        # HSN Summary
        writer.writerow(['HSN-wise Summary of Outward Supplies'])
        writer.writerow(['HSN', 'Description', 'Total Quantity', 'Total Value', 'Rate', 'Tax Amount'])
        
        cursor.execute("""
            SELECT 
                pm.hsn_code,
                pm.name as product_name,
                COALESCE(SUM(obi.qty), 0) as total_quantity,
                COALESCE(SUM(obi.total_amount - (obi.sgst_amount + obi.cgst_amount)), 0) as total_value,
                obi.gst_percent,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) != '27'  -- Inter-state
                    THEN obi.sgst_amount + obi.cgst_amount
                    ELSE 0 
                END), 0) as total_igst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state
                    THEN obi.cgst_amount
                    ELSE 0 
                END), 0) as total_cgst,
                COALESCE(SUM(CASE 
                    WHEN LEFT(p.gstin, 2) = '27'  -- Intra-state
                    THEN obi.sgst_amount
                    ELSE 0 
                END), 0) as total_sgst
            FROM outgoing_bills ob
            JOIN outgoing_bill_items obi ON ob.s_no = obi.bill_s_no
            JOIN prod_master pm ON obi.product_id = pm.prod_id
            JOIN party_master p ON ob.party_id = p.p_id
            WHERE ob.bill_date BETWEEN %s AND %s
            GROUP BY pm.hsn_code, pm.name, obi.gst_percent
            ORDER BY pm.hsn_code, obi.gst_percent
        """, (start_date, end_date))
        hsn_summary = cursor.fetchall()
        
        for item in hsn_summary:
            writer.writerow([item['hsn_code'],
                           item['product_name'],
                           f"{item['total_quantity']:.2f}",
                           f"{item['total_value']:.2f}",
                           f"{item['gst_percent']}%",
                           f"{item['total_igst']:.2f}",
                           f"{item['total_cgst']:.2f}",
                           f"{item['total_sgst']:.2f}"])
        
        cursor.close()
        conn.close()
        
        # Prepare the response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=GSTR3B_{month}.csv',
                'Content-Type': 'text/csv'
            }
        )
        
    except Exception as e:
        if 'conn' in locals():
            conn.close()
        flash(f'Error downloading GSTR-3B report: {str(e)}', 'danger')
        return redirect(url_for('gstr3b_report'))

@app.route('/get_party_bills/<int:party_id>')
def get_party_bills(party_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all unpaid/partially paid bills for the party
        cursor.execute("""
            SELECT 
                ib.s_no,
                ib.inv_id,
                ib.bill_date,
                ib.final_amount,
                COALESCE(ib.paid_amount, 0) as paid_amount,
                (ib.final_amount - COALESCE(ib.paid_amount, 0)) as pending_amount
            FROM incoming_bills ib
            WHERE ib.party_id = %s
            AND (ib.final_amount > COALESCE(ib.paid_amount, 0))
            ORDER BY ib.bill_date
        """, (party_id,))
        bills = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify(bills)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Payment Routes
@app.route('/record_payment', methods=['GET', 'POST'])
def record_payment():
    if request.method == 'POST':
        try:
            payment_type = request.form['payment_type']
            payment_date = request.form['payment_date']
            payment_mode = request.form['payment_mode']
            amount = float(request.form['amount'])
            narration = request.form.get('narration', '')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if payment_type == 'vendor':
                vendor_id = request.form['vendor_id']
                cursor.execute("""
                    INSERT INTO payments 
                    (payment_date, payment_type, vendor_id, payment_mode, amount, narration)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (payment_date, payment_type, vendor_id, payment_mode, amount, narration))
            else:  # misc payment
                payment_for = request.form['payment_for']
                cursor.execute("""
                    INSERT INTO payments 
                    (payment_date, payment_type, payment_for, payment_mode, amount, narration)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (payment_date, payment_type, payment_for, payment_mode, amount, narration))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Payment recorded successfully!', 'success')
            return redirect(url_for('view_payments'))
            
        except Exception as e:
            flash(f'Error recording payment: {str(e)}', 'danger')
            return redirect(url_for('record_payment'))
    
    # GET request - show form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    vendors = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('record_payment.html', vendors=vendors)

@app.route('/view_payments')
def view_payments():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                p.*,
                pm.party as vendor_name
            FROM payments p
            LEFT JOIN party_master pm ON p.vendor_id = pm.p_id
            ORDER BY p.payment_date DESC, p.payment_id DESC
        """)
        payments = cursor.fetchall()
        
        # Calculate total amount
        total_amount = sum(payment['amount'] for payment in payments)
        
        cursor.close()
        conn.close()
        
        return render_template('view_payments.html', payments=payments, total_amount=total_amount)
        
    except Exception as e:
        flash(f'Error fetching payments: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/edit_payment/<int:payment_id>', methods=['GET', 'POST'])
def edit_payment(payment_id):
    if request.method == 'POST':
        try:
            payment_type = request.form['payment_type']
            payment_date = request.form['payment_date']
            payment_mode = request.form['payment_mode']
            amount = float(request.form['amount'])
            narration = request.form.get('narration', '')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if payment_type == 'vendor':
                vendor_id = request.form['vendor_id']
                cursor.execute("""
                    UPDATE payments 
                    SET payment_date = %s, payment_type = %s, vendor_id = %s, 
                        payment_mode = %s, amount = %s, narration = %s
                    WHERE payment_id = %s
                """, (payment_date, payment_type, vendor_id, payment_mode, amount, narration, payment_id))
            else:  # misc payment
                payment_for = request.form['payment_for']
                cursor.execute("""
                    UPDATE payments 
                    SET payment_date = %s, payment_type = %s, payment_for = %s, 
                        payment_mode = %s, amount = %s, narration = %s
                    WHERE payment_id = %s
                """, (payment_date, payment_type, payment_for, payment_mode, amount, narration, payment_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Payment updated successfully!', 'success')
            return redirect(url_for('view_payments'))
            
        except Exception as e:
            flash(f'Error updating payment: {str(e)}', 'danger')
            return redirect(url_for('edit_payment', payment_id=payment_id))
    
    # GET request - show form with existing data
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.*, pm.party as vendor_name 
        FROM payments p
        LEFT JOIN party_master pm ON p.vendor_id = pm.p_id
        WHERE p.payment_id = %s
    """, (payment_id,))
    payment = cursor.fetchone()
    
    if not payment:
        flash('Payment not found', 'danger')
        return redirect(url_for('view_payments'))
    
    cursor.execute("SELECT p_id, party FROM party_master ORDER BY party")
    vendors = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('edit_payment.html', payment=payment, vendors=vendors)

@app.route('/delete_payment/<int:payment_id>')
def delete_payment(payment_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete the payment
        cursor.execute('DELETE FROM payments WHERE payment_id = %s', (payment_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('Payment deleted successfully!', 'success')
        return redirect(url_for('view_payments'))
        
    except Exception as e:
        flash(f'Error deleting payment: {str(e)}', 'danger')
        return redirect(url_for('view_payments'))

if __name__ == '__main__':
    app.run(debug=True) 
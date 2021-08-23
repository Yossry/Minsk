
def set_charge_date(cr, registry):
    cr.execute("""
        UPDATE account_invoice SET charge_date = date_due 
        WHERE "type" = 'out_invoice'
        AND date_due is not NULL 
        AND charge_date is NULL;
    """)
    return True

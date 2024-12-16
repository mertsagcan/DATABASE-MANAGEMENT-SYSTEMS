
CREATE OR REPLACE FUNCTION check_amount_before_insert()
RETURNS TRIGGER AS $$
BEGIN

    IF NEW.amount <= 0 THEN

        RAISE EXCEPTION 'Amount must be greater than 0';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER trigger_check_amount_before_insert
BEFORE INSERT ON shopping_carts
FOR EACH ROW EXECUTE FUNCTION check_amount_before_insert();

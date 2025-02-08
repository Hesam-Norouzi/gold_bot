CREATE TABLE gold_prices (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    time TIME NOT NULL DEFAULT CURRENT_TIME,
    gold_price_world INTEGER,
    dollar_price INTEGER,
    gold_mesghal INTEGER,
    gold18_price_iran INTEGER,
    index NUMERIC GENERATED ALWAYS AS (gold_mesghal - ((gold_price_world * dollar_price)/9.5742)) STORED,
    status VARCHAR(20)
);

CREATE OR REPLACE FUNCTION update_gold_status()
RETURNS TRIGGER AS $$
BEGIN
    NEW.status := CASE
        WHEN NEW.index > 500000 THEN 'sell'
        WHEN NEW.index < 100000 THEN 'buy'
        ELSE 'do nothing'
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER gold_prices_status_trigger
BEFORE INSERT OR UPDATE ON gold_prices
FOR EACH ROW
EXECUTE PROCEDURE update_gold_status();
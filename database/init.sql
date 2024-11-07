CREATE TABLE financial_data (
    id SERIAL PRIMARY KEY,
    company VARCHAR(50),
    period VARCHAR(50),
    date DATE,
    data JSONB
);

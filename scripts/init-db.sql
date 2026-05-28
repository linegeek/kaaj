-- Create separate database for Hatchet (app uses 'kaaj' which postgres creates automatically)
CREATE DATABASE hatchet;
CREATE USER hatchet WITH PASSWORD 'hatchet';
GRANT ALL PRIVILEGES ON DATABASE hatchet TO hatchet;

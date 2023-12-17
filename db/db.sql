

DROP TABLE IF EXISTS "deal";
DROP TABLE IF EXISTS "object";
DROP TABLE IF EXISTS "user";
DROP TABLE IF EXISTS "type_of_deal";
DROP TABLE IF EXISTS "type_of_object";
DROP TABLE IF EXISTS "adress";


CREATE TABLE "user" (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    second_name VARCHAR(255) NOT NULL,
    login VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    pass_num CHAR(11) UNIQUE NOT NULL,
    phone_num CHAR(11) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(10)
);

CREATE TABLE "type_of_object" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE "adress" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE "type_of_deal" (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE "object" (
    id SERIAL PRIMARY KEY,
    id_type_of_object SERIAL REFERENCES "type_of_object" (id),
    id_type_of_deal SERIAL REFERENCES "type_of_deal" (id),
    id_adress SERIAL REFERENCES "adress" (id),
    room_num INTEGER NOT NULL,
    square INTEGER NOT NULL,
    price INTEGER NOT NULL,
    floar_num INTEGER NOT NULL,
    date_build INTEGER NOT NULL,
    material_type VARCHAR(255) NOT NULL,
    distance_to_subway INTEGER,
    district VARCHAR(255) NOT NULL,
    description TEXT,
    date_of_sale DATE NOT NULL,
    image TEXT NOT NULL
);

CREATE TABlE "deal" (
    id SERIAL PRIMARY KEY,
    id_object SERIAL REFERENCES "object" (id),
    id_first_user INTEGER  REFERENCES "user" (id),
    id_second_user INTEGER REFERENCES "user" (id),
    id_type_of_deal SERIAL NOT NULL REFERENCES "type_of_deal" (id),
    date_of_deal DATE,
    price_of_deal INTEGER 
);



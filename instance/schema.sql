PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS configkeys;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS postcode;
DROP TABLE IF EXISTS googleplace;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS googletypes;
DROP TABLE IF EXISTS openinghours;
DROP TABLE IF EXISTS googlereviews;
DROP TABLE IF EXISTS yelpplace;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS joblist;

PRAGMA foreign_keys = ON;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE configkeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyname TEXT UNIQUE NOT NULL,
    keyvalue TEXT NOT NULL,
    keytype TEXT NOT NULL
);

CREATE TABLE restaurants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    businessstatus TEXT,
    restaurantname TEXT NOT NULL,
    street1 TEXT NOT NULL,
    street2 TEXT,
    suburb TEXT NOT NULL,
    postcode TEXT NOT NULL,
    restaurantstate TEXT NOT NULL
);

CREATE TABLE  review (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datestamp DATETIME NOT NULL,
    restaurantid REFERENCES restaurants (id),
    reviews INTEGER NOT NULL,
    average INTEGER NOT NULL,
    price INTEGER,
    source TEXT NOT NULL
);

CREATE TABLE keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    typeid INTEGER NOT NULL,
    entitytype TEXT NOT NULL
);

CREATE TABLE postcode (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    postcode TEXT NOT NULL,
    locality TEXT NOT NULL,
    postcodestate TEXT NOT NULL,
    lat FLOAT NOT NULL,
    lng FLOAT NOT NULL,
    sa2 TEXT
);

CREATE TABLE places (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placename TEXT,
    parentplace INTEGER,
    googleplaceid REFERENCES googleplace(id),
    yelpplaceid REFERENCES yelpplace(id),
    vicinity TEXT,
    street1 TEXT NOT NULL,
    street2 TEXT,
    suburb TEXT NOT NULL,
    postcode TEXT NOT NULL,
    placestate TEXT NOT NULL,
    phonenumber TEXT
);


CREATE TABLE googleplace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid REFERENCES places(id),
    business_status INTEGER,
    viewportnelat FLOAT,
    viewportnelng FLOAT,
    viewportswlat FLOAT,
    viewportswlng FLOAT,
    lat FLOAT,
    lng FLOAT,
    price_level INTEGER,
    rating FLOAT,
    user_ratings_total, INTEGER,
    googleplace_id TEXT,
    placeurl TEXT,
    website TEXT
);

CREATE TABLE yelpplace (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid REFERENCES places(id),
    business_status INTEGER,
    lat FLOAT,
    lng FLOAT,
    price_level INTEGER,
    rating FLOAT,
    user_ratings_total INTEGER,
    yelpplace_id TEXT,
    website TEXT
);

CREATE TABLE types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid REFERENCES places(id),
    placetype TEXT
);

CREATE TABLE openinghours (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid REFERENCES places(id),
    sundayopen TEXT,
    sundayclose TEXT,
    mondayopen TEXT,
    mondayclose TEXT,
    tuesdayopen TEXT,
    tuesdayclose TEXT,
    wednesdayopen TEXT,
    wednesdayclose TEXT,
    thursdayopen TEXT,
    thursdayclose TEXT,
    fridayopen TEXT,
    fridayclose TEXT,
    saturdayopen TEXT,
    saturdayclose TEXT
);

CREATE TABLE reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    placeid REFERENCES places(id),
    rating INTEGER,
    reviewtext TEXT,
    source TEXT
);

CREATE TABLE joblist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    jobjson TEXT,
    jobtype TEXT
);

INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('googleapikey', 'key=AIzaSyCG6S55TX0YlfBGrnyFlBEMrQzwpBdICzU', 'string');
INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('yelpapikey', 'Bearer spf4KDBHyyC_RFAjsGq_x3bj1XJSk-tWW797udceKCQtXtwjHtIDw2KeZ1aMWrvgcCLkmfZi3G2A1nLcU5k77qko8syWYcgOWO_xZAKtRMxarOVkp5Fm461jFzX5XnYx', 'string');

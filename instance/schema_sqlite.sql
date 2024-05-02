PRAGMA foreign_keys = OFF;

DROP TABLE if EXISTS categorytotype;
DROP TABLE if EXISTS categorylist;
DROP TABLE IF EXISTS configkeys;
DROP TABLE IF EXISTS cuisinelist;
DROP TABLE IF EXISTS jobresults;
DROP TABLE IF EXISTS linelist;
DROP TABLE IF EXISTS pointlist;
DROP TABLE IF EXISTS polygon;
DROP TABLE IF EXISTS regiondata;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS searchcategories;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS restaurants;
DROP TABLE IF EXISTS keywords;
DROP TABLE IF EXISTS postcode;
DROP TABLE IF EXISTS googleplace;
DROP TABLE IF EXISTS googlesupportedtypes;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS googletypes;
DROP TABLE IF EXISTS openinghours;
DROP TABLE IF EXISTS googlereviews;
DROP TABLE IF EXISTS yelpplace;
DROP TABLE IF EXISTS types;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS joblist;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS zomatoplace;

PRAGMA foreign_keys = ON;



CREATE TABLE configkeys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyname TEXT UNIQUE NOT NULL,
    keyvalue TEXT NOT NULL,
    keytype TEXT NOT NULL
);

CREATE TABLE categorytotype (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  categoryid REFERENCES categorylist (id) ON DELETE CASCADE,
  cuisineid REFERENCES cuisinelist (id) ON DELETE CASCADE
);

CREATE TABLE categorylist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name text,
  comment text
);

CREATE TABLE cuisinelist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placetype TEXT,
  coffee BOOLEAN DEFAULT 0,
  license BOOLEAN DEFAULT 0,
  cuisine BOOLEAN DEFAULT 0,
  blacklist BOOLEAN DEFAULT 0
);

CREATE TABLE googleplace (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid int REFERENCES places (id),
  business_status int DEFAULT NULL,
  viewportnelat float DEFAULT NULL,
  viewportnelng float DEFAULT NULL,
  viewportswlat float DEFAULT NULL,
  viewportswlng float DEFAULT NULL,
  lat float DEFAULT NULL,
  lng float DEFAULT NULL,
  price_level int DEFAULT NULL,
  rating float DEFAULT NULL,
  user_ratings_total int DEFAULT NULL,
  googleplace_id text,
  placeurl text,
  website text,
  pluscode text
);

CREATE TABLE joblist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  jobjson TEXT,
  jobtype TEXT,
  address TEXT,
  radius int DEFAULT NULL,
  lat float DEFAULT NULL,
  lng float DEFAULT NULL,
  maxprice int DEFAULT NULL,
  minprice int DEFAULT NULL,
  roughcount int DEFAULT NULL,
  googleplugin int DEFAULT 0,
  yelpplugin int DEFAULT 0,
  zomatoplugin int DEFAULT 0,
  googlecomplete BOOLEAN DEFAULT 0,
  yelpcomplete BOOLEAN DEFAULT 0,
  zomatocomplete BOOLEAN DEFAULT 0,
  userid REFERENCES users (id)
);

CREATE TABLE jobresults (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid REFERENCES places (id),
  jobid REFERENCES jonlist (id)
);

CREATE TABLE linelist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  polygon_id REFERENCES polygon (id),
  nlat float DEFAULT NULL,
  nlng float DEFAULT NULL,
  slat float DEFAULT NULL,
  slng float DEFAULT NULL
); 

CREATE TABLE openinghours (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid REFERENCES places (id),
  sundayopen text,
  sundayclose text,
  mondayopen text,
  mondayclose text,
  tuesdayopen text,
  tuesdayclose text,
  wednesdayopen text,
  wednesdayclose text,
  thursdayopen text,
  thursdayclose text,
  fridayopen text,
  fridayclose text,
  saturdayopen text,
  saturdayclose text
);

CREATE TABLE places (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placename text,
  parentplace REFERENCES places (id) DEFAULT NULL,
  googleplaceid REFERENCES googleplace (id) DEFAULT NULL,
  yelpplaceid REFERENCES yelpplace (id) DEFAULT NULL,
  vicinity text,
  street1 text,
  street2 text,
  suburb text,
  postcode text,
  placestate text,
  phonenumber text,
  zomatoplaceid REFERENCES zomatoplace (id) DEFAULT NULL,
  pluscode text
);

CREATE TABLE pointlist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  polygon_id REFERENCES polygon (id),
  lat float DEFAULT NULL,
  lng float DEFAULT NULL,
  order_ int DEFAULT NULL
);

CREATE TABLE polygon (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  region_id REFERENCES regeiondata (id),
  max_lng float DEFAULT NULL,
  max_lat float DEFAULT NULL,
  min_lng float DEFAULT NULL,
  min_lat float DEFAULT NULL,
  points int DEFAULT NULL
);

CREATE TABLE postcode (
  postcode int DEFAULT NULL,
  Locality text,
  postcodestate TEXT,
  lat float DEFAULT NULL,
  lng float DEFAULT NULL,
  sa2 text,
  ID INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE regiondata (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sa2_maincode character(9) DEFAULT NULL,
  sa2_5_digit character(5) DEFAULT NULL,
  sa2_name text,
  sa3_name text,
  sa4_name text, 
  state text,
  area float DEFAULT NULL
);

CREATE TABLE reviews (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid REFERENCES places (id),
  rating int DEFAULT NULL,
  reviewtext text,
  source text
);

CREATE TABLE roles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE
);

CREATE TABLE searchcategories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  jobid REFERENCES joblist (id),
  category text,
  plugin text
);

CREATE TABLE types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid REFERENCES places (id) DEFAULT NULL,
  placetype text
);

CREATE TABLE user_roles (
  user_id REFERENCES users (id) DEFAULT NULL,
  role_id REFERENCES roles (id) DEFAULT NULL,
  id INTEGER PRIMARY KEY AUTOINCREMENT
);

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE DEFAULT NULL,
  password TEXT DEFAULT NULL,
  is_active BOOLEAN NOT NULL DEFAULT 1,
  email_confirmed_at DATETIME DEFAULT NULL,
  first_name TEXT DEFAULT NULL,
  last_name TEXT DEFAULT NULL
);

CREATE TABLE yelpplace (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid REFERENCES places (id) DEFAULT NULL,
  business_status int DEFAULT NULL,
  lat float DEFAULT NULL,
  lng float DEFAULT NULL,
  price_level int DEFAULT NULL,
  rating float DEFAULT NULL,
  user_ratings_total int DEFAULT NULL,
  yelpplace_id text,
  website text
);

CREATE TABLE zomatoplace (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  placeid  REFERENCES places (id) DEFAULT NULL,
  zomatoplace_id int DEFAULT NULL,
  rating float DEFAULT NULL,
  user_ratings_total int DEFAULT NULL,
  cuisine text,
  website text,
  business_status int DEFAULT NULL,
  price_level int DEFAULT NULL,
  lat float DEFAULT NULL,
  lng float DEFAULT NULL
);

CREATE TABLE googlesupportedtypes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  description TEXT,
  value TEXT,
  checked BOOLEAN DEFAULT 1, 
);

INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('googleapikey', 'key=AIzaSyCG6S55TX0YlfBGrnyFlBEMrQzwpBdICzU', 'string');
INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('yelpapikey', 'Bearer spf4KDBHyyC_RFAjsGq_x3bj1XJSk-tWW797udceKCQtXtwjHtIDw2KeZ1aMWrvgcCLkmfZi3G2A1nLcU5k77qko8syWYcgOWO_xZAKtRMxarOVkp5Fm461jFzX5XnYx', 'string');

INSERT INTO roles (name) VALUES ('admin');
INSERT INTO users (username, password, is_active, first_name, last_name) VALUES ('arg', '$2b$12$E0zTUAot1FPyr9km7ONMDeD9BNPmpuhy9VEr50cbPCEgSROi0Uwgm', 1, 'Admin', 'Man');
INSERT INTO user_roles (user_id, role_id) VALUES (1, 1);

INSERT INTO googlesupportedtypes (value, description) VALUES ('airport', 'Airport');
INSERT INTO googlesupportedtypes (value, description) VALUES ('amusement_park', 'Amusement Park');
INSERT INTO googlesupportedtypes (value, description) VALUES ('aquarium', 'Aquarium');
INSERT INTO googlesupportedtypes (value, description) VALUES ('art_gallery', 'Art Gallery');
INSERT INTO googlesupportedtypes (value, description) VALUES ('bakery', 'Bakery');
INSERT INTO googlesupportedtypes (value, description) VALUES ('bar', 'Bar');
INSERT INTO googlesupportedtypes (value, description) VALUES ('bowling_alley', 'Bowling Alley');
INSERT INTO googlesupportedtypes (value, description) VALUES ('cafe', 'Cafe');
INSERT INTO googlesupportedtypes (value, description) VALUES ('casino', 'Casino');
INSERT INTO googlesupportedtypes (value, description) VALUES ('convenience_store', 'Convenience Store');
INSERT INTO googlesupportedtypes (value, description) VALUES ('gas_station', 'Gas Station');
INSERT INTO googlesupportedtypes (value, description) VALUES ('liquor_store', 'Liquor Store');
INSERT INTO googlesupportedtypes (value, description) VALUES ('lodging', 'Lodging');
INSERT INTO googlesupportedtypes (value, description) VALUES ('meal_delivery', 'Meal Delivery');
INSERT INTO googlesupportedtypes (value, description) VALUES ('meal_takeaway', 'Meal Takeaway');
INSERT INTO googlesupportedtypes (value, description) VALUES ('night_club', 'Night Club');
INSERT INTO googlesupportedtypes (value, description) VALUES ('restaurant', 'Restaurant');
INSERT INTO googlesupportedtypes (value, description) VALUES ('shopping_mall', 'Shopping Mall');
INSERT INTO googlesupportedtypes (value, description) VALUES ('spa', 'Spa');
INSERT INTO googlesupportedtypes (value, description) VALUES ('stadium', 'Stadium');
INSERT INTO googlesupportedtypes (value, description) VALUES ('supermarket', 'Supermarket');


SET FOREIGN_KEY_CHECKS=0; 

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

SET FOREIGN_KEY_CHECKS=1; 

#CREATE DATABASE `flasky_test` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
CREATE TABLE `configkeys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `keyname` text NOT NULL,
  `keyvalue` text NOT NULL,
  `keytype` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categorylist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` text,
  `comment` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `cuisinelist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placetype` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `coffee` tinyint(1) DEFAULT NULL,
  `license` tinyint(1) DEFAULT NULL,
  `cuisine` tinyint(1) DEFAULT NULL,
  `blacklist` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=307 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `categorytotype` (
  `id` int NOT NULL AUTO_INCREMENT,
  `categoryid` int DEFAULT NULL,
  `cuisineid` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `categoryid` (`categoryid`),
  KEY `cuisineid` (`cuisineid`),
  CONSTRAINT `categorytotype_ibfk_1` FOREIGN KEY (`categoryid`) REFERENCES `categorylist` (`id`) ON DELETE CASCADE,
  CONSTRAINT `categorytotype_ibfk_2` FOREIGN KEY (`cuisineid`) REFERENCES `cuisinelist` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `places` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placename` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `parentplace` int DEFAULT NULL,
  `googleplaceid` int DEFAULT NULL,
  `yelpplaceid` int DEFAULT NULL,
  `vicinity` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `street1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `street2` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `suburb` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `postcode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `placestate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `phonenumber` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `zomatoplaceid` int DEFAULT NULL,
  `pluscode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`)
  ) ENGINE=InnoDB AUTO_INCREMENT=7758 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `googleplace` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `business_status` int DEFAULT NULL,
  `viewportnelat` float DEFAULT NULL,
  `viewportnelng` float DEFAULT NULL,
  `viewportswlat` float DEFAULT NULL,
  `viewportswlng` float DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `price_level` int DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `user_ratings_total` int DEFAULT NULL,
  `googleplace_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `placeurl` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `website` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `pluscode` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `googleplace_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7282 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `joblist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jobjson` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `jobtype` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `radius` int DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `maxprice` int DEFAULT NULL,
  `minprice` int DEFAULT NULL,
  `roughcount` int DEFAULT NULL,
  `googleplugin` int DEFAULT NULL,
  `yelpplugin` int DEFAULT '0',
  `zomatoplugin` int DEFAULT '0',
  `googlecomplete` tinyint DEFAULT '0',
  `yelpcomplete` tinyint DEFAULT '0',
  `zomatocomplete` tinyint DEFAULT '0',
  `userid` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=331 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `jobresults` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `jobid` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  KEY `jobid` (`jobid`),
  CONSTRAINT `jobresults_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`),
  CONSTRAINT `jobresults_ibfk_2` FOREIGN KEY (`jobid`) REFERENCES `joblist` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14680 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `openinghours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `sundayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `sundayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `mondayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `mondayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `tuesdayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `tuesdayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `wednesdayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `wednesdayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `thursdayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `thursdayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `fridayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `fridayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `saturdayopen` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `saturdayclose` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `openinghours_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6062 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `regiondata` (
  `id` int NOT NULL AUTO_INCREMENT,
  `sa2_maincode` char(9) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `sa2_5_digit` char(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `sa2_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `sa3_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `sa4_name` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `state` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `area` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2197 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `polygon` (
  `id` int NOT NULL AUTO_INCREMENT,
  `region_id` int DEFAULT NULL,
  `max_lng` float DEFAULT NULL,
  `max_lat` float DEFAULT NULL,
  `min_lng` float DEFAULT NULL,
  `min_lat` float DEFAULT NULL,
  `points` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `region_id` (`region_id`),
  CONSTRAINT `polygon_ibfk_1` FOREIGN KEY (`region_id`) REFERENCES `regiondata` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8975 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `pointlist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `polygon_id` int DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `order_` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `polygon_id` (`polygon_id`),
  CONSTRAINT `pointlist_ibfk_1` FOREIGN KEY (`polygon_id`) REFERENCES `polygon` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;



CREATE TABLE `linelist` (
  `id` int NOT NULL AUTO_INCREMENT,
  `polygon_id` int DEFAULT NULL,
  `nlat` float DEFAULT NULL,
  `nlng` float DEFAULT NULL,
  `slat` float DEFAULT NULL,
  `slng` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `polygon_id` (`polygon_id`),
  CONSTRAINT `linelist_ibfk_1` FOREIGN KEY (`polygon_id`) REFERENCES `polygon` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4155609 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `postcode` (
  `postcode` int DEFAULT NULL,
  `Locality` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `postcodestate` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `sa2` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `ID` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=18276 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `reviews` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `rating` int DEFAULT NULL,
  `reviewtext` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `source` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `searchcategories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `jobid` int DEFAULT NULL,
  `category` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `plugin` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `jobid` (`jobid`),
  CONSTRAINT `searchcategories_ibfk_1` FOREIGN KEY (`jobid`) REFERENCES `joblist` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3598 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `types` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `placetype` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `types_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23350 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `is_active` tinyint NOT NULL DEFAULT '1',
  `email_confirmed_at` varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `first_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `last_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `user_roles` (
  `user_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  KEY `id_idx` (`user_id`),
  KEY `roles.id_idx` (`role_id`),
  CONSTRAINT `roles.id` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `users.id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `yelpplace` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `business_status` int DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `price_level` int DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `user_ratings_total` int DEFAULT NULL,
  `yelpplace_id` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `website` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `yelpplace_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2802 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `zomatoplace` (
  `id` int NOT NULL AUTO_INCREMENT,
  `placeid` int DEFAULT NULL,
  `zomatoplace_id` int DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `user_ratings_total` int DEFAULT NULL,
  `cuisine` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `website` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `business_status` int DEFAULT NULL,
  `price_level` int DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `placeid` (`placeid`),
  CONSTRAINT `zomatoplace_ibfk_1` FOREIGN KEY (`placeid`) REFERENCES `places` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=266 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('googleapikey', 'key=AIzaSyCG6S55TX0YlfBGrnyFlBEMrQzwpBdICzU', 'string');
INSERT INTO configkeys (keyname, keyvalue, keytype) VALUES ('yelpapikey', 'Bearer spf4KDBHyyC_RFAjsGq_x3bj1XJSk-tWW797udceKCQtXtwjHtIDw2KeZ1aMWrvgcCLkmfZi3G2A1nLcU5k77qko8syWYcgOWO_xZAKtRMxarOVkp5Fm461jFzX5XnYx', 'string');
INSERT INTO roles (name) VALUES ('admin');
INSERT INTO users (username, password, is_active, first_name, last_name) VALUES ('arg', '$2b$12$E0zTUAot1FPyr9km7ONMDeD9BNPmpuhy9VEr50cbPCEgSROi0Uwgm', 1, 'Admin', 'Man');
INSERT INTO user_roles (user_id, role_id) VALUES (1, 1);
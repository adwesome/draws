// Old
CREATE TABLE IF NOT EXISTS participants(uid, cid);
CREATE TABLE IF NOT EXISTS winners(cid, uid);
CREATE TABLE IF NOT EXISTS campaigns (cid, date_go, ad, who, percent, prize);

// New
CREATE TABLE IF NOT EXISTS players (uid INTEGER, date_created INTEGER, region INTEGER, city INTEGER, sex INTEGER, age INTEGER, tguid INTEGER);
CREATE TABLE IF NOT EXISTS brands (name TEXT);
CREATE TABLE IF NOT EXISTS playersbrands (pid INTEGER, bid INTEGER);
INSERT INTO brands VALUES ('mk');
INSERT INTO brands VALUES ('lenta');

CREATE TABLE IF NOT EXISTS org (name TEXT, bid INTEGER);
INSERT INTO org VALUES ('Магнит Косметик', 1);
INSERT INTO org VALUES ('Лента', 2);
CREATE TABLE IF NOT EXISTS cam (oid INTEGER, date_start INTEGER, date_end INTEGER, ad TEXT, winners INTEGER);
INSERT INTO cam VALUES (1, 1731077891, 1731164291, '/img/ad-mk.jpg', 3);
INSERT INTO cam VALUES (2, 1731077891, 1731164291, '/img/ad-lenta.jpg', 3);
CREATE TABLE IF NOT EXISTS par (cid INTEGER, pid INTEGER, status INTEGER);

alter table brands rename column name to webapp_code;
alter table brands add column name TEXT;
UPDATE brands SET name = 'Магнит Косметик' WHERE webapp_code = 'mk';
UPDATE brands SET name = 'Лента' WHERE webapp_code = 'lenta';
alter table brands add column logo TEXT;
UPDATE brands SET logo = 'img/brands/logos/mk.png' WHERE webapp_code = 'mk';
UPDATE brands SET logo = 'img/brands/logos/lenta.png' WHERE webapp_code = 'lenta';

INSERT INTO cam VALUES (1, 1731189929, 1733004197, '/img/ad-mk.jpg?v=1', 3);
INSERT INTO cam VALUES (1, 1731189929, 1733004197, '/img/ad-mk.jpg?v=2', 5);
INSERT INTO cam VALUES (2, 1731189929, 1733004197, '/img/ad-lenta.jpg?=1', 3);
INSERT INTO cam VALUES (2, 1731189929, 1733004197, '/img/ad-lenta.jpg?v=2', 1);

INSERT INTO brands VALUES ('mk', 'Магнит Косметик', 'img/brands/logos/mk.png');
DELETE from brands WHERE rowid = 1;
UPDATE org SET bid = 3 WHERE bid = 1;

UPDATE cam set ad = 'img/ads/ad-mk.jpg' where oid = 1;
UPDATE cam set ad = 'img/ads/ad-lenta.jpg' where oid = 2;

ALTER TABLE par ADD COLUMN date TEXT;
ALTER TABLE cam RENAME COLUMN winners TO chance;

UPDATE playersbrands SET bid = 3 where bid = 1;
UPDATE cam set chance = 20 where rowid = 4;
UPDATE cam set chance = 15 where rowid = 3;
UPDATE cam set chance = 15 where rowid = 5;
UPDATE cam set chance = 10 where rowid = 6;

ALTER TABLE par ADD COLUMN gift TEXT;
UPDATE par SET gift = 'https://card.digift.ru/card/show/code/bb898d955afe898e5596abd0311e5b49' WHERE status = 1;

INSERT INTO orgs VALUES ('DeLuxe', 'Салон красоты', 'бул. Советов 5');

UPDATE cam SET date_end = 1731607200 WHERE rowid >= 3;
INSERT INTO cam VALUES (1, 1731618000, 1731806999, '/img/ad-mk.jpg', 3);
INSERT INTO cam VALUES (2, 1731618000, 1731806999, '/img/ad-lenta.jpg', 3);

UPDATE par SET gift = '' WHERE gift IS NULL;


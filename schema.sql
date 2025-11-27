DROP TABLE IF EXISTS shortened_links;

CREATE TABLE shortened_links (
	id INTEGER PRIMARY KEY AUTOINCREMENT;
	long_link TEXT UNIQUE NOT NULL;
	short_link TEXT NOT NULL;
);

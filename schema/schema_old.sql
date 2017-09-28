CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL, 
	CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(64), "default" BOOLEAN, permissions INTEGER, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(64), 
	role_id INTEGER, email VARCHAR(64), password_hash VARCHAR(128), confirmed BOOLEAN, about_me TEXT, last_seen DATETIME, location VARCHAR(64), member_since DATETIME, name VARCHAR(64), avatar_hash VARCHAR(32), 
	PRIMARY KEY (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
);
CREATE UNIQUE INDEX ix_users_username ON users (username);
CREATE UNIQUE INDEX ix_users_email ON users (email);
CREATE INDEX ix_roles_default ON roles ("default");
CREATE TABLE posts (
	id INTEGER NOT NULL, 
	body TEXT, 
	timestamp DATETIME, 
	author_id INTEGER, body_html TEXT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES users (id)
);
CREATE INDEX ix_posts_timestamp ON posts (timestamp);
CREATE TABLE follows (
	follower_id INTEGER NOT NULL, 
	followed_id INTEGER NOT NULL, 
	timestamp DATETIME, 
	PRIMARY KEY (follower_id, followed_id), 
	FOREIGN KEY(followed_id) REFERENCES users (id), 
	FOREIGN KEY(follower_id) REFERENCES users (id)
);
CREATE TABLE comments (
	id INTEGER NOT NULL, 
	body TEXT, 
	body_html TEXT, 
	timestamp DATETIME, 
	disabled BOOLEAN, 
	author_id INTEGER, 
	post_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(author_id) REFERENCES users (id), 
	FOREIGN KEY(post_id) REFERENCES posts (id), 
	CHECK (disabled IN (0, 1))
);
CREATE INDEX ix_comments_timestamp ON comments (timestamp);

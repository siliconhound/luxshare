from app import db

followers = db.Table(
    "followers", db.Column("follower_id", db.Integer,
                           db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")))

post_hashtag = db.Table(
    "hashtag_post", db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("hashtag_id", db.Integer, db.ForeignKey("hashtag.id")))

tagged_users = db.Table(
    "tagged_users", db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")))

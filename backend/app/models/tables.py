from app import db

followers = db.Table(
    "followers", db.Column("follower_id", db.Integer,
                           db.ForeignKey("user.id")),
    db.Column("followed_id", db.Integer, db.ForeignKey("user.id")))

hashtag_posts = db.Table(
    "hashtag_posts",
    db.Column("hashtag_id", db.Integer, db.ForeignKey("hashtag.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")))

tagged_users = db.Table(
    "tagged_users", db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")))

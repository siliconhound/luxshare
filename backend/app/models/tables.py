from app import db

followers = db.Table("followers",
                     db.Column("follower_id", db.Integer, db.ForeignKey("user.id")),
                     db.Column("followed_id", db.Integer, db.ForeignKey("user.id")))

hashtag_post = db.Table("hashtag_post",
                        db.Column("hashtag_id", db.Integer, db.ForeignKey("hashtag.id")),
                        db.Column("post_id", db.Integer, db.ForeignKey("post.id")))

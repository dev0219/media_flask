"""This scripts sets up inital data for the MediaMix.ai App
"""

from apps import db
from apps.authentication.models import Users

# drop all tables first if they are populated
db.drop_all()

# Creates all the Tables Model --> DB Table
db.create_all()

# create admin user
admin = Users(username="admin",email= "admin@something.com", password="password", is_admin=True)


if __name__ == "__main__":
    db.session.add_all([admin])
    db.session.commit()
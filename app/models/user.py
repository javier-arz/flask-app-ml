from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True,
                         unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           index=True,
                           default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    @property
    def password(self):
        """Throw an error when trying to access password attribute"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)

    # Methods
    def verify_password(self, password):
        """Returns true or false by verifing a given password"""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def create(cls, attributes):
        """Create a user from writable attributes, save it to the database,
        and return it."""
        valid_attributes = {
            attribute.key
            for attribute in cls.__mapper__.column_attrs
        }
        valid_attributes.update(
            name
            for name, descriptor in vars(cls).items()
            if isinstance(descriptor, property)
            and descriptor.fset is not None
        )

        invalid_attributes = sorted(
            set(attributes) - valid_attributes
        )
        if invalid_attributes:
            invalid_names = ", ".join(invalid_attributes)
            raise AttributeError(
                f"Unknown {cls.__name__} "
                f"attribute(s): {invalid_names}"
            )

        instance = cls()
        for attribute, value in attributes.items():
            setattr(instance, attribute, value)

        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, attributes):
        """Update writable attributes, save changes to the database,
        and return this user."""
        valid_attributes = {
            attribute.key
            for attribute in self.__mapper__.column_attrs
        }
        valid_attributes.update(
            name
            for name, descriptor in vars(type(self)).items()
            if isinstance(descriptor, property)
            and descriptor.fset is not None
        )

        invalid_attributes = sorted(
            set(attributes) - valid_attributes
        )
        if invalid_attributes:
            invalid_names = ", ".join(invalid_attributes)
            raise AttributeError(
                f"Unknown {type(self).__name__} "
                f"attribute(s): {invalid_names}"
            )

        for attribute, value in attributes.items():
            setattr(self, attribute, value)

        db.session.commit()
        return self

    def delete(self):
        """Delete this user from the database."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Model representation for code debugging"""
        return f'<User id:{self.id} username:{self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Load the user from the database, given the id stored
    in the session"""
    return User.query.get(int(user_id))

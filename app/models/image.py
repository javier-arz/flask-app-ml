from app import db
from datetime import datetime, timezone

class Image(db.Model):
    __tablename__ = 'images'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           index=True, 
                           default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True),
                           default=lambda: datetime.now(timezone.utc), 
                           onupdate=lambda: datetime.now(timezone.utc))

    # Methods
    @classmethod
    def create(cls, attributes):
        """Create an instance from mapped attributes, save it to the database,
        and return it."""
        valid_attributes = {
            attribute.key
            for attribute in cls.__mapper__.column_attrs
        }
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
        """Update mapped attributes, save changes to the database,
        and return this instance."""
        valid_attributes = {
            attribute.key
            for attribute in self.__mapper__.column_attrs
        }
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
        """Delete this instance from the database."""
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        """Model representation for Code Debugging"""
        return f'<Image id:{self.id}>'

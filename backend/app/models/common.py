from app import db
from datetime import datetime

class BaseMixin(object):

  @classmethod
  def get(cls, id):
    """ Returns an instance of model by id :param id: model id """

    return cls.query.get(id)

  @classmethod
  def get_all(cls, ids=None):
    """
    Returns list of all model instances, if id list is specified, all instances
    in that list are returned
    """

    return cls.query.all() if not ids else cls.query.filter(
        cls.id.in_(ids)).all()

  @classmethod
  def find(cls, **kwargs):
    """
    Returns list of all model instances filtered by specified keys
    """

    return cls.query.filter_by(**kwargs)

  @classmethod
  def first(cls, **kwargs):
    """
    Returns first model instance that meets parameters
    """

    return cls.query.filter_by(**kwargs).first()

  def update(self, data):
    """
    updates updatable fields in ATTR_FIELDS with the data provided
    """
    for field in self.ATTR_FIELDS:
      if field in data:
        setattr(self, field, data[field])


class DateAudit(object):

  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(
      db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  def audit_dates(self) -> dict:
    """
    Returns date properties for audit
    """
    return {
        "created_at": self.created_at.isoformat() + 'Z',
        "updated_at": self.updated_at.isoformat() + 'Z'
    }

class PaginatedAPIMixin(object):

  @staticmethod
  def to_collection_dict(query, page = 0, per_page = 0, endpoint = '', **kwargs):
    """
    Returns a dictionary of a paginated collection of model instances
    """
    resources = query.paginate(page, per_page, False)
    return {
        'items': [item.to_dict() for item in resources.items],
        '_meta': {
            'page': page,
            'per_page': per_page,
            'total_pages': resources.pages,
            'total_items': resources.total
        },
        '_links': {
            'self':
                url_for(endpoint, page=page, per_page=per_page, **kwargs),
            'next':
                url_for(endpoint, page=page + 1, per_page=per_page, **kwargs)
                if resources.has_next else None,
            'prev':
                url_for(endpoint, page=page - 1, per_page=per_page, **kwargs)
                if resources.has_prev else None
        }
    }

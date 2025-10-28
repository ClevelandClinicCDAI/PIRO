from typing import Type

from db.base_class import Base


def get_model_dict(model: Type[Base]):
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}

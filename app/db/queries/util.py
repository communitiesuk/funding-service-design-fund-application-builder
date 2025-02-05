from sqlalchemy import delete


def delete_all_related_objects(db, model, column, ids):
    ## Delete objects for a given object type and based on the filter id and data
    if ids:
        stmt = delete(model).filter(column.in_(ids))
        db.session.execute(stmt)
        db.session.commit()

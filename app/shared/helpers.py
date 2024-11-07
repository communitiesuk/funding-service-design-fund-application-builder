from dataclasses import asdict
from dataclasses import is_dataclass
from app.db.models import Page

def convert_to_dict(obj):
    if is_dataclass(obj):
        return asdict(obj)
    elif isinstance(obj, list):
        return [asdict(item) if is_dataclass(item) else item for item in obj]
    else:
        return obj


def find_enum(enum_class, value):
    for enum in enum_class:
        if enum.value == value:
            return enum
    return None

def get_all_pages_in_parent_form(db, page_id):
    # Get the form_id from page_id
    page = db.session.query(Page).filter(Page.page_id == page_id).first()
    
    if page is None:
        raise ValueError(f"No page found with page_id: {page_id}")
    
    form_id = page.form_id
    
    # Get all page ids belonging to the form
    page_ids = db.session.query(Page.page_id).filter(Page.form_id == form_id).all()
    
    # Extract page_ids from the result
    page_ids = [p.page_id for p in page_ids]
    
    return page_ids
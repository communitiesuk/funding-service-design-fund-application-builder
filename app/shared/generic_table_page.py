class GenericTablePage:
    def __init__(
        self,
        page_heading: str,
        page_description: str,
        detail_text: str,
        detail_description: str,
        button_text: str,
        button_url: str,
        table_header: list[dict],
        table_rows: list[dict],
    ):
        """
        Initializes the GenericTablePage object with the necessary metadata for rendering a generic table page.

        Args:
            page_heading (str): The heading for the page.
            page_description (str): The description to display on the page.
            detail_text (str): A detail title or introductory text for the page.
            detail_description (str): A detail description of the detail title.
            button_text (str): The text for a button on the page.
            button_url (str): Button URL for the page.
            table_header (list): The heading of the table, typically the column headers.
            table_rows (list): A list of table rows to be displayed on the page.
        """
        self.page_heading = page_heading
        self.page_description = page_description
        self.detail = {
            "detail_text": detail_text,
            "detail_description": detail_description,
        }
        self.button = {
            "button_text": button_text,
            "button_url": button_url,
        }
        self.table = {
            "table_header": table_header,
            "table_rows": table_rows,
        }

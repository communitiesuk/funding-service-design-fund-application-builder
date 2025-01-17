import math


class GenericTablePage:
    def __init__(
        self,
        table_header: list[dict],
        table_rows: list[dict],
        current_page: int = 1,
        rows_per_page: int = 20,
    ):
        """
        Initializes the GenericTablePage object with the necessary metadata for rendering a generic table page.

        Args:
            table_header (list): The heading of the table, typically the column headers.
            table_rows (list): A list of table rows to be displayed on the page.
            current_page (int): When using pagination, this variable will be used to determine the page. Default to 1.
            rows_per_page (int): The number of rows to display per page. Default to 20.
        """
        pagination, paginated_rows = self.pagination(table_rows, current_page, rows_per_page)
        self.generic_table_page = {
            "table": {"table_header": table_header, "table_rows": paginated_rows},
            **({"pagination": pagination} if bool(pagination) else {}),
        }

    @staticmethod
    def pagination(table_rows: list[dict], current_page: int, rows_per_page: int) -> tuple[dict, list]:
        if len(table_rows) <= rows_per_page:
            return {}, table_rows
        # Paginate the data
        total_items = len(table_rows)
        number_of_pages = math.ceil(total_items / rows_per_page)
        start_index = (current_page - 1) * rows_per_page
        end_index = start_index + rows_per_page
        paginated_rows = table_rows[start_index:end_index]
        # Pagination metadata
        pagination = {
            "items": [
                {
                    "number": i,
                    "href": f"?page={i}",
                    **({"current": True} if i == current_page else {}),  # Add "current" only if i == current_page
                }
                for i in range(1, number_of_pages + 1)
            ],
            **({"previous": {"href": f"?page={current_page - 1}"}} if current_page > 1 else {}),
            **({"next": {"href": f"?page={current_page + 1}"}} if current_page < number_of_pages else {}),
        }

        return pagination, paginated_rows

def determine_display_value_for_condition(
    condition_value: str,
    list_name: str = None,
    form_lists: list[dict] = None,
    lang: str = "en",
) -> str:
    """Determines the display value for the given condition string - either translating true/false into
       yes/no or by finding the display value from the given list.
       Uses lang to determine english or welsh

    Args:
        condition_value (str): Value to translate
        list_name (str, optional): Name of the list for this field. Defaults to None.
        form_lists (list[dict], optional): List of lists from the form_json to find value. Defaults to [].
        lang (str, optional): Language to use. Defaults to 'en'.

    Returns:
        str: The display value
    """
    if form_lists is None:
        form_lists = []
    if condition_value.casefold() == "true":
        return "Yes" if lang == "en" else "Ydy"
    elif condition_value.casefold() == "false":
        return "No" if lang == "en" else "Nac ydy"
    else:
        if list_name:
            list_values = next(lizt["items"] for lizt in form_lists if lizt["name"] == list_name)
            condition_text = next(item["text"] for item in list_values if item["value"] == condition_value)
            return condition_text
        return condition_value


def determine_if_just_html_page(components: list) -> bool:
    """Determines whether this page contains only html (display) components

    Args:
        components (list): Components present on this page

    Returns:
        bool: Whether or not they are all html display components
    """
    return all([(c["type"].casefold() == "para" or c["type"].casefold() == "html") for c in components])


def remove_lowest_in_hierarchy(number_str: str) -> str:
    """Takes in a string numerical hierarchy eg. 2.3.4 and removes the lowest member, in this case 4

    Args:
        number_str (str): Hierarchy to remove the lowest part of, eg. 4.5.6

    Returns:
        str: Resulting hierarchy string, eg. 4.5
    """
    last_dot_idx = number_str.rfind(".")
    return number_str[:last_dot_idx]


def increment_lowest_in_hierarchy(number_str: str) -> str:
    """Takes in a string numerical hierarchy, eg. 2.3.4 and increments the lowest number.

    Args:
        number_str (str): Hierarchy to increment, eg. 1.2.3

    Returns:
        str: Incremented hierarchy, eg. 1.2.4
    """
    result = ""
    split_by_dots = number_str.split(".")
    if not split_by_dots[-1]:
        split_by_dots.pop()
    to_inc = int(split_by_dots[-1])
    split_by_dots.pop()
    to_inc += 1
    if split_by_dots:
        result = (".").join(split_by_dots)
        result += "."
    result += f"{to_inc}"
    return result


def strip_leading_numbers(text: str) -> str:
    """Removes leading numbers and . from a string

    Args:
        text (str): String to remove leading numbers from, eg. `2.2. A Title`

    Returns:
        str: Stripped string, eg. `A Title`
    """
    result = text
    for char in text:
        if char == " ":
            break
        if char.isdigit() or char == ".":
            result = result[1:]  # strip this character
    return result.strip()


def build_section_header(section_title, lang: str = "en"):
    """Formats the title text for this section, and creates an html-safe anchor id for that section

    Args:
        section (Section): Section to create title for
        lang (str, optional): Language for this title. Defaults to "en".

    Returns:
        str, str: Anchor ID, followed by the title text
    """
    title = section_title
    title = strip_leading_numbers(title)
    anchor = title.casefold().replace(" ", "-")
    return anchor, title

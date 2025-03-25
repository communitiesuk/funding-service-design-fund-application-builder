from uuid import uuid4

import pytest

from app.db.models import Form, Fund, Round, Section
from app.db.queries.application import (
    delete_form_from_section,
    delete_section_from_round,
    get_section_by_id,
    move_form_down,
    move_form_up,
    move_section_down,
    move_section_up,
    swap_elements_in_list,
)
from app.db.queries.round import get_round_by_id
from tests.seed_test_data import BASIC_FUND_INFO, BASIC_ROUND_INFO

section_id = uuid4()


# Create a section with one form, at index 1
@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"})],
    }
)
def test_form_sorting(seed_dynamic_data, _db):
    section = seed_dynamic_data["sections"][0]
    form1 = seed_dynamic_data["forms"][0]
    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 1

    # add a form at index 2, confirm ordering
    form2: Form = Form(
        form_id=uuid4(), section_id=section.section_id, section_index=2, name_in_apply_json={"en": "Form 2"}
    )
    _db.session.add(form2)
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 2
    assert result_section.forms[0].form_id == form1.form_id
    assert result_section.forms[1].form_id == form2.form_id

    # add a form at index 0, confirm ordering
    form0: Form = Form(
        form_id=uuid4(), section_id=section.section_id, section_index=0, name_in_apply_json={"en": "Form 0"}
    )
    _db.session.add(form0)
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 3
    assert result_section.forms[0].form_id == form0.form_id
    assert result_section.forms[1].form_id == form1.form_id
    assert result_section.forms[2].form_id == form2.form_id

    # insert a form between 1 and 2, check ordering
    formX: Form = Form(form_id=uuid4(), section_id=section.section_id, name_in_apply_json={"en": "Form X"})
    result_section.forms.insert(2, formX)
    _db.session.bulk_save_objects([result_section])
    _db.session.commit()

    result_section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 4
    assert result_section.forms[0].form_id == form0.form_id
    assert result_section.forms[1].form_id == form1.form_id
    assert result_section.forms[2].form_id == formX.form_id
    assert result_section.forms[3].form_id == form2.form_id
    assert result_section.forms[3].section_index == 4


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
def test_form_sorting_removal(seed_dynamic_data, _db):
    section = seed_dynamic_data["sections"][0]

    result_section: Section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(result_section.forms) == 3
    form2 = result_section.forms[1]
    assert form2.section_index == 2

    delete_form_from_section(section_id=result_section.section_id, form_id=form2.form_id)

    updated_section: Section = _db.session.query(Section).where(Section.section_id == section.section_id).one_or_none()
    assert len(updated_section.forms) == 2
    assert updated_section.forms[0].section_index == 1
    assert updated_section.forms[1].section_index == 2


# Create a section with one form, at index 1
round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "hello section",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section2"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section3"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
def test_section_sorting_removal(seed_dynamic_data, _db):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3
    last_section_id = round.sections[2].section_id
    assert round.sections[2].index == 3
    section_to_delete = round.sections[1]

    delete_section_from_round(section_id=section_to_delete.section_id, round_id=round_id)

    updated_round = get_round_by_id(round_id)
    assert len(updated_round.sections) == 2
    assert round.sections[1].section_id == last_section_id
    assert round.sections[1].index == 2


round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "hello section",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section2"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "hello section3"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
@pytest.mark.parametrize(
    "index_to_move, exp_new_index",
    [
        (1, 2),  # move 1 ->2
        (2, 3),  # move 2 -> 3
    ],
)
def test_section_sorting_move_down(seed_dynamic_data, _db, index_to_move, exp_new_index):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3

    section_to_move_down = round.sections[index_to_move - 1]  # numbering starts at 1 not 0
    id_to_move = section_to_move_down.section_id
    assert section_to_move_down.index == index_to_move

    section_that_moves_up = round.sections[index_to_move]
    assert section_that_moves_up.index == index_to_move + 1
    section_id_that_moves_up = section_that_moves_up.section_id

    move_section_down(round_id=round_id, section_id=section_to_move_down.section_id)

    updated_round = get_round_by_id(round_id)
    # total sections shouldn't change
    assert len(round.sections) == 3

    # check new position
    moved_down_section = updated_round.sections[index_to_move]
    assert moved_down_section.section_id == id_to_move
    assert moved_down_section.index == exp_new_index

    # check the section that was after this one has now moved up
    moved_up_section = updated_round.sections[index_to_move - 1]
    assert moved_up_section.section_id == section_id_that_moves_up
    assert moved_up_section.index == exp_new_index - 1


round_id = uuid4()
fund_id = uuid4()


@pytest.mark.seed_config(
    {
        "funds": [Fund(**BASIC_FUND_INFO, fund_id=fund_id, short_name="UT1")],
        "rounds": [
            Round(**BASIC_ROUND_INFO, title_json={"en": "round1"}, round_id=round_id, fund_id=fund_id, short_name="R1")
        ],
        "sections": [
            Section(
                name_in_apply_json={
                    "en": "section a",
                },
                index=1,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "section b"},
                index=2,
                round_id=round_id,
            ),
            Section(
                name_in_apply_json={"en": "section c"},
                index=3,
                round_id=round_id,
            ),
        ],
    }
)
@pytest.mark.parametrize(
    "index_to_move, exp_new_index",
    [
        (2, 1),  # move 2 -> 1
        (3, 2),  # move 3 -> 2
    ],
)
def test_move_section_up(seed_dynamic_data, _db, index_to_move, exp_new_index):
    round_id = seed_dynamic_data["rounds"][0].round_id
    round: Round = get_round_by_id(round_id)
    assert len(round.sections) == 3

    section_to_move_up = round.sections[index_to_move - 1]  # list index starts at 0 not 1
    id_to_move = section_to_move_up.section_id
    assert section_to_move_up.index == index_to_move

    section_that_gets_moved_down = round.sections[index_to_move - 2]
    id_that_gets_moved_down = section_that_gets_moved_down.section_id
    assert section_that_gets_moved_down.index == index_to_move - 1

    move_section_up(round_id=round_id, section_id=id_to_move)

    updated_round = get_round_by_id(round_id)
    assert len(updated_round.sections) == 3

    # Check section that moved up
    moved_up_section = updated_round.sections[index_to_move - 2]
    assert moved_up_section.section_id == id_to_move
    assert moved_up_section.index == exp_new_index
    # Check the section that got moved down
    moved_down_section = updated_round.sections[index_to_move - 1]
    assert moved_down_section.section_id == id_that_gets_moved_down
    assert moved_down_section.index == exp_new_index + 1


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
@pytest.mark.parametrize("index_to_move, exp_new_index", [(2, 1), (3, 2)])
def test_move_form_up(seed_dynamic_data, _db, index_to_move, exp_new_index):
    section_id = seed_dynamic_data["sections"][0].section_id
    section = get_section_by_id(section_id)
    assert len(section.forms) == 3

    id_to_move_up = section.forms[index_to_move - 1].form_id
    assert section.forms[index_to_move - 1].section_index == index_to_move

    id_to_move_down = section.forms[index_to_move - 2].form_id
    assert section.forms[index_to_move - 2].section_index == exp_new_index

    move_form_up(section_id, id_to_move_up)

    updated_section = get_section_by_id(section_id)
    assert len(updated_section.forms) == 3

    assert updated_section.forms[index_to_move - 2].form_id == id_to_move_up
    assert updated_section.forms[index_to_move - 1].form_id == id_to_move_down


section_id = uuid4()


@pytest.mark.seed_config(
    {
        "sections": [Section(section_id=section_id, name_in_apply_json={"en": "hello section"})],
        "forms": [
            Form(form_id=uuid4(), section_id=section_id, section_index=1, name_in_apply_json={"en": "Form 1"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=2, name_in_apply_json={"en": "Form 2"}),
            Form(form_id=uuid4(), section_id=section_id, section_index=3, name_in_apply_json={"en": "Form 3"}),
        ],
    }
)
@pytest.mark.parametrize("index_to_move, exp_new_index", [(1, 2), (2, 3)])
def test_move_form_down(seed_dynamic_data, _db, index_to_move, exp_new_index):
    section_id = seed_dynamic_data["sections"][0].section_id
    section = get_section_by_id(section_id)
    assert len(section.forms) == 3

    id_to_move_down = section.forms[index_to_move - 1].form_id
    assert section.forms[index_to_move - 1].section_index == index_to_move

    id_to_move_up = section.forms[index_to_move].form_id
    assert section.forms[index_to_move].section_index == index_to_move + 1

    move_form_down(section_id, id_to_move_down)

    updated_section = get_section_by_id(section_id)
    assert len(updated_section.forms) == 3

    assert updated_section.forms[index_to_move].form_id == id_to_move_down
    assert updated_section.forms[index_to_move - 1].form_id == id_to_move_up


@pytest.mark.parametrize(
    "input_list, idx_a, idx_b, exp_result",
    [
        (["a", "b", "c", "d"], 0, 1, ["b", "a", "c", "d"]),
        (["a", "b", "c", "d"], 1, 3, ["a", "d", "c", "b"]),
        (["a", "b", "c", "d"], -1, 3, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], -1, -123123, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], 1, -123123, ["a", "b", "c", "d"]),
        (["a", "b", "c", "d"], 1, 4, ["a", "b", "c", "d"]),
    ],
)
def test_swap_elements(input_list, idx_a, idx_b, exp_result):
    result = swap_elements_in_list(input_list, idx_a, idx_b)
    assert result == exp_result

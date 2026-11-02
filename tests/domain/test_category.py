import pytest

from moneyup.domain import Category, CategoryKind


def test_create_category():
    food = Category("Food", CategoryKind.EXPENSE)

    assert food.name == "Food"
    assert food.kind is CategoryKind.EXPENSE


def test_name_is_trimmed():
    assert Category("  Rent  ", CategoryKind.EXPENSE).name == "Rent"


@pytest.mark.parametrize("bad_name", ["", "   "])
def test_empty_name_is_rejected(bad_name):
    with pytest.raises(ValueError):
        Category(bad_name, CategoryKind.EXPENSE)


def test_categories_with_same_data_are_equal():
    # dataclasses compare by value, not by identity
    assert Category("Food", CategoryKind.EXPENSE) == Category(
        "Food", CategoryKind.EXPENSE
    )


def test_category_is_immutable():
    food = Category("Food", CategoryKind.EXPENSE)
    with pytest.raises(AttributeError):
        food.name = "Drinks"

from core.list_util import split_list_group


def test_split_list_group_basic():
    test_list: list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert split_list_group(lst=test_list, group_size=3) == [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
    ]


def test_split_list_group_advanced():
    test_list: list = [1, 2, 3, 4, 5, 6, [1, 2, 3], 7, 8, 9]
    assert split_list_group(lst=test_list, group_size=4) == [
        [1, 2, 3, 4],
        [5, 6, [1, 2, 3], 7],
        [8, 9],
    ]

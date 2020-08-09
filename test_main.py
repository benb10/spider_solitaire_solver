from main import get_run, Card


def test_get_run():
    test = ['J', '10', 'A']
    test = [Card(val=v, box=None) for v in test]
    assert [c.val for c in get_run(test)] == ['A']

    test = ['10', '9', '8']
    test = [Card(val=v, box=None) for v in test]
    assert [c.val for c in get_run(test)] == ['10', '9', '8']

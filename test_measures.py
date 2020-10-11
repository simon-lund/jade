import pytest

from measures import (
    group_by_package,
    noc,
    ca,
    ce,
    instability,
    dcm_lcom3,
    dcm_sim,
    dcm_cc,
    pdd,
    dlm,
)


def test_group_by_package():
    dg = {
        "a.G": {},
        "a.b.H": {},
        "a.b.I": {},
        "a.b.c.A": {},
        "a.b.c.d.e.f.g.h.i.j.J": {},
        "a.d.e.B": {},
        "a.d.e.C": {},
        "a.f.g.D": {},
        "a.f.g.E": {},
        "a.f.g.F": {},
    }

    assert group_by_package(dg) == {
        "a": ["a.G"],
        "a.b": ["a.b.H", "a.b.I"],
        "a.b.c": ["a.b.c.A"],
        "a.b.c.d.e.f.g.h.i.j": ["a.b.c.d.e.f.g.h.i.j.J"],
        "a.d.e": ["a.d.e.B", "a.d.e.C"],
        "a.f.g": ["a.f.g.D", "a.f.g.E", "a.f.g.F"],
    }


def test_noc():
    assert noc({"a"}) == 1
    assert noc({"a", "b", "c"}) == 3
    assert noc({"a", "b", "c", "d", "e"}) == 5
    assert noc({"a", "b", "c", "d", "e", "f", "g"}) == 7


def test_cpl():
    dg1 = {
        "a": ["b", "c", "d"],
        "b": ["c", "d"],
        "c": ["e", "f"],
        "d": ["g"],
        "e": ["g"],
        "f": ["d"],
        "g": [],
        "h": ["i", "j"],
        "i": ["j"],
        "j": ["g"],
    }

    classes1 = {"a", "d", "i"}
    assert ce(classes1, dg1) == 3
    assert ca(classes1, dg1) == 3
    assert instability(classes1, dg1) == 3 / (3 + 3)

    classes2 = {"a", "b", "c", "d", "i"}
    assert ce(classes2, dg1) == 3
    assert ca(classes2, dg1) == 2
    assert instability(classes2, dg1) == 3 / (3 + 2)

    classes3 = {"a", "h"}
    assert ce(classes3, dg1) == 2
    assert ca(classes3, dg1) == 0
    assert instability(classes3, dg1) == 2 / (2 + 0)


    dg2 = {
        "a": ["b", "c", "d"],
        "b": ["a", "c", "d"],
        "c": ["e", "f"],
        "d": ["f", "g"],
        "e": ["a", "b", "g"],
        "f": ["a", "h"],
        "g": ["f"],
        "h": ["i", "j", "d"],
        "i": ["j", "h"],
        "j": ["g", "h"],
    }

    classes4 = {"a", "d", "i"}
    assert ce(classes4, dg2) == 3
    assert ca(classes4, dg2) == 4
    assert instability(classes4, dg2) == 3 / (3 + 4)

    classes5 = {"a", "b", "c", "d", "i"}
    assert ce(classes5, dg2) == 3
    assert ca(classes5, dg2) == 3
    assert instability(classes5, dg2) == 3 / (3 + 3)

    classes6 = {"a", "h"}
    assert ce(classes6, dg2) == 2
    assert ca(classes6, dg2) == 5
    assert instability(classes6, dg2) == 2 / (2 + 5)



def test_dcm():
    pkg1 = [{"a", "b", "c"}]

    assert dcm_lcom3(pkg1) == 0
    assert dcm_sim(pkg1) == 0
    assert dcm_cc(pkg1) == (1 + 1 + 1) / (1 * 3)

    pkg2 = [
        {"a", "b", "c"},
        {"a", "b", "c"},
        {"a", "b", "c"},
    ]

    assert dcm_lcom3(pkg2) == (len(pkg2) - 1) * len(pkg2) / 2
    assert dcm_sim(pkg2) == (3 / 3 + 3 / 3 + 3 / 3) / 3
    assert dcm_cc(pkg2) == (5 + 5 + 5) / (5 * 3)

    pkg3 = [
        {"a", "b"},
        {"c", "d"},
        {"e", "f", "g"},
        {"h", "i", "j", "k", "l"},
        {"m"},
    ]

    assert dcm_lcom3(pkg3) == 0
    assert dcm_sim(pkg3) == 0
    assert dcm_cc(pkg3) == (1 * 13) / (5 * 13)

    pkg4 = [
        {"a", "b"},
        {"b", "c"},
        {"c", "d"},
        {"d", "e"},
    ]

    assert dcm_lcom3(pkg4) == 3
    assert dcm_sim(pkg4) == (1 / 3 + 0 / 3 + 0 / 3 + 1 / 3 + 0 / 3 + 1 / 3) / 6
    assert dcm_cc(pkg4) == (1 + 2 + 2 + 2 + 1) / (4 * 5)

    pkg5 = [
        {"a", "b", "c"},
        {"a", "b"},
        {"c", "d", "e"},
        {"c", "f"},
        {"g"},
    ]

    assert dcm_lcom3(pkg5) == 4
    assert dcm_sim(pkg5) == (2 / 3 + 1 / 5 + 1 / 4 + 1 / 4) / 10
    assert dcm_cc(pkg5) == (2 + 2 + 3 + 1 + 1 + 1 + 1) / (5 * 7)


def test_pdd():
    dg1 = {
        "a": ["b", "c", "d"],
        "b": ["c", "d"],
        "c": ["e", "f"],
        "d": ["g"],
        "e": ["g"],
        "f": ["d"],
        "g": [],
        "h": ["i", "j"],
        "i": ["j"],
        "j": ["g"],
    }

    assert pdd({"a", "b", "c"}, dg1) == 10 / 14
    assert pdd({"a", "b", "c", "d", "e", "f", "g", "h", "i", "j"}, dg1) == 14 / 14
    assert pdd({"h", "i"}, dg1) == 4 / 14
    assert pdd({"h", "i", "f"}, dg1) == 6 / 14
    assert pdd({"h", "i", "f", "d"}, dg1) == 6 / 14
    assert pdd({"h", "i", "f", "d", "e"}, dg1) == 7 / 14
    assert pdd({"h", "i", "f", "d", "e", "c"}, dg1) == 9 / 14
    assert pdd({"a", "b", "c"}, dg1) == 10 / 14
    assert pdd({"j"}, dg1) == 1 / 14

    dg2 = {
        "a": ["b", "c", "d"],
        "b": ["a", "c", "d"],
        "c": ["e", "f"],
        "d": ["f", "g"],
        "e": ["a", "b", "g"],
        "f": ["a", "h"],
        "g": ["f"],
        "h": ["i", "j", "d"],
        "i": ["j", "h"],
        "j": ["g", "h"],
    }

    for c in dg2:
        assert pdd({c}, dg2) == 1

    assert pdd({"a", "b"}, dg2) == 1
    assert pdd({"b", "i"}, dg2) == 1
    assert pdd({"c", "d"}, dg2) == 1
    assert pdd({"e", "j"}, dg2) == 1
    assert pdd({"f", "g"}, dg2) == 1
    assert pdd({"h", "i"}, dg2) == 1

    assert pdd({"a", "c", "d"}, dg2) == 1
    assert pdd({"b", "f", "g"}, dg2) == 1
    assert pdd({"d", "e", "f"}, dg2) == 1
    assert pdd({"h", "i", "j"}, dg2) == 1


def test_dlm():
    deps = {
        "a.G",
        "a.b.H",
        "a.b.I",
        "a.b.c.A",
        "a.b.c.d.e.f.g.h.i.j.J",
        "a.d.e.B",
        "a.d.e.C",
        "a.f.g.D",
        "a.f.g.E",
        "a.f.g.F",
    }

    assert dlm("a", deps) == 23
    assert dlm("a.b", deps) == 25
    assert dlm("a.f", deps) == 27
    assert dlm("a.b.c", deps) == 31
    assert dlm("a.b.c.d", deps) == 39

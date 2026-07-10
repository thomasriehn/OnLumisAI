from worker.connectors.filesystem import acl_for

RULES = [
    {"pattern": "hr/*", "groups": ["hr"]},
    {"pattern": "produktion/*", "groups": ["produktion", "qs"]},
    {"pattern": "*.geheim.md", "groups": ["geschaeftsfuehrung"]},
]


def test_first_matching_rule_wins():
    assert acl_for("hr/urlaub.md", RULES, ["all-users"]) == ["hr"]
    assert acl_for("produktion/linie1/wartung.md", RULES, ["all-users"]) == [
        "produktion",
        "qs",
    ]


def test_default_when_no_rule_matches():
    assert acl_for("allgemein/kantine.md", RULES, ["all-users"]) == ["all-users"]


def test_pattern_matches_across_directories():
    assert acl_for("strategie/2026.geheim.md", RULES, ["all-users"]) == [
        "geschaeftsfuehrung"
    ]


def test_windows_separators_normalized():
    assert acl_for("hr\\urlaub.md", RULES, ["all-users"]) == ["hr"]


def test_empty_rules():
    assert acl_for("x.md", [], ["all-users"]) == ["all-users"]

data = {
    "change": [
        "ALTER TABLE Image ADD COLUMN creator text",
        "ALTER TABLE Image ADD COLUMN source text",
    ],
    "revert": ["ALTER TABLE Image DROP creator", "ALTER TABLE Image DROP source"],
    "logging": ["ADDED Columns: creator (text), source (text) TO Image"],
    "reversible": True,
}

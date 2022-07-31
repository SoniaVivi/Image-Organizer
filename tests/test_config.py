from vivid.config import Config


class TestConfig:
    def test_section_attributes(self):
        assert sorted(
            Config().section_attributes("image_index_context_menu")
        ) == sorted(
            [
                "image_tagging",
                "image_renaming",
                "image_deleting",
                "image_removing",
                "image_blacklisting",
                "creator_updating",
                "source_updating",
                "folder_searching",
                "hash_searching",
            ]
        )

    def test_section_items(self):
        assert Config().section_items("image_index_context_menu") == {
            "image_tagging": "True",
            "image_renaming": "True",
            "image_removing": "True",
            "image_deleting": "False",
            "image_blacklisting": "False",
            "creator_updating": "True",
            "source_updating": "True",
            "folder_searching": "True",
            "hash_searching": "True",
        }

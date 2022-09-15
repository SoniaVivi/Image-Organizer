from vivid.vivid_logger import VividLogger as Logger


class TestVividLogger:
    test_messages = [
        "This is a message",
        "SEVERE WARNING",
        "GENERIC ERROR",
    ]

    def test_register(self):
        logger_a = Logger("test")
        logger_a.register("msg_a", self.test_messages[0])
        assert callable(logger_a.msg_a) == True
        assert hasattr(Logger("throw_away"), "msg_a") == False
        assert callable(Logger("test").msg_a) == True

    def test_write(self, capfd):
        Logger.set_print_mode("console")
        logger = Logger("test")
        logger.register("msg_b", self.test_messages[1], level=4)
        logger.register("msg_c", self.test_messages[2], level=3)

        logger.msg_a()
        out, err = capfd.readouterr()
        assert (
            out == f"[\033[0;33m WARNING \033[0;0m] [ test ] {self.test_messages[0]}\n"
        )

        logger.msg_b()
        out, err = capfd.readouterr()
        assert (
            out == f"[\033[1;31m CRITICAL \033[0;0m] [ test ] {self.test_messages[1]}\n"
        )

        logger.msg_c()
        out, err = capfd.readouterr()
        assert out == f"[\033[0;31m ERROR \033[0;0m] [ test ] {self.test_messages[2]}\n"

    def test_print_history(self, capfd):
        Logger("test").print_history()
        out, err = capfd.readouterr()
        out = out.split("\n")
        msgs = [
            f"[\033[0;33m WARNING \033[0;0m] [ test ] {self.test_messages[0]}",
            f"[\033[1;31m CRITICAL \033[0;0m] [ test ] {self.test_messages[1]}",
            f"[\033[0;31m ERROR \033[0;0m] [ test ] {self.test_messages[2]}",
        ]
        for i in range(0, 3):
            assert out[i].split("|")[1] == " " + msgs[i]

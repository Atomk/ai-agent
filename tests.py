import unittest
from functions.get_files_info import get_files_info


class TestGetFilesInfo(unittest.TestCase):
    def test_current_directory(self):
        result = get_files_info("calculator", ".")
        expected = "\n".join([
            "- pkg: file_size=4096 bytes, is_dir=True",
            "- main.py: file_size=588 bytes, is_dir=False",
            "- tests.py: file_size=1354 bytes, is_dir=False",
        ])
        self.assertEqual(result, expected)

    def test_existing_subdir(self):
        result = get_files_info("calculator", "pkg")
        expected = "\n".join([
            "- calculator.py: file_size=1744 bytes, is_dir=False",
            "- render.py: file_size=777 bytes, is_dir=False",
        ])
        self.assertEqual(result, expected)

    def test_non_existing_subdir(self):
        result = get_files_info("calculator", "fake_dir")
        expected = "Error: \"fake_dir\" is not a directory"
        self.assertEqual(result, expected)

    def test_outside_absolute(self):
        result = get_files_info("calculator", "/bin")
        expected = "Error: Cannot list \"/bin\" as it is outside the permitted working directory"
        self.assertEqual(result, expected)

    def test_outside_relative(self):
        result = get_files_info("calculator", "../")
        expected = "Error: Cannot list \"../\" as it is outside the permitted working directory"
        self.assertEqual(result, expected)

    # TODO make this work
    # def test_nonexistent_working_directory(self):
    #     result = get_files_info("banana", ".")
    #     expected = "Error: \"banana\" does not exist"
    #     self.assertEqual(result, expected)
    #
    #     result = get_files_info("banana")
    #     expected = "Error: \"banana\" does not exist"
    #     self.assertEqual(result, expected)
    #
    #     result = get_files_info("main.py")
    #     expected = "Error: \"main.py\" is not a directory"
    #     self.assertEqual(result, expected)

    # TODO prevent using working directories that are outside the package


if __name__ == "__main__":
    unittest.main()

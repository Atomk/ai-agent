import os
import unittest
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file


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


class TestGetFileContent(unittest.TestCase):
    def test_existing(self):
        result = get_file_content(".", ".python-version")
        self.assertTrue(result.startswith("3."))
        self.assertTrue(result.endswith("\n"))
        self.assertTrue(3 <= len(result) <= 9)

    def test_non_existing(self):
        filename = "fake_file"
        result = get_file_content("calculator", filename)
        expected = f'Error: File not found or is not a regular file: "{filename}"'
        self.assertEqual(result, expected)

    def test_outside_absolute(self):
        result = get_file_content("calculator", "/bin/main.py")
        expected = 'Error: Cannot read "/bin/main.py" as it is outside the permitted working directory'
        self.assertEqual(result, expected)

    def test_outside_relative(self):
        result = get_file_content("calculator", "../main.py")
        expected = 'Error: Cannot read "../main.py" as it is outside the permitted working directory'
        self.assertEqual(result, expected)

    # TODO create a test TXT for this, needs to override the MAX_LENGTH
    # def test_truncated(self):
    #     # set MAX_LENGTH to 3
    #     file_path = ".python-version"
    #     result = get_file_content(".", file_path)
    #     expected = f'3.1[...File "{file_path}" truncated at 3 characters]'
    #     self.assertEqual(result, expected)


class TestWriteFile(unittest.TestCase):
    def _remove_if_exists(self, dir, rel_path):
        abspath = os.path.abspath(os.path.join(dir, rel_path))
        if os.path.exists(abspath):
            os.remove(abspath)

    def _exists(self, dir, rel_path) -> bool:
        abspath = os.path.abspath(os.path.join(dir, rel_path))
        return os.path.exists(abspath)

    def test_not_a_file(self):
        result = write_file(".", ".", "TEST ERROR")
        self.assertEqual(result, f'Error: "." exists but it\'s not a regular file')

    def test_create_and_overwrite(self):
        wd = "."
        file_path = "__test_file"
        content = "Test file created successfully!"
        # Ensure file does not exist before the test
        self._remove_if_exists(wd, file_path)
        result = write_file(wd, file_path, content)
        self.assertEqual(
            result,  f'Successfully wrote to "{file_path}" (31 characters written)'
        )
        self.assertEqual(get_file_content(wd, file_path), content)

        # Overwrite
        content_new = "Content was overwritten!"
        result = write_file(wd, file_path, content_new)
        self.assertEqual(
            result, f'Successfully wrote to "{file_path}" (24 characters written)'
        )
        self.assertEqual(get_file_content(wd, file_path), content_new)
        # Delete test file
        self._remove_if_exists(wd, file_path)

    def test_create_in_existing_subdir(self):
        wd = "calculator"
        file_path = "__test_file"
        content = "Test file created successfully!"
        # Ensure file does not exist before the test
        self._remove_if_exists(wd, file_path)
        result = write_file(wd, file_path, content)
        self.assertEqual(
            result,  f'Successfully wrote to "{file_path}" (31 characters written)'
        )
        self.assertEqual(get_file_content(wd, file_path), content)
        # Delete test file
        self._remove_if_exists(wd, file_path)

    # TODO: function should actually create the necessary subdirectories
    def test_create_in_nonexistent_subdir(self):
        wd = "__new_subdir"
        file_path = "__test_file"
        content = "Test file created successfully!"
        result = write_file(wd, file_path, content)
        self.assertTrue(result.startswith("Error: cannot write to file"))
        self.assertFalse(self._exists(wd, file_path))

    def test_outside_absolute(self):
        result = write_file("calculator", "/bin/main.py", "TEST ERROR")
        expected = 'Error: Cannot write to "/bin/main.py" as it is outside the permitted working directory'
        self.assertEqual(result, expected)

    def test_outside_relative(self):
        result = write_file("calculator", "../main.py", "TEST ERROR")
        expected = 'Error: Cannot write to "../main.py" as it is outside the permitted working directory'
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()

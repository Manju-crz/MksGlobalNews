import os
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


class FileUtils:
    """Utility class for file operations"""

    @staticmethod
    def create_file(filename, content='', encoding='utf-8'):
        """
        Create a file with the given filename and content.
        Automatically detects file type based on extension.

        Args:
            filename (str): Name of the file to create (with extension)
            content (str or dict or list): Content to write to the file
            encoding (str): File encoding (default: 'utf-8')

        Returns:
            bool: True if file created successfully, False otherwise

        Examples:
            # Create text file
            FileUtils.create_file('data.txt', 'Hello World')

            # Create JSON file
            FileUtils.create_file('data.json', {'key': 'value'})

            # Create XML file
            FileUtils.create_file('data.xml', {'root': {'item': 'value'}})

            # Create empty file
            FileUtils.create_file('empty.log')
        """
        try:
            # Get file extension
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            # Get directory path
            directory = os.path.dirname(filename)

            # Create directory if it doesn't exist
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")

            # Handle different file types
            if ext == '.json':
                # JSON file
                with open(filename, 'w', encoding=encoding) as f:
                    if isinstance(content, (dict, list)):
                        json.dump(content, f, indent=2, ensure_ascii=False)
                    else:
                        # If content is string, try to parse it as JSON
                        try:
                            json_content = json.loads(content) if content else {}
                            json.dump(json_content, f, indent=2, ensure_ascii=False)
                        except:
                            # If not valid JSON, write as is
                            f.write(str(content))

            elif ext == '.xml':
                # XML file
                if isinstance(content, dict):
                    # Convert dict to XML
                    root = FileUtils._dict_to_xml(content)
                    xml_str = FileUtils._prettify_xml(root)
                    with open(filename, 'w', encoding=encoding) as f:
                        f.write(xml_str)
                else:
                    # Write content as is
                    with open(filename, 'w', encoding=encoding) as f:
                        f.write(str(content))

            else:
                # Text file or any other extension
                with open(filename, 'w', encoding=encoding) as f:
                    if isinstance(content, (dict, list)):
                        # Convert to string representation
                        f.write(str(content))
                    else:
                        f.write(str(content))

            print(f"File created successfully: {filename}")
            return True

        except Exception as e:
            print(f"Error creating file '{filename}': {str(e)}")
            return False

    @staticmethod
    def _dict_to_xml(data, root_name='root'):
        """Convert dictionary to XML ElementTree"""
        if isinstance(data, dict) and len(data) == 1:
            root_name = list(data.keys())[0]
            data = data[root_name]

        root = ET.Element(root_name)
        FileUtils._build_xml_tree(root, data)
        return root

    @staticmethod
    def _build_xml_tree(parent, data):
        """Recursively build XML tree from dictionary"""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for item in value:
                        child = ET.SubElement(parent, key)
                        if isinstance(item, dict):
                            FileUtils._build_xml_tree(child, item)
                        else:
                            child.text = str(item)
                elif isinstance(value, dict):
                    child = ET.SubElement(parent, key)
                    FileUtils._build_xml_tree(child, value)
                else:
                    child = ET.SubElement(parent, key)
                    child.text = str(value)
        else:
            parent.text = str(data)

    @staticmethod
    def _prettify_xml(elem):
        """Return a pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    def append_to_file(filename, content, encoding='utf-8'):
        """
        Append content to an existing file.

        Args:
            filename (str): Name of the file
            content (str): Content to append
            encoding (str): File encoding (default: 'utf-8')

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'a', encoding=encoding) as f:
                f.write(str(content))
            print(f"Content appended to: {filename}")
            return True
        except Exception as e:
            print(f"Error appending to file '{filename}': {str(e)}")
            return False

    @staticmethod
    def read_file(filename, encoding='utf-8'):
        """
        Read content from a file.

        Args:
            filename (str): Name of the file
            encoding (str): File encoding (default: 'utf-8')

        Returns:
            str or dict: File content (parsed if JSON)
        """
        try:
            _, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext == '.json':
                with open(filename, 'r', encoding=encoding) as f:
                    return json.load(f)
            else:
                with open(filename, 'r', encoding=encoding) as f:
                    return f.read()

        except Exception as e:
            print(f"Error reading file '{filename}': {str(e)}")
            return None

    @staticmethod
    def file_exists(filename):
        """Check if file exists"""
        return os.path.exists(filename)

    @staticmethod
    def delete_file(filename):
        """
        Delete a file.

        Args:
            filename (str): Name of the file to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"File deleted: {filename}")
                return True
            else:
                print(f"File not found: {filename}")
                return False
        except Exception as e:
            print(f"Error deleting file '{filename}': {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Create text file
    FileUtils.create_file('test.txt', 'This is a test file')

    # Create JSON file
    FileUtils.create_file('test.json', {'name': 'John', 'age': 30, 'city': 'New York'})

    # Create XML file
    FileUtils.create_file('test.xml', {'person': {'name': 'John', 'age': '30'}})

    # Create log file
    FileUtils.create_file('test.log', 'Log entry 1\n')

    # Create CSV file
    FileUtils.create_file('test.csv', 'Name,Age,City\nJohn,30,New York\n')

    # Create file in subdirectory
    FileUtils.create_file('output/data.txt', 'Data in subdirectory')

    # Append to file
    FileUtils.append_to_file('test.log', 'Log entry 2\n')

    # Read file
    content = FileUtils.read_file('test.txt')
    print(f"Content: {content}")

    # Check if file exists
    exists = FileUtils.file_exists('test.txt')
    print(f"File exists: {exists}")

    # Delete file
    FileUtils.delete_file('test.txt')
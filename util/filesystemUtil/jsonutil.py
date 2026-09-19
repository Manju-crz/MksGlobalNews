import json
import os


class JsonUtil:
    """Utility class for JSON file operations"""

    @staticmethod
    def replace_json_content(filepath, new_content):
        """
        Replace JSON content in a file with new JSON content.
        If the file doesn't exist yet, this method creates it.

        Args:
            filepath (str): Path to the JSON file
            new_content (dict or list): New JSON content to write

        Returns:
            bool: True if successful, False otherwise

        Examples:
            # Replace JSON content in a file
            new_data = {'key': 'value', 'items': [1, 2, 3]}
            JsonUtil.replace_json_content('data.json', new_data)
        """
        try:
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)

            # Write new content, creating the file if it doesn't already exist
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(new_content, f, indent=2, ensure_ascii=False)

            print(f"Successfully wrote JSON content to: {filepath}")
            return True

        except Exception as e:
            print(f"Error replacing JSON content: {str(e)}")
            return False

    @staticmethod
    def read_json_content(filepath):
        """
        Read JSON content from a file.

        Args:
            filepath (str): Path to the JSON file

        Returns:
            dict or list: JSON content, or None if error

        Examples:
            # Read JSON content
            data = JsonUtil.read_json_content('data.json')
        """
        try:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)

            print(f"Successfully read JSON content from: {filepath}")
            return content

        except Exception as e:
            print(f"Error reading JSON content: {str(e)}")
            return None

    @staticmethod
    def merge_json_content(filepath, new_content, overwrite_keys=True):
        """
        Merge new JSON content with existing content in a file.

        Args:
            filepath (str): Path to the JSON file
            new_content (dict): New JSON content to merge
            overwrite_keys (bool): If True, new values overwrite existing keys.
                                   If False, existing keys are preserved (default: True)

        Returns:
            bool: True if successful, False otherwise

        Examples:
            # Merge new content (overwrite existing keys)
            new_data = {'key2': 'new_value'}
            JsonUtil.merge_json_content('data.json', new_data)

            # Merge without overwriting existing keys
            JsonUtil.merge_json_content('data.json', new_data, overwrite_keys=False)
        """
        try:
            # Read existing content
            existing_content = JsonUtil.read_json_content(filepath)

            if existing_content is None:
                print("Creating new file with provided content")
                existing_content = {}

            if not isinstance(existing_content, dict):
                print("Existing content is not a dictionary. Cannot merge.")
                return False

            if not isinstance(new_content, dict):
                print("New content is not a dictionary. Cannot merge.")
                return False

            # Merge content
            if overwrite_keys:
                # New content overwrites existing keys
                merged_content = {**existing_content, **new_content}
            else:
                # Existing keys are preserved
                merged_content = {**new_content, **existing_content}

            # Write merged content
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(merged_content, f, indent=2, ensure_ascii=False)

            print(f"Successfully merged JSON content in: {filepath}")
            return True

        except Exception as e:
            print(f"Error merging JSON content: {str(e)}")
            return False

    @staticmethod
    def append_to_json_array(filepath, new_item):
        """
        Append a new item to a JSON array in a file.

        Args:
            filepath (str): Path to the JSON file
            new_item (any): Item to append to the array

        Returns:
            bool: True if successful, False otherwise

        Examples:
            # Append item to JSON array
            JsonUtil.append_to_json_array('items.json', {'id': 1, 'name': 'Item 1'})
        """
        try:
            # Read existing content
            existing_content = JsonUtil.read_json_content(filepath)

            if existing_content is None:
                print("Creating new file with array containing the item")
                existing_content = []

            if not isinstance(existing_content, list):
                print("Existing content is not an array. Cannot append.")
                return False

            # Append new item
            existing_content.append(new_item)

            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing_content, f, indent=2, ensure_ascii=False)

            print(f"Successfully appended item to JSON array in: {filepath}")
            return True

        except Exception as e:
            print(f"Error appending to JSON array: {str(e)}")
            return False

    @staticmethod
    def update_json_key(filepath, key_path, new_value):
        """
        Update a specific key in JSON content (supports nested keys).

        Args:
            filepath (str): Path to the JSON file
            key_path (str or list): Key path (e.g., 'user.name' or ['user', 'name'])
            new_value (any): New value for the key

        Returns:
            bool: True if successful, False otherwise

        Examples:
            # Update top-level key
            JsonUtil.update_json_key('data.json', 'name', 'New Name')

            # Update nested key
            JsonUtil.update_json_key('data.json', 'user.profile.age', 30)
            JsonUtil.update_json_key('data.json', ['user', 'profile', 'age'], 30)
        """
        try:
            # Read existing content
            content = JsonUtil.read_json_content(filepath)

            if content is None:
                print("File not found or empty")
                return False

            if not isinstance(content, dict):
                print("Content is not a dictionary. Cannot update key.")
                return False

            # Parse key path
            if isinstance(key_path, str):
                keys = key_path.split('.')
            else:
                keys = key_path

            # Navigate to the nested key
            current = content
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]

            # Update the final key
            current[keys[-1]] = new_value

            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

            print(f"Successfully updated key '{key_path}' in: {filepath}")
            return True

        except Exception as e:
            print(f"Error updating JSON key: {str(e)}")
            return False

    @staticmethod
    def delete_json_key(filepath, key_path):
        """
        Delete a specific key from JSON content (supports nested keys).

        Args:
            filepath (str): Path to the JSON file
            key_path (str or list): Key path to delete (e.g., 'user.name' or ['user', 'name'])

        Returns:
            bool: True if successful, False otherwise

        Examples:
            # Delete top-level key
            JsonUtil.delete_json_key('data.json', 'old_key')

            # Delete nested key
            JsonUtil.delete_json_key('data.json', 'user.profile.age')
        """
        try:
            # Read existing content
            content = JsonUtil.read_json_content(filepath)

            if content is None:
                print("File not found or empty")
                return False

            if not isinstance(content, dict):
                print("Content is not a dictionary. Cannot delete key.")
                return False

            # Parse key path
            if isinstance(key_path, str):
                keys = key_path.split('.')
            else:
                keys = key_path

            # Navigate to the parent of the key to delete
            current = content
            for key in keys[:-1]:
                if key not in current:
                    print(f"Key path not found: {key_path}")
                    return False
                current = current[key]

            # Delete the final key
            if keys[-1] in current:
                del current[keys[-1]]
            else:
                print(f"Key not found: {key_path}")
                return False

            # Write updated content
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)

            print(f"Successfully deleted key '{key_path}' from: {filepath}")
            return True

        except Exception as e:
            print(f"Error deleting JSON key: {str(e)}")
            return False

    @staticmethod
    def validate_json_file(filepath):
        """
        Validate if a file contains valid JSON.

        Args:
            filepath (str): Path to the JSON file

        Returns:
            bool: True if valid JSON, False otherwise

        Examples:
            # Validate JSON file
            is_valid = JsonUtil.validate_json_file('data.json')
        """
        try:
            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                json.load(f)

            print(f"Valid JSON file: {filepath}")
            return True

        except json.JSONDecodeError as e:
            print(f"Invalid JSON in file {filepath}: {str(e)}")
            return False

        except Exception as e:
            print(f"Error validating JSON file: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    print("=== JsonUtil Examples ===\n")

    test_file = "test_data.json"

    # Example 1: Replace JSON content
    print("--- Replace JSON Content ---")
    new_data = {
        'name': 'John Doe',
        'age': 30,
        'city': 'New York',
        'hobbies': ['reading', 'coding']
    }
    JsonUtil.replace_json_content(test_file, new_data)
    print()

    # Example 2: Read JSON content
    print("--- Read JSON Content ---")
    content = JsonUtil.read_json_content(test_file)
    print(f"Content: {content}\n")

    # Example 3: Merge JSON content
    print("--- Merge JSON Content ---")
    merge_data = {'age': 31, 'country': 'USA'}
    JsonUtil.merge_json_content(test_file, merge_data)
    print()

    # Example 4: Update specific key
    print("--- Update JSON Key ---")
    JsonUtil.update_json_key(test_file, 'age', 32)
    print()

    # Example 5: Validate JSON file
    print("--- Validate JSON File ---")
    is_valid = JsonUtil.validate_json_file(test_file)
    print(f"Is valid: {is_valid}\n")

    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"Cleaned up test file: {test_file}")
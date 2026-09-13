import os
from datetime import datetime
from pathlib import Path


class DirectoryUtil:
    """Utility class for directory operations"""

    @staticmethod
    def get_latest_file(directory_path, file_extension='.json', timestamp_format='%Y_%m_%d_%H_%M'):
        """
        Get the latest file from a directory based on timestamp in filename.

        Args:
            directory_path (str): Path to the directory to search
            file_extension (str): File extension to filter (e.g., '.json', '.txt', '.xml')
            timestamp_format (str): Format of timestamp in filename (default: '%Y_%m_%d_%H_%M')

        Returns:
            str: Full path to the latest file, or None if no files found

        Examples:
            # Get latest JSON file from dumps folder
            latest = DirectoryUtil.get_latest_file('dumps', '.json')
            # Returns: 'dumps/2026_08_14_00_15.json'

            # Get latest XML file
            latest = DirectoryUtil.get_latest_file('dumps', '.xml')

            # Get latest file with custom timestamp format
            latest = DirectoryUtil.get_latest_file('dumps', '.json', '%Y%m%d_%H%M%S')
        """
        try:
            # Check if directory exists
            if not os.path.exists(directory_path):
                print(f"Directory not found: {directory_path}")
                return None

            # Get all files with the specified extension
            files = [f for f in os.listdir(directory_path)
                     if f.endswith(file_extension) and os.path.isfile(os.path.join(directory_path, f))]

            if not files:
                print(f"No {file_extension} files found in {directory_path}")
                return None

            # Parse timestamps and find the latest file
            latest_file = None
            latest_timestamp = None

            for filename in files:
                try:
                    # Remove file extension to get timestamp
                    timestamp_str = filename.replace(file_extension, '')

                    # Parse timestamp
                    file_timestamp = datetime.strptime(timestamp_str, timestamp_format)

                    # Check if this is the latest file
                    if latest_timestamp is None or file_timestamp > latest_timestamp:
                        latest_timestamp = file_timestamp
                        latest_file = filename

                except ValueError:
                    # Skip files that don't match the timestamp format
                    print(f"Skipping file with invalid timestamp format: {filename}")
                    continue

            if latest_file:
                full_path = os.path.join(directory_path, latest_file)
                print(f"Latest file found: {full_path}")
                return full_path
            else:
                print(f"No files with valid timestamp format found in {directory_path}")
                return None

        except Exception as e:
            print(f"Error getting latest file: {str(e)}")
            return None

    @staticmethod
    def get_all_files_sorted(directory_path, file_extension='.json', timestamp_format='%Y_%m_%d_%H_%M', ascending=False):
        """
        Get all files from a directory sorted by timestamp in filename.

        Args:
            directory_path (str): Path to the directory to search
            file_extension (str): File extension to filter (e.g., '.json', '.txt', '.xml')
            timestamp_format (str): Format of timestamp in filename (default: '%Y_%m_%d_%H_%M')
            ascending (bool): If True, sort oldest to newest. If False, sort newest to oldest (default)

        Returns:
            list: List of full file paths sorted by timestamp

        Examples:
            # Get all JSON files sorted (newest first)
            files = DirectoryUtil.get_all_files_sorted('dumps', '.json')
            # Returns: ['dumps/2026_08_14_00_15.json', 'dumps/2026_08_14_00_10.json', ...]

            # Get all files sorted oldest first
            files = DirectoryUtil.get_all_files_sorted('dumps', '.json', ascending=True)
        """
        try:
            # Check if directory exists
            if not os.path.exists(directory_path):
                print(f"Directory not found: {directory_path}")
                return []

            # Get all files with the specified extension
            files = [f for f in os.listdir(directory_path)
                     if f.endswith(file_extension) and os.path.isfile(os.path.join(directory_path, f))]

            if not files:
                print(f"No {file_extension} files found in {directory_path}")
                return []

            # Parse timestamps and create list of (timestamp, filename) tuples
            file_list = []

            for filename in files:
                try:
                    # Remove file extension to get timestamp
                    timestamp_str = filename.replace(file_extension, '')

                    # Parse timestamp
                    file_timestamp = datetime.strptime(timestamp_str, timestamp_format)

                    # Add to list
                    file_list.append((file_timestamp, filename))

                except ValueError:
                    # Skip files that don't match the timestamp format
                    print(f"Skipping file with invalid timestamp format: {filename}")
                    continue

            # Sort by timestamp
            file_list.sort(key=lambda x: x[0], reverse=not ascending)

            # Return full paths
            sorted_files = [os.path.join(directory_path, filename) for _, filename in file_list]

            print(f"Found {len(sorted_files)} files in {directory_path}")
            return sorted_files

        except Exception as e:
            print(f"Error getting sorted files: {str(e)}")
            return []

    @staticmethod
    def get_oldest_file(directory_path, file_extension='.json', timestamp_format='%Y_%m_%d_%H_%M'):
        """
        Get the oldest file from a directory based on timestamp in filename.

        Args:
            directory_path (str): Path to the directory to search
            file_extension (str): File extension to filter (e.g., '.json', '.txt', '.xml')
            timestamp_format (str): Format of timestamp in filename (default: '%Y_%m_%d_%H_%M')

        Returns:
            str: Full path to the oldest file, or None if no files found

        Examples:
            # Get oldest JSON file from dumps folder
            oldest = DirectoryUtil.get_oldest_file('dumps', '.json')
            # Returns: 'dumps/2026_08_13_00_00.json'
        """
        try:
            # Check if directory exists
            if not os.path.exists(directory_path):
                print(f"Directory not found: {directory_path}")
                return None

            # Get all files with the specified extension
            files = [f for f in os.listdir(directory_path)
                     if f.endswith(file_extension) and os.path.isfile(os.path.join(directory_path, f))]

            if not files:
                print(f"No {file_extension} files found in {directory_path}")
                return None

            # Parse timestamps and find the oldest file
            oldest_file = None
            oldest_timestamp = None

            for filename in files:
                try:
                    # Remove file extension to get timestamp
                    timestamp_str = filename.replace(file_extension, '')

                    # Parse timestamp
                    file_timestamp = datetime.strptime(timestamp_str, timestamp_format)

                    # Check if this is the oldest file
                    if oldest_timestamp is None or file_timestamp < oldest_timestamp:
                        oldest_timestamp = file_timestamp
                        oldest_file = filename

                except ValueError:
                    # Skip files that don't match the timestamp format
                    print(f"Skipping file with invalid timestamp format: {filename}")
                    continue

            if oldest_file:
                full_path = os.path.join(directory_path, oldest_file)
                print(f"Oldest file found: {full_path}")
                return full_path
            else:
                print(f"No files with valid timestamp format found in {directory_path}")
                return None

        except Exception as e:
            print(f"Error getting oldest file: {str(e)}")
            return None

    @staticmethod
    def delete_old_files(directory_path, keep_count=5, file_extension='.json', timestamp_format='%Y_%m_%d_%H_%M'):
        """
        Delete old files from a directory, keeping only the specified number of latest files.

        Args:
            directory_path (str): Path to the directory
            keep_count (int): Number of latest files to keep (default: 5)
            file_extension (str): File extension to filter (e.g., '.json', '.txt', '.xml')
            timestamp_format (str): Format of timestamp in filename (default: '%Y_%m_%d_%H_%M')

        Returns:
            int: Number of files deleted

        Examples:
            # Keep only the 5 latest JSON files, delete the rest
            deleted = DirectoryUtil.delete_old_files('dumps', keep_count=5, file_extension='.json')
            # Returns: 3 (if 3 files were deleted)
        """
        try:
            # Get all files sorted (newest first)
            sorted_files = DirectoryUtil.get_all_files_sorted(
                directory_path, file_extension, timestamp_format, ascending=False
            )

            if len(sorted_files) <= keep_count:
                print(f"No files to delete. Found {len(sorted_files)} files, keeping {keep_count}")
                return 0

            # Files to delete (all files after keep_count)
            files_to_delete = sorted_files[keep_count:]

            deleted_count = 0
            for filepath in files_to_delete:
                try:
                    os.remove(filepath)
                    print(f"Deleted: {filepath}")
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {filepath}: {str(e)}")

            print(f"Deleted {deleted_count} old files, kept {keep_count} latest files")
            return deleted_count

        except Exception as e:
            print(f"Error deleting old files: {str(e)}")
            return 0


# Example usage
if __name__ == "__main__":
    print("=== DirectoryUtil Examples ===\n")

    # Example directory path
    dumps_dir = "dumps"

    # Get latest JSON file
    print("--- Get Latest File ---")
    latest_json = DirectoryUtil.get_latest_file(dumps_dir, '.json')
    if latest_json:
        print(f"Latest JSON file: {latest_json}\n")

    # Get latest XML file
    latest_xml = DirectoryUtil.get_latest_file(dumps_dir, '.xml')
    if latest_xml:
        print(f"Latest XML file: {latest_xml}\n")

    # Get all files sorted (newest first)
    print("--- Get All Files Sorted (Newest First) ---")
    all_files = DirectoryUtil.get_all_files_sorted(dumps_dir, '.json')
    for i, filepath in enumerate(all_files[:3], 1):  # Show first 3
        print(f"{i}. {filepath}")
    print()

    # Get all files sorted (oldest first)
    print("--- Get All Files Sorted (Oldest First) ---")
    all_files_asc = DirectoryUtil.get_all_files_sorted(dumps_dir, '.json', ascending=True)
    for i, filepath in enumerate(all_files_asc[:3], 1):  # Show first 3
        print(f"{i}. {filepath}")
    print()

    # Get oldest file
    print("--- Get Oldest File ---")
    oldest_json = DirectoryUtil.get_oldest_file(dumps_dir, '.json')
    if oldest_json:
        print(f"Oldest JSON file: {oldest_json}\n")

    # Delete old files (keep only 5 latest)
    print("--- Delete Old Files (Keep 5 Latest) ---")
    # Uncomment to actually delete files
    # deleted = DirectoryUtil.delete_old_files(dumps_dir, keep_count=5, file_extension='.json')
    # print(f"Deleted {deleted} files\n")
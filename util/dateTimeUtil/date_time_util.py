from datetime import datetime


class DateTimeUtil:
    """Utility class for date and time operations"""

    @staticmethod
    def get_timestamp_string(format_type='filename'):
        """
        Generate a timestamp string in various formats.

        Args:
            format_type (str): Type of format to return
                - 'filename': Returns yyyy_MM_dd_HH_mm (default)
                - 'readable': Returns yyyy-MM-dd HH:mm:ss
                - 'date_only': Returns yyyy-MM-dd
                - 'time_only': Returns HH:mm:ss
                - 'custom': Allows custom format (use with custom_format parameter)

        Returns:
            str: Formatted timestamp string

        Examples:
            # Get filename-friendly timestamp
            DateTimeUtil.get_timestamp_string()
            # Returns: '2026_08_14_00_01'

            # Get readable timestamp
            DateTimeUtil.get_timestamp_string('readable')
            # Returns: '2026-08-14 00:01:30'
        """
        now = datetime.now()

        if format_type == 'filename':
            return now.strftime('%Y_%m_%d_%H_%M')
        elif format_type == 'readable':
            return now.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date_only':
            return now.strftime('%Y-%m-%d')
        elif format_type == 'time_only':
            return now.strftime('%H:%M:%S')
        else:
            # Default to filename format
            return now.strftime('%Y_%m_%d_%H_%M')

    @staticmethod
    def get_custom_timestamp(format_string):
        """
        Generate a timestamp string with custom format.

        Args:
            format_string (str): Custom strftime format string
                Examples:
                - "%Y_%m_%d_%H_%M_%S" for yyyy_MM_dd_HH_mm_ss
                - "%Y%m%d" for yyyyMMdd
                - "%d-%m-%Y" for dd-mm-yyyy

        Returns:
            str: Formatted timestamp string

        Examples:
            DateTimeUtil.get_custom_timestamp('%Y_%m_%d_%H_%M_%S')
            # Returns: '2026_08_14_00_01_30'
        """
        now = datetime.now()
        return now.strftime(format_string)

    @staticmethod
    def get_timestamp_with_milliseconds():
        """
        Generate a timestamp string with milliseconds.
        Format: yyyy_MM_dd_HH_mm_ss_fff

        Returns:
            str: Timestamp with milliseconds

        Examples:
            DateTimeUtil.get_timestamp_with_milliseconds()
            # Returns: '2026_08_14_00_01_30_123'
        """
        now = datetime.now()
        return now.strftime('%Y_%m_%d_%H_%M_%S_%f')[:-3]  # Remove last 3 digits to get milliseconds

    @staticmethod
    def get_date_string():
        """
        Get current date string in yyyy_MM_dd format.

        Returns:
            str: Date string

        Examples:
            DateTimeUtil.get_date_string()
            # Returns: '2026_08_14'
        """
        now = datetime.now()
        return now.strftime('%Y_%m_%d')

    @staticmethod
    def get_time_string():
        """
        Get current time string in HH_mm_ss format.

        Returns:
            str: Time string

        Examples:
            DateTimeUtil.get_time_string()
            # Returns: '00_01_30'
        """
        now = datetime.now()
        return now.strftime('%H_%M_%S')

    @staticmethod
    def get_timestamp_for_specific_time(hour=0, minute=0, second=0, format_type='filename'):
        """
        Generate a timestamp string for a specific time of today's date.

        Args:
            hour (int): Hour (0-23), default: 0
            minute (int): Minute (0-59), default: 0
            second (int): Second (0-59), default: 0
            format_type (str): Format type ('filename', 'readable', etc.)

        Returns:
            str: Formatted timestamp string for the specified time

        Examples:
            # Get timestamp for 1 AM today
            DateTimeUtil.get_timestamp_for_specific_time(hour=1)
            # Returns: '2026_08_14_01_00'

            # Get timestamp for 1:30 AM today
            DateTimeUtil.get_timestamp_for_specific_time(hour=1, minute=30)
            # Returns: '2026_08_14_01_30'

            # Get timestamp for 11:45:30 PM today
            DateTimeUtil.get_timestamp_for_specific_time(hour=23, minute=45, second=30)
            # Returns: '2026_08_14_23_45'
        """
        now = datetime.now()
        specific_time = now.replace(hour=hour, minute=minute, second=second, microsecond=0)

        if format_type == 'filename':
            return specific_time.strftime('%Y_%m_%d_%H_%M')
        elif format_type == 'readable':
            return specific_time.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date_only':
            return specific_time.strftime('%Y-%m-%d')
        elif format_type == 'time_only':
            return specific_time.strftime('%H:%M:%S')
        else:
            return specific_time.strftime('%Y_%m_%d_%H_%M')

    @staticmethod
    def get_timestamp_for_specific_date(
            year=None, month=None, day=None,
            hour=0, minute=0, second=0,
            format_type='filename'):
        """
        Generate a timestamp string for a specific date and time.

        Args:
            year (int): Year (if None, uses current year)
            month (int): Month (1-12, if None, uses current month)
            day (int): Day (1-31, if None, uses current day)
            hour (int): Hour (0-23), default: 0
            minute (int): Minute (0-59), default: 0
            second (int): Second (0-59), default: 0
            format_type (str): Format type ('filename', 'readable', etc.)

        Returns:
            str: Formatted timestamp string for the specified date and time

        Examples:
            # Get timestamp for January 15, 2026 at 1 AM
            DateTimeUtil.get_timestamp_for_specific_date(year=2026, month=1, day=15, hour=1)
            # Returns: '2026_01_15_01_00'

            # Get timestamp for 15th of current month at 2:30 PM
            DateTimeUtil.get_timestamp_for_specific_date(day=15, hour=14, minute=30)
            # Returns: '2026_08_15_14_30'
        """
        now = datetime.now()

        # Use current values if not provided
        year = year if year is not None else now.year
        month = month if month is not None else now.month
        day = day if day is not None else now.day

        specific_datetime = datetime(year, month, day, hour, minute, second)

        if format_type == 'filename':
            return specific_datetime.strftime('%Y_%m_%d_%H_%M')
        elif format_type == 'readable':
            return specific_datetime.strftime('%Y-%m-%d %H:%M:%S')
        elif format_type == 'date_only':
            return specific_datetime.strftime('%Y-%m-%d')
        elif format_type == 'time_only':
            return specific_datetime.strftime('%H:%M:%S')
        else:
            return specific_datetime.strftime('%Y_%m_%d_%H_%M')

    @staticmethod
    def parse_timestamp_string(timestamp_str, format_string='%Y_%m_%d_%H_%M'):
        """
        Parse a timestamp string back to datetime object.

        Args:
            timestamp_str (str): Timestamp string to parse
            format_string (str): Format of the timestamp string (default: '%Y_%m_%d_%H_%M')

        Returns:
            datetime: Parsed datetime object or None if parsing fails

        Examples:
            DateTimeUtil.parse_timestamp_string('2026_08_14_00_01')
            # Returns: datetime(2026, 8, 14, 0, 1)
        """
        try:
            return datetime.strptime(timestamp_str, format_string)
        except Exception as e:
            print(f"Error parsing timestamp: {str(e)}")
            return None


# Example usage
if __name__ == "__main__":
    print("=== DateTimeUtil Examples ===\n")

    # Get filename-friendly timestamp (yyyy_MM_dd_HH_mm)
    print(f"Filename timestamp: {DateTimeUtil.get_timestamp_string()}")
    print(f"Filename timestamp (explicit): {DateTimeUtil.get_timestamp_string('filename')}")

    # Get readable timestamp
    print(f"Readable timestamp: {DateTimeUtil.get_timestamp_string('readable')}")

    # Get date only
    print(f"Date only: {DateTimeUtil.get_timestamp_string('date_only')}")

    # Get time only
    print(f"Time only: {DateTimeUtil.get_timestamp_string('time_only')}")

    # Get custom format
    print(f"Custom format: {DateTimeUtil.get_custom_timestamp('%Y%m%d_%H%M%S')}")

    # Get timestamp with milliseconds
    print(f"With milliseconds: {DateTimeUtil.get_timestamp_with_milliseconds()}")

    # Get date string
    print(f"Date string: {DateTimeUtil.get_date_string()}")

    # Get time string
    print(f"Time string: {DateTimeUtil.get_time_string()}")

    # Parse timestamp
    timestamp = DateTimeUtil.get_timestamp_string()
    parsed = DateTimeUtil.parse_timestamp_string(timestamp)
    print(f"\nParsed timestamp: {parsed}")

    # Get timestamp for specific time of today
    print(f"\n--- Specific Time Examples ---")
    print(f"1 AM today: {DateTimeUtil.get_timestamp_for_specific_time(hour=1)}")
    print(f"1:30 AM today: {DateTimeUtil.get_timestamp_for_specific_time(hour=1, minute=30)}")
    print(f"2:45 PM today: {DateTimeUtil.get_timestamp_for_specific_time(hour=14, minute=45)}")
    print(f"11:59 PM today: {DateTimeUtil.get_timestamp_for_specific_time(hour=23, minute=59)}")

    # Get timestamp for specific date and time
    print(f"\n--- Specific Date Examples ---")
    print(f"Jan 15, 2026 at 1 AM: {DateTimeUtil.get_timestamp_for_specific_date(year=2026, month=1, day=15, hour=1)}")
    print(f"15th of current month at 2:30 PM: {DateTimeUtil.get_timestamp_for_specific_date(day=15, hour=14, minute=30)}")

    # Example: Generate filename with timestamp
    filename = f"news_data_{DateTimeUtil.get_timestamp_string()}.json"
    print(f"\nExample filename: {filename}")

    # Example: Generate filename with 1 AM timestamp
    filename_1am = f"news_data_{DateTimeUtil.get_timestamp_for_specific_time(hour=1)}.json"
    print(f"Example filename (1 AM): {filename_1am}")
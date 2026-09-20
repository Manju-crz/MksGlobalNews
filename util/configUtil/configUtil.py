import os
import json

# Get project root relative to this file
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ConfigUtil:
    """Utility class for reading configuration settings"""

    @staticmethod
    def get_scraper_config():
        """
        Read scraper configuration from config.json file.

        Returns:
            dict: Configuration dictionary with scraper settings
        """
        try:
            config_path = os.path.join(PROJECT_ROOT, "data", "config.json")

            if not os.path.exists(config_path):
                print(f"Config file not found: {config_path}")
                # Return default configuration
                return {
                    "scraper_settings": {
                        "time_limit_hours": 6,
                        "include_minutes_ago": True
                    }
                }

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            return config

        except Exception as e:
            print(f"Error reading config file: {str(e)}")
            # Return default configuration on error
            return {
                "scraper_settings": {
                    "time_limit_hours": 6,
                    "include_minutes_ago": True
                }
            }

    @staticmethod
    def get_time_limit_hours():
        """
        Get the time limit in hours for filtering recent news.

        Returns:
            int: Time limit in hours (default: 6)
        """
        config = ConfigUtil.get_scraper_config()
        return config.get("scraper_settings", {}).get("time_limit_hours", 6)

    @staticmethod
    def should_include_minutes_ago():
        """
        Check if minutes-ago articles should be included.

        Returns:
            bool: True if minutes-ago should be included (default: True)
        """
        config = ConfigUtil.get_scraper_config()
        return config.get("scraper_settings", {}).get("include_minutes_ago", True)


if __name__ == "__main__":
    # Test the configuration utility
    print("=== ConfigUtil Test ===")
    print(f"Project root: {PROJECT_ROOT}")
    config = ConfigUtil.get_scraper_config()
    print(f"Full config: {config}")
    print(f"Time limit hours: {ConfigUtil.get_time_limit_hours()}")
    print(f"Include minutes ago: {ConfigUtil.should_include_minutes_ago()}")
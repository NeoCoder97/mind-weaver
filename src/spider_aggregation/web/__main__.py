"""
Main entry point for mind-weaver web application.
"""

from spider_aggregation.web.app import create_app
from spider_aggregation.config import get_config


def main():
    """Main entry point for the web application."""
    config = get_config()

    # Print startup message
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           MindWeaver v{config.version or "0.3.0"}                    ║
║                                                              ║
║   Web UI: http://{config.web.host}:{config.web.port}              ║
║                                                              ║
║   Press Ctrl+C to stop the server                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    app = create_app(debug=config.web.debug)
    app.run(
        host=config.web.host,
        port=config.web.port,
        debug=config.web.debug,
    )


if __name__ == "__main__":
    main()

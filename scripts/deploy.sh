#!/bin/bash
# MindWeaver Deployment Script
# This script helps with deployment and setup tasks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Default values
DB_PATH="data/spider_aggregation.db"
BACKUP_DIR="data/backups"
LOG_DIR="data/logs"
VENV_DIR=".venv"

# Parse command line arguments
COMMAND=""
ENVIRONMENT="development"

while [[ $# -gt 0 ]]; do
    case $1 in
        install)
            COMMAND="install"
            shift
            ;;
        init)
            COMMAND="init"
            shift
            ;;
        start)
            COMMAND="start"
            shift
            ;;
        stop)
            COMMAND="stop"
            shift
            ;;
        restart)
            COMMAND="restart"
            shift
            ;;
        backup)
            COMMAND="backup"
            shift
            ;;
        restore)
            COMMAND="restore"
            BACKUP_FILE="$2"
            shift 2
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        logs)
            COMMAND="logs"
            shift
            ;;
        test)
            COMMAND="test"
            shift
            ;;
        clean)
            COMMAND="clean"
            shift
            ;;
        --production)
            ENVIRONMENT="production"
            shift
            ;;
        --help|-h)
            echo "MindWeaver Deployment Script"
            echo ""
            echo "Usage: $0 [COMMAND] [OPTIONS]"
            echo ""
            echo "Commands:"
            echo "  install      Install dependencies and setup environment"
            echo "  init         Initialize database"
            echo "  start        Start the scheduler daemon"
            echo "  stop         Stop the scheduler daemon"
            echo "  restart      Restart the scheduler daemon"
            echo "  backup       Backup database"
            echo "  restore      Restore database from backup"
            echo "  status       Show service status"
            echo "  logs         Show recent logs"
            echo "  test         Run tests"
            echo "  clean        Clean temporary files"
            echo ""
            echo "Options:"
            echo "  --production    Use production environment"
            echo "  --help, -h      Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 install"
            echo "  $0 init"
            echo "  $0 start --production"
            echo "  $0 backup"
            echo "  $0 restore data/backups/backup_20260201.db"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if uv is installed
check_uv() {
    if ! command -v uv &> /dev/null; then
        print_error "uv is not installed. Installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        print_success "uv installed"
    fi
}

# Install dependencies
install_deps() {
    print_info "Installing dependencies..."
    check_uv
    uv sync
    print_success "Dependencies installed"
}

# Initialize database
init_database() {
    print_info "Initializing database..."

    # Create directories
    mkdir -p "$(dirname "$DB_PATH")"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$LOG_DIR"

    # Initialize database
    uv run mind-weaver init

    print_success "Database initialized at: $DB_PATH"
}

# Start scheduler
start_scheduler() {
    print_info "Starting scheduler..."

    # Check if PID file exists
    if [ -f "data/scheduler.pid" ]; then
        PID=$(cat data/scheduler.pid)
        if ps -p $PID > /dev/null 2>&1; then
            print_warning "Scheduler is already running (PID: $PID)"
            exit 0
        else
            print_warning "Removing stale PID file"
            rm -f data/scheduler.pid
        fi
    fi

    # Start scheduler in background
    if [ "$ENVIRONMENT" = "production" ]; then
        nohup uv run mind-weaver start >> "$LOG_DIR/scheduler.log" 2>&1 &
        echo $! > data/scheduler.pid
        print_success "Scheduler started in production mode (PID: $!)"
    else
        print_warning "Starting in foreground (use Ctrl+C to stop)"
        print_info "Use --production for background mode"
        uv run mind-weaver start
    fi
}

# Stop scheduler
stop_scheduler() {
    print_info "Stopping scheduler..."

    if [ ! -f "data/scheduler.pid" ]; then
        print_warning "Scheduler is not running (no PID file found)"
        exit 0
    fi

    PID=$(cat data/scheduler.pid)

    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        sleep 2

        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            print_warning "Force stopping scheduler..."
            kill -9 $PID
        fi

        rm -f data/scheduler.pid
        print_success "Scheduler stopped"
    else
        print_warning "Scheduler is not running (stale PID file)"
        rm -f data/scheduler.pid
    fi
}

# Restart scheduler
restart_scheduler() {
    print_info "Restarting scheduler..."
    stop_scheduler
    sleep 1
    start_scheduler
}

# Backup database
backup_database() {
    print_info "Backing up database..."

    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"

    # Create backup filename with timestamp
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).db"

    if [ -f "$DB_PATH" ]; then
        cp "$DB_PATH" "$BACKUP_FILE"
        print_success "Database backed up to: $BACKUP_FILE"

        # Keep only last 10 backups
        cd "$BACKUP_DIR"
        ls -t backup_*.db | tail -n +11 | xargs -r rm --
        print_info "Old backups cleaned (keeping last 10)"
    else
        print_error "Database file not found: $DB_PATH"
        exit 1
    fi
}

# Restore database
restore_database() {
    if [ -z "$BACKUP_FILE" ]; then
        print_error "Please specify backup file"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi

    print_info "Restoring database from: $BACKUP_FILE"

    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    # Stop scheduler if running
    if [ -f "data/scheduler.pid" ]; then
        print_info "Stopping scheduler before restore..."
        stop_scheduler
    fi

    # Create backup of current database before restore
    if [ -f "$DB_PATH" ]; then
        print_info "Backing up current database..."
        cp "$DB_PATH" "$BACKUP_DIR/pre_restore_$(date +%Y%m%d_%H%M%S).db"
    fi

    # Restore database
    cp "$BACKUP_FILE" "$DB_PATH"
    print_success "Database restored from: $BACKUP_FILE"
}

# Show status
show_status() {
    print_info "MindWeaver Status"
    echo ""

    # Check if scheduler is running
    if [ -f "data/scheduler.pid" ]; then
        PID=$(cat data/scheduler.pid)
        if ps -p $PID > /dev/null 2>&1; then
            echo "Scheduler: Running (PID: $PID)"
        else
            echo "Scheduler: Not running (stale PID file)"
        fi
    else
        echo "Scheduler: Not running"
    fi

    # Database info
    if [ -f "$DB_PATH" ]; then
        DB_SIZE=$(du -h "$DB_PATH" | cut -f1)
        echo "Database: $DB_PATH ($DB_SIZE)"

        # Count feeds and entries
        FEED_COUNT=$(uv run python -c "from spider_aggregation.storage.database import DatabaseManager; from spider_aggregation.storage.repositories.feed_repo import FeedRepository; manager = DatabaseManager('$DB_PATH'); manager.init_db(); session = manager.session(); print(len(FeedRepository(session).list()))" 2>/dev/null || echo "?")
        ENTRY_COUNT=$(uv run python -c "from spider_aggregation.storage.database import DatabaseManager; from spider_aggregation.storage.repositories.entry_repo import EntryRepository; manager = DatabaseManager('$DB_PATH'); manager.init_db(); session = manager.session(); print(EntryRepository(session).count())" 2>/dev/null || echo "?")

        echo "  Feeds: $FEED_COUNT"
        echo "  Entries: $ENTRY_COUNT"
    else
        echo "Database: Not initialized"
    fi

    # Disk space
    echo ""
    echo "Disk Space:"
    df -h . | tail -1 | awk '{print "  Total: " $2 ", Used: " $3 ", Available: " $4}'
}

# Show logs
show_logs() {
    if [ -f "$LOG_DIR/scheduler.log" ]; then
        tail -n 50 "$LOG_DIR/scheduler.log"
    else
        # Find latest log file
        LATEST_LOG=$(ls -t "$LOG_DIR"/spider_*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ]; then
            tail -n 50 "$LATEST_LOG"
        else
            print_warning "No log files found"
        fi
    fi
}

# Run tests
run_tests() {
    print_info "Running tests..."
    uv run pytest tests/ -v --tb=short
    print_success "Tests completed"
}

# Clean temporary files
clean_temp() {
    print_info "Cleaning temporary files..."

    # Remove Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true

    # Remove coverage files
    rm -rf htmlcov/ .coverage 2>/dev/null || true

    # Remove build artifacts
    rm -rf build/ dist/ *.egg-info 2>/dev/null || true

    print_success "Temporary files cleaned"
}

# Main execution
case $COMMAND in
    install)
        install_deps
        ;;
    init)
        init_database
        ;;
    start)
        start_scheduler
        ;;
    stop)
        stop_scheduler
        ;;
    restart)
        restart_scheduler
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_temp
        ;;
    "")
        print_error "No command specified"
        echo "Use --help for usage information"
        exit 1
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        echo "Use --help for usage information"
        exit 1
        ;;
esac

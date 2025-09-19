"""
Clockodo MCP Server - Time tracking tools and resources for Claude Desktop.
Provides comprehensive integration with Clockodo API for time management.
"""

import json
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import FastMCP, Context
from clockodo_client import ClockodoClient, ClockodoAPIError


@dataclass
class AppContext:
    """Application context with Clockodo client."""
    clockodo: ClockodoClient


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    """Manage application lifecycle with Clockodo client initialization."""
    try:
        clockodo = ClockodoClient()
        yield AppContext(clockodo=clockodo)
    except Exception as e:
        print(f"Failed to initialize Clockodo client: {e}")
        raise


# Create FastMCP server with lifespan management
mcp = FastMCP("Clockodo Time Tracker", lifespan=app_lifespan)


# Core time tracking tools
@mcp.tool()
async def start_time_tracking(
    customer_name: str,
    project_name: Optional[str] = None,
    service_name: Optional[str] = None,
    description: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Start time tracking for a customer/project.

    Args:
        customer_name: Name of the customer
        project_name: Optional project name
        service_name: Optional service name
        description: Optional description text
    """
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Get customers to find ID
        customers = await clockodo.get_customers()
        customer = next((c for c in customers if customer_name.lower() in c["name"].lower()), None)
        if not customer:
            return f"Customer '{customer_name}' not found. Available customers: {', '.join([c['name'] for c in customers[:5]])}"

        customers_id = customer["id"]
        projects_id = None
        services_id = None

        # Find project if specified
        if project_name:
            projects = await clockodo.get_projects(customers_id)
            project = next((p for p in projects if project_name.lower() in p["name"].lower()), None)
            if project:
                projects_id = project["id"]
            else:
                return f"Project '{project_name}' not found for customer '{customer_name}'"

        # Find service if specified
        if service_name:
            services = await clockodo.get_services()
            service = next((s for s in services if service_name.lower() in s["name"].lower()), None)
            if service:
                services_id = service["id"]
            else:
                return f"Service '{service_name}' not found"

        # Start tracking
        result = await clockodo.start_clock(
            customers_id=customers_id,
            projects_id=projects_id,
            services_id=services_id,
            text=description
        )

        return f"✅ Time tracking started for {customer['name']}" + \
               (f" - {project_name}" if project_name else "") + \
               (f" ({service_name})" if service_name else "")

    except ClockodoAPIError as e:
        return f"❌ Error starting time tracking: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.tool()
async def stop_time_tracking(ctx: Context = None) -> str:
    """Stop current time tracking."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Check if there's a running entry
        running = await clockodo.get_clock()
        if not running:
            return "⏹️ No time tracking currently running"

        # Stop the clock
        result = await clockodo.stop_clock()

        # Calculate duration
        if running and "time_since" in running:
            start_time = datetime.fromisoformat(running["time_since"].replace("Z", "+00:00"))
            duration = datetime.now() - start_time.replace(tzinfo=None)
            hours = duration.total_seconds() / 3600

            return f"⏹️ Time tracking stopped. Duration: {hours:.2f} hours"

        return "⏹️ Time tracking stopped"

    except ClockodoAPIError as e:
        return f"❌ Error stopping time tracking: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.tool()
async def get_running_entry(ctx: Context = None) -> str:
    """Get current running time entry."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        running = await clockodo.get_clock()
        if not running:
            return "⏹️ No time tracking currently running"

        # Format running entry info
        customer_name = running.get("customers_name", "Unknown")
        project_name = running.get("projects_name", "")
        service_name = running.get("services_name", "")
        description = running.get("text", "")
        start_time = running.get("time_since", "")

        info = f"⏰ Currently tracking: {customer_name}"
        if project_name:
            info += f" - {project_name}"
        if service_name:
            info += f" ({service_name})"
        if description:
            info += f"\nDescription: {description}"
        if start_time:
            try:
                start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                duration = datetime.now() - start.replace(tzinfo=None)
                hours = duration.total_seconds() / 3600
                info += f"\nDuration: {hours:.2f} hours (started {start.strftime('%H:%M')})"
            except:
                info += f"\nStarted: {start_time}"

        return info

    except ClockodoAPIError as e:
        return f"❌ Error getting running entry: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.tool()
async def create_time_entry(
    customer_name: str,
    date_str: str,
    start_time: str,
    end_time: str,
    project_name: Optional[str] = None,
    service_name: Optional[str] = None,
    description: Optional[str] = None,
    ctx: Context = None
) -> str:
    """Create a manual time entry.

    Args:
        customer_name: Name of the customer
        date_str: Date in YYYY-MM-DD format
        start_time: Start time in HH:MM format
        end_time: End time in HH:MM format
        project_name: Optional project name
        service_name: Optional service name
        description: Optional description
    """
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Parse and validate datetime
        time_since = f"{date_str} {start_time}:00"
        time_until = f"{date_str} {end_time}:00"

        # Validate datetime format
        datetime.strptime(time_since, "%Y-%m-%d %H:%M:%S")
        datetime.strptime(time_until, "%Y-%m-%d %H:%M:%S")

        # Find customer
        customers = await clockodo.get_customers()
        customer = next((c for c in customers if customer_name.lower() in c["name"].lower()), None)
        if not customer:
            return f"Customer '{customer_name}' not found"

        customers_id = customer["id"]
        projects_id = None
        services_id = None

        # Find project if specified
        if project_name:
            projects = await clockodo.get_projects(customers_id)
            project = next((p for p in projects if project_name.lower() in p["name"].lower()), None)
            if project:
                projects_id = project["id"]

        # Find service if specified
        if service_name:
            services = await clockodo.get_services()
            service = next((s for s in services if service_name.lower() in s["name"].lower()), None)
            if service:
                services_id = service["id"]

        # Create entry
        result = await clockodo.create_entry(
            customers_id=customers_id,
            time_since=time_since,
            time_until=time_until,
            projects_id=projects_id,
            services_id=services_id,
            text=description
        )

        # Calculate duration
        start = datetime.strptime(time_since, "%Y-%m-%d %H:%M:%S")
        end = datetime.strptime(time_until, "%Y-%m-%d %H:%M:%S")
        duration = (end - start).total_seconds() / 3600

        return f"✅ Time entry created: {customer['name']} ({duration:.2f}h on {date_str})"

    except ValueError as e:
        return f"❌ Invalid date/time format: {e}"
    except ClockodoAPIError as e:
        return f"❌ Error creating entry: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


# Resources for data access
@mcp.resource("entries://{period}")
async def get_time_entries(period: str, ctx: Context = None) -> str:
    """Get time entries for a period (today, yesterday, week, month)."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Calculate date range based on period
        today = date.today()

        if period == "today":
            time_since = clockodo.format_date(today)
            time_until = clockodo.format_date_end(today)
        elif period == "yesterday":
            yesterday = today - timedelta(days=1)
            time_since = clockodo.format_date(yesterday)
            time_until = clockodo.format_date_end(yesterday)
        elif period == "week":
            # Current week (Monday to Sunday)
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            time_since = clockodo.format_date(monday)
            time_until = clockodo.format_date_end(sunday)
        elif period == "month":
            # Current month
            first_day = today.replace(day=1)
            next_month = first_day.replace(month=first_day.month + 1) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1)
            last_day = next_month - timedelta(days=1)
            time_since = clockodo.format_date(first_day)
            time_until = clockodo.format_date_end(last_day)
        else:
            return f"Invalid period '{period}'. Use: today, yesterday, week, month"

        entries = await clockodo.get_entries(time_since, time_until)

        if not entries:
            return f"No time entries found for {period}"

        # Get current user ID and filter entries
        current_user_id = await clockodo.get_current_user_id()
        user_entries = [entry for entry in entries if entry.get("users_id") == current_user_id]

        if not user_entries:
            return f"No time entries found for your user for {period}"

        # Format entries
        total_hours = 0
        result = f"📊 Time entries for {period}:\n\n"

        for entry in user_entries:
            customer = entry.get("customers_name", "Unknown")
            project = entry.get("projects_name", "")
            service = entry.get("services_name", "")
            text = entry.get("text", "")

            # Parse times
            try:
                start = datetime.fromisoformat(entry["time_since"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(entry["time_until"].replace("Z", "+00:00"))
                duration = (end - start).total_seconds() / 3600
                total_hours += duration

                result += f"• {start.strftime('%m/%d %H:%M')}-{end.strftime('%H:%M')} "
                result += f"{customer}"
                if project:
                    result += f" - {project}"
                if service:
                    result += f" ({service})"
                result += f" [{duration:.2f}h]"
                if text:
                    result += f"\n  📝 {text}"
                result += "\n"
            except:
                result += f"• {customer} - Invalid time format\n"

        result += f"\n⏱️ Total: {total_hours:.2f} hours"
        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting entries: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.resource("customers://all")
async def get_all_customers(ctx: Context = None) -> str:
    """Get all customers."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo
        customers = await clockodo.get_customers()

        if not customers:
            return "No customers found"

        result = "👥 Customers:\n\n"
        for customer in customers:
            result += f"• {customer['name']} (ID: {customer['id']})\n"

        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting customers: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.resource("projects://{customer_name}")
async def get_customer_projects(customer_name: str, ctx: Context = None) -> str:
    """Get projects for a specific customer."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Find customer
        customers = await clockodo.get_customers()
        customer = next((c for c in customers if customer_name.lower() in c["name"].lower()), None)
        if not customer:
            return f"Customer '{customer_name}' not found"

        projects = await clockodo.get_projects(customer["id"])

        if not projects:
            return f"No projects found for {customer['name']}"

        result = f"📁 Projects for {customer['name']}:\n\n"
        for project in projects:
            result += f"• {project['name']} (ID: {project['id']})\n"

        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting projects: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.resource("services://all")
async def get_all_services(ctx: Context = None) -> str:
    """Get all services."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo
        services = await clockodo.get_services()

        if not services:
            return "No services found"

        result = "🔧 Services:\n\n"
        for service in services:
            result += f"• {service['name']} (ID: {service['id']})\n"

        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting services: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


@mcp.resource("users://all")
async def get_all_users(ctx: Context = None) -> str:
    """Get all users."""
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo
        users = await clockodo.get_users()

        if not users:
            return "No users found"

        result = "👥 Users:\n\n"
        for user in users:
            status = "✅ Active" if user.get("active") else "❌ Inactive"
            result += f"• {user['name']} (ID: {user['id']})\n"
            result += f"  📧 {user.get('email', 'No email')}\n"
            result += f"  🎭 Role: {user.get('role', 'Unknown')} | Status: {status}\n\n"

        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting users: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"


# Quick summary tool
@mcp.tool()
async def get_work_summary(period: str = "week", ctx: Context = None) -> str:
    """Get work summary with total hours and breakdown by customer/project.

    Args:
        period: Period to summarize (today, yesterday, week, month)
    """
    try:
        clockodo = ctx.request_context.lifespan_context.clockodo

        # Calculate date range
        today = date.today()

        if period == "today":
            time_since = clockodo.format_date(today)
            time_until = clockodo.format_date_end(today)
        elif period == "yesterday":
            yesterday = today - timedelta(days=1)
            time_since = clockodo.format_date(yesterday)
            time_until = clockodo.format_date_end(yesterday)
        elif period == "week":
            monday = today - timedelta(days=today.weekday())
            sunday = monday + timedelta(days=6)
            time_since = clockodo.format_date(monday)
            time_until = clockodo.format_date_end(sunday)
        elif period == "month":
            first_day = today.replace(day=1)
            next_month = first_day.replace(month=first_day.month + 1) if first_day.month < 12 else first_day.replace(year=first_day.year + 1, month=1)
            last_day = next_month - timedelta(days=1)
            time_since = clockodo.format_date(first_day)
            time_until = clockodo.format_date_end(last_day)
        else:
            return f"Invalid period '{period}'"

        entries = await clockodo.get_entries(time_since, time_until)

        if not entries:
            return f"No time entries for {period}"

        # Get current user ID and filter entries
        current_user_id = await clockodo.get_current_user_id()
        user_entries = [entry for entry in entries if entry.get("users_id") == current_user_id]

        if not user_entries:
            return f"No time entries found for your user for {period}"

        # Group by customer and project
        summary = {}
        total_hours = 0

        for entry in user_entries:
            try:
                start = datetime.fromisoformat(entry["time_since"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(entry["time_until"].replace("Z", "+00:00"))
                duration = (end - start).total_seconds() / 3600
                total_hours += duration

                customer = entry.get("customers_name", "Unknown")
                project = entry.get("projects_name", "General")

                if customer not in summary:
                    summary[customer] = {}
                if project not in summary[customer]:
                    summary[customer][project] = 0
                summary[customer][project] += duration
            except:
                continue

        # Format summary
        result = f"📊 Work Summary ({period}):\n\n"
        result += f"⏱️ Total Hours: {total_hours:.2f}h\n\n"

        for customer, projects in summary.items():
            customer_total = sum(projects.values())
            result += f"👤 {customer}: {customer_total:.2f}h\n"
            for project, hours in projects.items():
                result += f"  📁 {project}: {hours:.2f}h\n"
            result += "\n"

        return result

    except ClockodoAPIError as e:
        return f"❌ Error getting summary: {e}"
    except Exception as e:
        return f"❌ Unexpected error: {e}"
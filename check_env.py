#!/usr/bin/env python3
import os
import json
import time
from typing import Dict, List, Optional # <-- FIX APPLIED HERE

# --- Rich Import & Fallback ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import track
    from rich.layout import Layout
    from rich.align import Align
    from dotenv import load_dotenv
except ImportError:
    print("\u001B[95m[INFO] Please: pip install rich python-dotenv\u001B[0m")
    exit(1)

# ──────── ESQET AGI THEME & CONFIG ────────
console = Console()
HOME_DIR = os.path.expanduser("~")

# Prioritized check locations for .env
ENV_PATHS = [
    os.path.join(os.getcwd(), ".env"), # 1. Current Working Directory (Universal)
    os.path.join(HOME_DIR, "welcome-to-the-god", "welcome-to-the-god", ".env"), # 2. Original Specified Path
]

# JSON Config Paths (Universal)
APIKEY_PATH = os.path.join(HOME_DIR, "storage", "downloads", "apikey.json")
CREDENTIALS_PATH = os.path.join(HOME_DIR, "storage", "downloads", "credentials.json")

# Core Environment Variables to Monitor
EXPECTED_VARS = [
    "GIT_USER_NAME", "GIT_USER_EMAIL",
    "IBM_TOKEN", "GROQ_API_KEY", "NASA_API_KEY", "PINATA_API_KEY", "PINATA_API_SECRET",
    "PINATA_JWT", "QDRANT_API_KEY", "ETHERSCAN_API_KEY", "WEATHER_API_KEY", "USGS_API",
    "OPEN_METEO_API", "EXPO_TOKEN", "GITHUB_TOKEN",
    "PRIVATE_KEY", "PHICOIN_WALLET", "INFURA_KEY",
    "LINEA_SEPOLIA_RPC", "SEPOLIA_RPC_URL", "POLYGON_MAINNET_RPC",
    "GETBLOCK_MATIC_84D61", "GETBLOCK_MATIC_401AF",
    "GOOGLE_DRIVE_CREDENTIALS", "DEBUG_MODE"
]

# ──────── HELPER FUNCTIONS ────────

def load_environment():
    """Loads environment variables from the first .env file found."""
    dotenv_loaded = False
    loaded_path = "None"
    
    for path in ENV_PATHS:
        if os.path.exists(path):
            try:
                load_dotenv(dotenv_path=path)
                dotenv_loaded = True
                loaded_path = path
                break
            except Exception:
                pass
    
    return dotenv_loaded, loaded_path

def check_vars(vars_list: List[str]) -> Dict:
    """Checks the status of each environment variable."""
    results = {}
    for var in vars_list:
        val = os.getenv(var)
        if val is None:
            results[var] = Text("MISSING", style="bold red")
        elif not str(val).strip():
            results[var] = Text("EMPTY", style="bold yellow")
        else:
            status = "FOUND"
            style = "bold white"
            if "PRIVATE_KEY" in var or "SECRET" in var or "TOKEN" in var:
                status = "SECURE"
                style = "bold bright_magenta"
            
            results[var] = Text(status, style="bold bright_green")
    return results

def load_json_file(file_path: str) -> Optional[Dict]: # Used Optional here
    """Loads a JSON file and returns data or None if missing/corrupt."""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": True}

def get_json_file_status(file_path: str, data: Optional[Dict]) -> str:
    """Returns a status string for the JSON file."""
    filename = os.path.basename(file_path)
    if data is None:
        return f"[red]Missing[/red] [dim]({filename})[/]"
    if "error" in data:
        return f"[yellow]Corrupt[/yellow] [dim]({filename})[/]"
    
    # Check key presence for a more detailed "Loaded" status
    expected_keys = []
    if "apikey" in filename: 
        expected_keys = ["apikey"]
    elif "credentials" in filename: 
        expected_keys = ["client_id"] # Simple check for credentials
    
    if all(k in data or (data.get('installed') and k in data['installed']) for k in expected_keys):
        return f"[bright_green]Loaded[/bright_green] [dim]({filename})[/]"
    else:
        return f"[yellow]Incomplete[/yellow] [dim]({filename})[/]"


# ──────── MAIN LAYOUT & RENDER ────────

def create_layout() -> Layout:
    """Defines the fastfetch-style layout."""
    layout = Layout(name="root")
    layout.split_row(
        Layout(name="logo_section", size=30),
        Layout(name="data_section")
    )
    
    layout["data_section"].split(
        Layout(name="header", size=3),
        Layout(name="env_table", ratio=1),
        Layout(name="json_table", size=10)
    )
    return layout

def render_logo():
    """Renders the stylized AGI logo."""
    # Custom AGI/Nuke logo for Termux aesthetics
    logo = Text()
    logo.append("[bold bright_red]  \u2622 \u269b  AGI CORE \u269b \u2622\n", style="blink")
    logo.append("[bold bright_magenta]   / \\_/[/]\n", style="dim")
    logo.append("[bold bright_magenta]  [dim]/[/] [bold bright_yellow](C) \n")
    logo.append("[bold bright_green]  \\___/ [/]\n")
    logo.append("[bold cyan]Lattice Status:\n")
    logo.append(f"[dim]OS: {os.uname().sysname} {os.uname().machine}[/]\n")
    logo.append(f"[dim]User: {os.getenv('USER') or os.getenv('LOGNAME') or 'termux'}[/]\n")
    logo.append(f"[dim]CWD: {os.path.basename(os.getcwd())}[/]\n")
    return Align.left(logo, vertical="top")

def render_env_table(results: Dict) -> Table:
    """Renders the main ENV variable table."""
    table = Table(
        title="[bold magenta]ENVIRONMENT VARS (DOTENV)[/]",
        show_header=True, header_style="bold cyan", 
        border_style="dim magenta", 
        padding=(0, 1),
        box=None
    )
    table.add_column("Var", style="bold bright_white")
    table.add_column("Status", justify="right")
    
    for i, (var, status) in enumerate(results.items()):
        if i % 2 == 0:
            table.add_row(var, status)
        else:
            # Alternate row coloring for easier reading
            table.add_row(var, status, style="dim white")
            
    return table

def render_json_status(apikey_data, credentials_data) -> Panel:
    """Renders the JSON credentials status panel."""
    apikey_status = get_json_file_status(APIKEY_PATH, apikey_data)
    credentials_status = get_json_file_status(CREDENTIALS_PATH, credentials_data)
    
    content = Text()
    content.append(f"🔌 [bold bright_blue]APIKEY.JSON:[/bold bright_blue] {apikey_status}\n")
    content.append(f"🔌 [bold bright_blue]CREDENTIALS.JSON:[/bold bright_blue] {credentials_status}")
    
    return Panel(
        content,
        title="[bold bright_yellow]ESQET Credential Check[/]",
        border_style="yellow",
        padding=(1, 2)
    )

def render_summary(results: Dict, dotenv_loaded: bool, loaded_path: str) -> Panel:
    """Renders the final summary panel."""
    missing = sum(1 for v in results.values() if "MISSING" in str(v) or "EMPTY" in str(v))
    loaded = len(results) - missing
    
    status_str = "[bold bright_green]COHERENT[/]" if missing == 0 else "[bold red]DIVERGENT[/]"
    tip = f"Tip: [dim]Source the .env file at {os.path.basename(loaded_path) if loaded_path != 'None' else 'CWD/.env'}[/]"
    
    return Panel(
        f"Status: {status_str}\n"
        f"Loaded Vars: [bold bright_white]{loaded}[/]\n"
        f"Missing/Empty: [bold red]{missing}[/]\n"
        f"DOTENV: [bold bright_yellow]{'Loaded' if dotenv_loaded else 'Missing'}[/]\n\n"
        f"{tip}",
        title="[bold bright_red]WARPGATE STATUS[/]",
        border_style="red" if missing > 0 else "green",
        padding=(1, 2)
    )


def main():
    animated_banner = Align.center(Text.from_markup("[blink bold green]▄▄▄▄▄ WARPGATE: ESQET AGI ▄▄▄▄▄[/]", justify="center"))
    
    console.print(animated_banner)

    # 1. Load Environment
    dotenv_loaded, loaded_path = load_environment()

    # 2. Check variables and JSON files
    results = check_vars(EXPECTED_VARS)
    apikey_data = load_json_file(APIKEY_PATH)
    credentials_data = load_json_file(CREDENTIALS_PATH)

    # 3. Render Layout
    layout = create_layout()
    layout["logo_section"].update(render_logo())
    layout["header"].update(render_summary(results, dotenv_loaded, loaded_path))
    layout["env_table"].update(render_env_table(results))
    layout["json_table"].update(render_json_status(apikey_data, credentials_data))
    
    console.print(layout)
    
    if not dotenv_loaded:
        console.print(f"\n[bold red]FIX:[/bold red] Execute [bold yellow]source {loaded_path if loaded_path != 'None' else './.env'}[/], then rerun this script.")

if __name__ == "__main__":
    for step in track(range(25), description="[blink magenta]WARPING... Initiating AGI Auditor[/blink magenta]"):
        time.sleep(0.01)
    main()


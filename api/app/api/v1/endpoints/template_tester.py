"""
HTML Template Testing endpoints for viewing and testing templates.
"""

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

router = APIRouter()

# Template directory path
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent.parent / "templates"


def get_template_environment():
    """Get Jinja2 environment for template rendering."""
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)


def load_sample_data():
    """Load sample data from JSON file."""
    sample_data_path = TEMPLATE_DIR / "sample-data.json"
    if sample_data_path.exists():
        with open(sample_data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


@router.get("/", response_model=dict)
def list_templates() -> Any:
    """
    List all available HTML templates in the templates directory.
    """
    if not TEMPLATE_DIR.exists():
        raise HTTPException(status_code=404, detail="Templates directory not found")

    templates = []

    # Get all HTML files in templates directory and subdirectories
    for html_file in TEMPLATE_DIR.rglob("*.html"):
        relative_path = html_file.relative_to(TEMPLATE_DIR)
        templates.append(
            {
                "name": html_file.stem,
                "path": str(relative_path),
                "full_path": str(html_file),
                "size": html_file.stat().st_size,
                "directory": str(relative_path.parent)
                if relative_path.parent != Path(".")
                else "root",
            }
        )

    return {
        "templates": templates,
        "total": len(templates),
        "template_directory": str(TEMPLATE_DIR),
    }


@router.get("/view/{template_path:path}", response_class=HTMLResponse)
def view_template(
    template_path: str,
    use_sample_data: bool = Query(True, description="Use sample data for rendering"),
    raw: bool = Query(False, description="Return raw HTML without rendering"),
) -> Any:
    """
    View a specific HTML template.

    Args:
        template_path: Path to the template file relative to templates directory
        use_sample_data: Whether to use sample data for Jinja2 rendering
        raw: Return raw HTML without Jinja2 rendering
    """
    template_file = TEMPLATE_DIR / template_path

    if not template_file.exists():
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )

    if not template_file.suffix.lower() == ".html":
        raise HTTPException(status_code=400, detail="Only HTML files are supported")

    try:
        if raw:
            # Return raw HTML content
            with open(template_file, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Render with Jinja2
            env = get_template_environment()
            template = env.get_template(template_path)

            # Load sample data if requested
            context = {}
            if use_sample_data:
                context = load_sample_data()

            content = template.render(**context)

        return HTMLResponse(content=content)

    except TemplateNotFound:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering template: {str(e)}"
        )


@router.get("/preview/{template_path:path}", response_class=HTMLResponse)
def preview_template(
    template_path: str,
    data: Optional[str] = Query(None, description="JSON data to use for rendering"),
) -> Any:
    """
    Preview a template with custom data.

    Args:
        template_path: Path to the template file relative to templates directory
        data: JSON string containing data to use for rendering
    """
    template_file = TEMPLATE_DIR / template_path

    if not template_file.exists():
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )

    try:
        env = get_template_environment()
        template = env.get_template(template_path)

        # Parse custom data or use sample data
        context = {}
        if data:
            try:
                context = json.loads(data)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON data provided",
                )
        else:
            context = load_sample_data()

        content = template.render(**context)
        return HTMLResponse(content=content)

    except TemplateNotFound:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering template: {str(e)}"
        )


@router.get("/raw/{template_path:path}")
def get_raw_template(template_path: str) -> Any:
    """
    Get raw template content as text.

    Args:
        template_path: Path to the template file relative to templates directory
    """
    template_file = TEMPLATE_DIR / template_path

    if not template_file.exists():
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )

    try:
        with open(template_file, "r", encoding="utf-8") as f:
            content = f.read()

        return {
            "template_path": template_path,
            "content": content,
            "size": len(content),
            "lines": len(content.splitlines()),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading template: {str(e)}")


@router.get("/sample-data")
def get_sample_data() -> Any:
    """
    Get the sample data used for template rendering.
    """
    try:
        sample_data = load_sample_data()
        return {
            "sample_data": sample_data,
            "keys": list(sample_data.keys()) if isinstance(sample_data, dict) else [],
            "data_file": str(TEMPLATE_DIR / "sample-data.json"),
        }
    except Exception as e:
        return {
            "error": f"Error loading sample data: {str(e)}",
            "sample_data": {},
            "keys": [],
        }


@router.post("/test-render/{template_path:path}", response_class=HTMLResponse)
def test_render_template(template_path: str, test_data: dict) -> Any:
    """
    Test render a template with provided data.

    Args:
        template_path: Path to the template file relative to templates directory
        test_data: Dictionary containing data to use for rendering
    """
    template_file = TEMPLATE_DIR / template_path

    if not template_file.exists():
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )

    try:
        env = get_template_environment()
        template = env.get_template(template_path)

        content = template.render(**test_data)
        return HTMLResponse(content=content)

    except TemplateNotFound:
        raise HTTPException(
            status_code=404, detail=f"Template '{template_path}' not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error rendering template: {str(e)}"
        )

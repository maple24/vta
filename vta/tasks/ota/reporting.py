from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.table import Table
from loguru import logger

ROOT = Path(__file__).resolve().parent.parent.parent.parent


class TestReporter:
    """Generic test reporter for generating HTML and console reports"""

    def __init__(
        self,
        test_name: str = "Test",
        log_base_path: Optional[Path] = None,
        custom_styles: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the test reporter

        Args:
            test_name: Name of the test (e.g., "OTA Test", "Performance Test")
            log_base_path: Base path for log files (defaults to ROOT/log)
            custom_styles: Custom CSS styles for HTML reports
        """
        self.test_name = test_name
        self.log_base_path = log_base_path or ROOT / "log"
        self.log_path = self.log_base_path / datetime.now().strftime("%A_%m%d%Y_%H%M")
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.console = Console()

        # Default styles that can be overridden
        self.default_styles = {
            "body": "font-family: Arial, sans-serif; margin: 20px;",
            "header": "background-color: #f0f0f0; padding: 10px; border-radius: 5px;",
            "success": "color: green; font-weight: bold;",
            "failure": "color: red; font-weight: bold;",
            "metric": "margin: 10px 0;",
            "log_section": "margin-top: 20px; background-color: #f9f9f9; padding: 10px; border-radius: 5px;",
            "summary": "background-color: #e6f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;",
            "table": "border-collapse: collapse; width: 100%; margin: 20px 0;",
            "table_cell": "border: 1px solid #ddd; padding: 8px; text-align: left;",
            "table_header": "background-color: #f2f2f2;",
        }

        if custom_styles:
            self.default_styles.update(custom_styles)

    def _get_css_styles(self) -> str:
        """Generate CSS styles for HTML reports"""
        return f"""
            body {{ {self.default_styles["body"]} }}
            .header {{ {self.default_styles["header"]} }}
            .success {{ {self.default_styles["success"]} }}
            .failure {{ {self.default_styles["failure"]} }}
            .metric {{ {self.default_styles["metric"]} }}
            .log-section {{ {self.default_styles["log_section"]} }}
            .summary {{ {self.default_styles["summary"]} }}
            table {{ {self.default_styles["table"]} }}
            th, td {{ {self.default_styles["table_cell"]} }}
            th {{ {self.default_styles["table_header"]} }}
        """

    def _calculate_summary_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary metrics from results"""
        if not results:
            return {}

        total_iterations = len(results)
        success_count = sum(1 for e in results if e["success"])
        failure_count = total_iterations - success_count
        avg_runtime = sum(e["runtime"] for e in results) / total_iterations
        success_rate = success_count / total_iterations * 100

        return {
            "total_iterations": total_iterations,
            "success_count": success_count,
            "failure_count": failure_count,
            "avg_runtime": avg_runtime,
            "success_rate": success_rate,
        }

    def _calculate_additional_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate metrics for additional fields (not just averages)"""
        if not results:
            return {}

        standard_columns = {"iteration", "success", "runtime", "failing_steps"}
        all_metric_keys = set()
        for result in results:
            all_metric_keys.update(result.keys())

        additional_metrics = {}
        numeric_metrics = all_metric_keys - standard_columns

        for key in numeric_metrics:
            values = [e.get(key) for e in results if e.get(key) is not None]
            if values:
                # Check if all values are numeric
                numeric_values = [v for v in values if isinstance(v, (int, float))]
                if numeric_values:
                    # For numeric values, calculate average
                    additional_metrics[f"avg_{key}"] = sum(numeric_values) / len(numeric_values)
                    # Also include min/max if there are multiple values
                    if len(numeric_values) > 1:
                        additional_metrics[f"min_{key}"] = min(numeric_values)
                        additional_metrics[f"max_{key}"] = max(numeric_values)
                else:
                    # For non-numeric values, just track the most common value or last value
                    additional_metrics[f"last_{key}"] = values[-1]

        return additional_metrics

    def _format_metric_name(self, key: str, prefix: str = "") -> str:
        """Format metric name for display"""
        name = key.replace("_", " ").title()
        if prefix:
            name = f"{prefix} {name}"
        return name

    def _build_additional_metrics_html(self, additional_metrics: Dict[str, Any]) -> str:
        """Build HTML for additional metrics summary"""
        html = ""
        for key, value in additional_metrics.items():
            metric_name = self._format_metric_name(key)
            
            # Format value based on type and key name
            if isinstance(value, (int, float)):
                if "time" in key.lower() or "duration" in key.lower() or key.startswith("avg_") and "time" in key:
                    formatted_value = f"{value:.2f} seconds"
                else:
                    formatted_value = f"{value:.2f}"
            else:
                formatted_value = str(value)
            
            html += f"<p><strong>{metric_name}:</strong> {formatted_value}</p>"
        return html

    def generate_html_report_for_iteration(
        self,
        iteration_num: int,
        success: bool,
        runtime: float,
        failing_steps: str = "",
        log_path: Optional[Path] = None,
        additional_metrics: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate HTML report for a single iteration"""
        # Build additional metrics HTML
        additional_html = ""
        if additional_metrics:
            for key, value in additional_metrics.items():
                display_name = self._format_metric_name(key)
                
                # Format value based on type
                if isinstance(value, (int, float)):
                    if "time" in key.lower() or "duration" in key.lower():
                        formatted_value = f"{value:.2f} seconds"
                    else:
                        formatted_value = f"{value:.2f}"
                else:
                    formatted_value = str(value)
                
                additional_html += f'<div class="metric"><strong>{display_name}:</strong> {formatted_value}</div>'

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.test_name} - Iteration {iteration_num}</title>
            <style>{self._get_css_styles()}</style>
        </head>
        <body>
            <div class="header">
                <h1>{self.test_name} Report - Iteration {iteration_num}</h1>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="metric">
                <strong>Result:</strong> <span class="{"success" if success else "failure"}">
                    {"PASS" if success else "FAIL"}
                </span>
            </div>
            
            <div class="metric">
                <strong>Runtime:</strong> {runtime:.2f} seconds
            </div>
            
            {additional_html}
            
            {'<div class="metric"><strong>Failing Steps:</strong> ' + failing_steps + "</div>" if failing_steps else ""}
            
            {f'<div class="log-section"><h3>Log File Location</h3><p>{log_path}</p></div>' if log_path else ""}
        </body>
        </html>
        """
        html_file_path = self.log_path / f"iteration_{iteration_num}_report.html"
        with open(html_file_path, "w") as f:
            f.write(html_content)
        return html_file_path

    def generate_html_summary_report(
        self,
        results: List[Dict[str, Any]],
        custom_columns: Optional[List[str]] = None,
        custom_summary_metrics: Optional[Dict[str, Any]] = None,
    ) -> Path:
        """Generate HTML summary report for all iterations"""
        summary_metrics = self._calculate_summary_metrics(results)
        additional_metrics = self._calculate_additional_metrics(results)

        # Default columns (keep it simple)
        default_columns = ["iteration", "success", "runtime", "failing_steps"]
        columns_to_show = custom_columns or default_columns

        # Generate table headers
        header_html = "".join(f"<th>{col.replace('_', ' ').title()}</th>" for col in columns_to_show)

        # Generate table rows
        rows_html = ""
        for entry in results:
            status_class = "success" if entry["success"] else "failure"
            status_text = "PASS" if entry["success"] else "FAIL"
            rows_html += "<tr>"

            for col in columns_to_show:
                if col == "success":
                    rows_html += f'<td class="{status_class}">{status_text}</td>'
                elif col == "runtime":
                    rows_html += f"<td>{entry.get(col, 0):.2f}s</td>"
                else:
                    rows_html += f"<td>{entry.get(col, 'N/A')}</td>"
            rows_html += "</tr>"

        # Build summary metrics HTML
        additional_metrics_html = self._build_additional_metrics_html(additional_metrics)
        custom_summary_html = ""
        if custom_summary_metrics:
            for key, value in custom_summary_metrics.items():
                custom_summary_html += f"<p><strong>{key}:</strong> {value}</p>"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.test_name} Summary Report</title>
            <style>{self._get_css_styles()}</style>
        </head>
        <body>
            <div class="header">
                <h1>{self.test_name} Summary Report</h1>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="summary">
                <h2>Summary Statistics</h2>
                <p><strong>Total Iterations:</strong> {summary_metrics.get("total_iterations", 0)}</p>
                <p><strong>Successful Tests:</strong> <span class="success">{summary_metrics.get("success_count", 0)}</span></p>
                <p><strong>Failed Tests:</strong> <span class="failure">{summary_metrics.get("failure_count", 0)}</span></p>
                <p><strong>Average Runtime:</strong> {summary_metrics.get("avg_runtime", 0):.2f} seconds</p>
                <p><strong>Success Rate:</strong> {summary_metrics.get("success_rate", 0):.1f}%</p>
                {additional_metrics_html}
                {custom_summary_html}
            </div>
            
            <table>
                <thead>
                    <tr>{header_html}</tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </body>
        </html>
        """
        html_file_path = self.log_path / "summary_report.html"
        with open(html_file_path, "w") as f:
            f.write(html_content)
        logger.info(f"HTML summary report generated: {html_file_path}")
        return html_file_path

    def generate_console_report(
        self, results: List[Dict[str, Any]], custom_columns: Optional[List[str]] = None, show_summary: bool = True
    ) -> None:
        """Generate console report using Rich"""
        table = Table(title=f"{self.test_name} Report")

        # Default columns (keep it simple and general)
        default_columns = ["iteration", "success", "runtime", "failing_steps"]
        columns_to_show = custom_columns or default_columns

        # Add columns to table
        column_headers = {
            "iteration": "Iteration",
            "success": "Result",
            "runtime": "Runtime (s)",
            "failing_steps": "Failing Steps",
        }

        for col in columns_to_show:
            header = column_headers.get(col, self._format_metric_name(col))
            table.add_column(header, justify="center")

        # Add data rows
        for entry in results:
            row_data = []
            for col in columns_to_show:
                if col == "success":
                    row_data.append("[green]PASS[/green]" if entry["success"] else "[red]FAIL[/red]")
                elif col == "runtime":
                    row_data.append(f"{entry.get(col, 0):.2f}")
                else:
                    row_data.append(str(entry.get(col, "N/A")))
            table.add_row(*row_data)

        # Add summary if requested
        if show_summary and results:
            summary_metrics = self._calculate_summary_metrics(results)
            additional_averages = self._calculate_additional_metrics(results)

            separator = ["─" * 15] * len(columns_to_show)
            table.add_row(*separator)

            # Add summary rows with proper column alignment
            empty_cols = [""] * (len(columns_to_show) - 2)

            table.add_row("[bold]Total Iterations[/bold]", str(summary_metrics["total_iterations"]), *empty_cols)
            table.add_row("[bold green]Total PASS[/bold green]", str(summary_metrics["success_count"]), *empty_cols)
            table.add_row("[bold red]Total FAIL[/bold red]", str(summary_metrics["failure_count"]), *empty_cols)
            table.add_row("[bold]Average Runtime (s)[/bold]", f"{summary_metrics['avg_runtime']:.2f}", *empty_cols)

            # Add additional metric averages
            for key, value in additional_averages.items():
                metric_name = self._format_metric_name(key)
                
                # Format value based on type and key name
                if isinstance(value, (int, float)):
                    if "time" in key.lower() or "duration" in key.lower() or key.startswith("avg_") and "time" in key:
                        formatted_value = f"{value:.2f} (s)"
                        table.add_row(f"[bold]{metric_name}[/bold]", formatted_value, *empty_cols)
                    else:
                        formatted_value = f"{value:.2f}"
                        table.add_row(f"[bold]{metric_name}[/bold]", formatted_value, *empty_cols)
                else:
                    table.add_row(f"[bold]{metric_name}[/bold]", str(value), *empty_cols)

        self.console.print(table)

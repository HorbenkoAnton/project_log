from typing import Dict, Any, Tuple
from collections import defaultdict
import src.config as config

class ReportFormatter:
    def __init__(self):
        self.active_cols = getattr(config, "SIGNATURE_COMPONENTS", ["service", "level", "message"])
        self.common_lvls = ["ERROR", "WARN", "INFO", "DEBUG"]

    def build_text_report(self, report_data: Dict[Tuple, Dict[str, Any]]) -> str:
        if not report_data:
            return "No logs aggregated."

        stats, total = self._get_global_stats(report_data)
        
        lines = [
            "=== LOG AGGREGATION SUMMARY ===",
            f"Total Events: {total}",
            f"Breakdown:    {self._format_stats_line(stats)}",
            f"Active Sig:   ({', '.join(self.active_cols)})",
            "=" * 40, ""
        ]

        # Detail routing: Grouped vs Flat
        if "level" in self.active_cols:
            lines.extend(self._build_grouped_details(report_data, stats))
        else:
            lines.extend(self._build_flat_details(report_data))

        return "\n".join(lines)

    def _get_global_stats(self, report_data):
        stats = defaultdict(int)
        total = 0
        for data in report_data.values():
            count = data["count"]
            total += count
            stats[data["sample"].level.upper()] += count
        return stats, total

    def _format_stats_line(self, stats):
        other = [l for l in stats.keys() if l not in self.common_lvls]
        return " | ".join([f"{l}: {stats[l]}" for l in self.common_lvls + other if stats[l] > 0])

    def _build_grouped_details(self, report_data, stats):
        lvl_idx = self.active_cols.index("level")
        grouped = defaultdict(list)
        for sig, data in report_data.items():
            grouped[sig[lvl_idx].upper()].append((sig, data))

        output = []
        for level in self.common_lvls + [l for l in stats.keys() if l not in self.common_lvls]:
            if level not in grouped: continue
            output.append(f"[{level} LEVEL DETAILS]")
            sorted_items = sorted(grouped[level], key=lambda x: x[1]["count"], reverse=True)
            output.extend([self._format_row(sig, data) for sig, data in sorted_items])
            output.append("-" * 40)
        return output

    def _build_flat_details(self, report_data):
        output = ["[AGGREGATED DETAILS]"]
        sorted_items = sorted(report_data.items(), key=lambda x: x[1]["count"], reverse=True)
        output.extend([self._format_row(sig, data) for sig, data in sorted_items])
        output.append("-" * 40)
        return output

    def _format_row(self, sig: Tuple, data: Dict) -> str:
        parts = [f"{data['count']:<6}"]
        for i, col in enumerate(self.active_cols):
            # Safety: Check if signature actually has this many elements
            if i < len(sig):
                val = str(sig[i])
            else:
                val = "MISSING"
                
            width = 40 if col == "message" else 15
            parts.append(f"{val:<{width}}")
        return " | ".join(parts)
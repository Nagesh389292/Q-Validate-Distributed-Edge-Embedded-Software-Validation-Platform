from typing import List, Dict, Set
from qvalidate.db import DatabaseManager

class TestImpactAnalysisEngine:
    """
    Test Impact Analysis (TIA) Engine.
    Maps changed source code files/components to affected test cases,
    enabling targeted selective regression execution rather than running full suites blindly.
    """
    def __init__(self, db: DatabaseManager = None):
        self.db = db or DatabaseManager()
        
        # Component to File mapping definition
        self.file_component_map: Dict[str, str] = {
            "Bootloader.cpp": "COMP-BOOT",
            "Firmware.cpp": "COMP-BOOT",
            "Firmware.hpp": "COMP-BOOT",
            "MemoryManager.cpp": "COMP-MEM",
            "Memory.cpp": "COMP-MEM",
            "Memory.hpp": "COMP-MEM",
            "CPUScheduler.cpp": "COMP-CPU",
            "CPU.cpp": "COMP-CPU",
            "CPU.hpp": "COMP-CPU",
            "Thermal.cpp": "COMP-CPU",
            "Benchmark.cpp": "COMP-PERF",
            "Latency.cpp": "COMP-PERF"
        }

    def get_impacted_components(self, changed_files: List[str]) -> Set[str]:
        impacted_components = set()
        for filepath in changed_files:
            basename = filepath.split("/")[-1].split("\\")[-1]
            if basename in self.file_component_map:
                impacted_components.add(self.file_component_map[basename])
            else:
                # Fallback heuristic by file name prefix
                if "boot" in basename.lower() or "firmware" in basename.lower():
                    impacted_components.add("COMP-BOOT")
                elif "mem" in basename.lower() or "heap" in basename.lower():
                    impacted_components.add("COMP-MEM")
                elif "cpu" in basename.lower() or "thermal" in basename.lower():
                    impacted_components.add("COMP-CPU")
                elif "perf" in basename.lower() or "latency" in basename.lower():
                    impacted_components.add("COMP-PERF")
        return impacted_components

    def analyze_impact(self, changed_files: List[str]) -> Dict:
        impacted_components = self.get_impacted_components(changed_files)
        
        selected_tests = []
        with self.db.get_connection() as conn:
            cur = conn.cursor()
            if impacted_components:
                placeholders = ",".join(["?"] * len(impacted_components))
                cur.execute(f"""
                    SELECT t.test_id, t.name, t.category, t.component_id, c.name as component_name
                    FROM test_cases t
                    LEFT JOIN components c ON t.component_id = c.component_id
                    WHERE t.component_id IN ({placeholders})
                """, list(impacted_components))
            else:
                # If no mapping matched, fallback to running all test cases
                cur.execute("""
                    SELECT t.test_id, t.name, t.category, t.component_id, c.name as component_name
                    FROM test_cases t
                    LEFT JOIN components c ON t.component_id = c.component_id
                """)
            
            rows = cur.fetchall()
            for r in rows:
                selected_tests.append(dict(r))

        return {
            "changed_files": changed_files,
            "impacted_component_ids": list(impacted_components),
            "selected_test_count": len(selected_tests),
            "selected_tests": selected_tests
        }

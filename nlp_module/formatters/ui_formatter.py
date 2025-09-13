"""
UI formatting utilities for Data Explorer
"""
from typing import Dict, List, Any
from nlp_module.core.parser import ParsedQuery

class UIFormatter:
    """Formats parsed queries and results for UI display"""
    
    def format_suggestion(self, parsed: ParsedQuery, confidence: float = None) -> Dict:
        """Format a parsed query as a UI suggestion"""
        conf = confidence if confidence is not None else parsed.confidence
        
        return {
            "title": self._get_operation_title(parsed),
            "description": parsed.explanation,
            "confidence": conf,
            "confidence_label": self._get_confidence_label(conf),
            "operation": parsed.operation,
            "args": parsed.args,
            "source": parsed.source,
            "executable": True
        }
    
    def _get_operation_title(self, parsed: ParsedQuery) -> str:
        """Generate a user-friendly title for the operation"""
        op = parsed.operation
        args = parsed.args
        
        if op == "group_and_aggregate":
            group_col = args.get("group_col", "data")
            agg_col = args.get("agg_col", "values")
            limit = args.get("limit")
            
            if limit:
                return f"Top {limit} {group_col.replace('_', ' ').title()}"
            else:
                return f"Analyze by {group_col.replace('_', ' ').title()}"
                
        elif op == "filter_data":
            column = args.get("column", "data")
            value = args.get("value", "value")
            return f"Filter: {column.replace('_', ' ').title()} = {value}"
            
        elif op == "sort_data":
            column = args.get("column", "data")
            return f"Sort by {column.replace('_', ' ').title()}"
            
        elif op == "pivot_data":
            index_col = args.get("index_col", "rows")
            columns_col = args.get("columns_col", "columns")
            return f"Pivot: {index_col.title()} vs {columns_col.title()}"
            
        else:  # preview
            return "Data Overview"
    
    def _get_confidence_label(self, confidence: float) -> str:
        """Convert confidence score to human-readable label"""
        if confidence >= 0.8:
            return "High"
        elif confidence >= 0.6:
            return "Medium" 
        else:
            return "Low"
    
    def format_result_summary(self, df, operation: str) -> Dict:
        """Format operation results for UI display"""
        if df is None:
            return {"error": "No data available"}
            
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "operation": operation,
            "column_names": list(df.columns),
            "preview": df.head(5).to_dict("records")
        }

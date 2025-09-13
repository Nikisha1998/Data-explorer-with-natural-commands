"""
Enhanced NLP Manager for Data Explorer with Natural Commands
"""
import pandas as pd
import logging
from typing import Dict, List, Optional, Any
from dataclasses import asdict

from nlp_module.core.parser import QueryParser, ParsedQuery
from nlp_module.formatters.ui_formatter import UIFormatter
from config import DATASET_COLUMNS, UI_CONFIG

logger = logging.getLogger(__name__)

class NLPManager:
    """Main NLP management class for natural language data queries"""
    
    def __init__(self, columns: List[str] = None):
        self.columns = columns or DATASET_COLUMNS
        self.parser = QueryParser(self.columns)
        self.formatter = UIFormatter()
        self.df = None
        self.current_view = None
        
    def set_dataset(self, df: pd.DataFrame):
        """Set the dataset context"""
        self.df = df
        self.columns = list(df.columns)
        self.parser = QueryParser(self.columns)  # Recreate with actual columns
        logger.info(f"Dataset loaded: {df.shape}")
    
    def process_query(self, query: str, debug: bool = False) -> Dict[str, Any]:
        """
        Process natural language query and return structured result
        
        Args:
            query: Natural language query
            debug: Enable debug logging
            
        Returns:
            Dict containing parsed query, suggestions, and metadata
        """
        if not query or not query.strip():
            return {
                "error": "Please enter a query to analyze your data",
                "suggestions": []
            }
        
        if self.df is None:
            return {
                "error": "No dataset loaded. Please upload a CSV file first.",
                "suggestions": []
            }
        
        try:
            # Parse the main query
            primary_result = self.parser.parse(query)
            
            if debug:
                logger.info(f"Primary parse: {asdict(primary_result)}")
            
            # Generate alternative interpretations
            suggestions = self._generate_suggestions(query, primary_result)
            
            # Execute the primary operation
            try:
                result_data = self._execute_operation(primary_result)
                self.current_view = result_data
            except Exception as e:
                logger.error(f"Operation execution failed: {e}")
                result_data = None
            
            return {
                "query": query,
                "primary": asdict(primary_result),
                "suggestions": suggestions,
                "result_data": result_data,
                "message": f"Found {len(suggestions)} interpretation(s) for: '{query}'"
            }
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            return {
                "error": f"Failed to process query: {str(e)}",
                "query": query,
                "suggestions": []
            }
    
    def _generate_suggestions(self, query: str, primary: ParsedQuery) -> List[Dict]:
        """Generate multiple interpretations for ambiguous queries"""
        suggestions = [self.formatter.format_suggestion(primary, confidence=primary.confidence)]
        
        # Add alternative interpretations based on query patterns
        query_lower = query.lower()
        
        if "performance" in query_lower and len(suggestions) == 1:
            # Add alternative performance views
            alternatives = [
                ParsedQuery(
                    operation="group_and_aggregate",
                    args={"group_col": "product_category", "agg_col": "net_revenue", "agg_func": "sum"},
                    explanation="Performance by product category",
                    confidence=0.7,
                    source="alternative"
                ),
                ParsedQuery(
                    operation="group_and_aggregate", 
                    args={"group_col": "channel", "agg_col": "units_sold", "agg_func": "sum"},
                    explanation="Sales performance by channel",
                    confidence=0.6,
                    source="alternative"
                )
            ]
            
            for alt in alternatives:
                if len(suggestions) < UI_CONFIG["max_suggestions"]:
                    suggestions.append(self.formatter.format_suggestion(alt, confidence=alt.confidence))
        
        elif "seasonality" in query_lower and "region" not in query_lower:
            # Add regional seasonality view
            alt = ParsedQuery(
                operation="pivot_data",
                args={
                    "index_col": "quarter",
                    "columns_col": "region",
                    "values_col": "net_revenue", 
                    "agg_func": "sum"
                },
                explanation="Seasonal patterns across regions",
                confidence=0.75,
                source="alternative"
            )
            suggestions.append(self.formatter.format_suggestion(alt, confidence=alt.confidence))
        
        elif "top" in query_lower and "product" in query_lower:
            # Add alternative top product views
            alternatives = [
                ParsedQuery(
                    operation="group_and_aggregate",
                    args={"group_col": "product_name", "agg_col": "units_sold", "agg_func": "sum", "limit": 5},
                    explanation="Top 5 products by units sold",
                    confidence=0.7,
                    source="alternative"
                ),
                ParsedQuery(
                    operation="group_and_aggregate",
                    args={"group_col": "product_category", "agg_col": "net_revenue", "agg_func": "mean"},
                    explanation="Average revenue by product category", 
                    confidence=0.6,
                    source="alternative"
                )
            ]
            
            for alt in alternatives:
                if len(suggestions) < UI_CONFIG["max_suggestions"]:
                    suggestions.append(self.formatter.format_suggestion(alt, confidence=alt.confidence))
        
        return suggestions[:UI_CONFIG["max_suggestions"]]
    
    def _execute_operation(self, parsed_query: ParsedQuery) -> Optional[pd.DataFrame]:
        """Execute the parsed operation on the dataset"""
        if self.df is None:
            return None
        
        try:
            operation = parsed_query.operation
            args = parsed_query.args
            
            if operation == "group_and_aggregate":
                return self._group_and_aggregate(args)
            elif operation == "filter_data":
                return self._filter_data(args)
            elif operation == "sort_data":
                return self._sort_data(args)
            elif operation == "pivot_data":
                return self._pivot_data(args)
            else:  # preview
                limit = args.get("limit", UI_CONFIG["default_preview_rows"])
                return self.df.head(limit)
                
        except Exception as e:
            logger.error(f"Operation execution failed: {e}")
            return None
    
    def _group_and_aggregate(self, args: Dict) -> pd.DataFrame:
        """Execute group and aggregate operation"""
        group_col = args["group_col"]
        agg_col = args["agg_col"] 
        agg_func = args.get("agg_func", "sum")
        limit = args.get("limit")
        sort_order = args.get("sort", "desc")
        
        grouped = self.df.groupby(group_col)[agg_col].agg(agg_func).reset_index()
        grouped.columns = [group_col, f"{agg_func}_{agg_col}"]
        
        # Sort results
        ascending = sort_order.lower() == "asc"
        grouped = grouped.sort_values(f"{agg_func}_{agg_col}", ascending=ascending)
        
        if limit:
            grouped = grouped.head(limit)
            
        return grouped
    
    def _filter_data(self, args: Dict) -> pd.DataFrame:
        """Execute filter operation"""
        column = args["column"]
        value = args["value"]
        
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
        
        return self.df[self.df[column] == value]
    
    def _sort_data(self, args: Dict) -> pd.DataFrame:
        """Execute sort operation"""
        column = args["column"]
        ascending = args.get("ascending", True)
        
        if column not in self.df.columns:
            raise ValueError(f"Column '{column}' not found in dataset")
            
        return self.df.sort_values(column, ascending=ascending)
    
    def _pivot_data(self, args: Dict) -> pd.DataFrame:
        """Execute pivot operation"""
        index_col = args["index_col"]
        columns_col = args["columns_col"]
        values_col = args["values_col"]
        agg_func = args.get("agg_func", "sum")
        
        return self.df.pivot_table(
            index=index_col,
            columns=columns_col, 
            values=values_col,
            aggfunc=agg_func,
            fill_value=0
        ).reset_index()
    
    def get_export_data(self, format: str = "csv") -> Optional[bytes]:
        """Export current view data"""
        if self.current_view is None:
            return None
            
        if format.lower() == "csv":
            return self.current_view.to_csv(index=False).encode()
        elif format.lower() == "json":
            return self.current_view.to_json(orient="records").encode()
        else:
            return None

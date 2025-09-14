"""
Core parsing functionality for natural language queries
"""
import re
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
logger = logging.getLogger(__name__)

@dataclass
class ParsedQuery:
    operation: str
    args: Dict
    explanation: str
    confidence: float
    source: str = "rule"

class RuleBasedParser:
    """Enhanced rule-based parser for natural language queries"""
    
    def __init__(self, columns: List[str], df=None):
        self.columns = columns
        self.df = df
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns for common query types"""
        return {
            # Revenue analysis patterns
            'top_products_revenue': re.compile(r'top\s+(\d+)\s+products?\s+.*revenue', re.I),
            'revenue_by': re.compile(r'revenue\s+.*by\s+(\w+)', re.I),
            'revenue_by_region': re.compile(r'revenue\s+.*by\s+region', re.I),
            'revenue_by_quarter': re.compile(r'revenue\s+.*by\s+quarter', re.I),
            
            # Seasonality patterns
            'seasonality': re.compile(r'season(ality|al)\s*.*by\s+(\w+)', re.I),
            'quarterly_analysis': re.compile(r'quarter(ly)?\s+.*', re.I),
            
            # Regional patterns
            'region_filter': re.compile(r'region\s*(?:=|is)?\s*([a-z]+)', re.I),
            'regional_performance': re.compile(r'performance\s+.*region', re.I),
            
            # Product patterns
            'product_performance': re.compile(r'product\s+performance', re.I),
            'top_products': re.compile(r'top\s+(\d+)?\s*products?(?:\s+this\s+quarter)?(?:\s+in\s+(\d{4}))?', re.I),
            
            # Time patterns
            'year_filter': re.compile(r'\b(20\d{2})\b'),
            'this_quarter': re.compile(r'this\s+quarter', re.I),
            
            # Sort patterns
            'sort_by': re.compile(r'sort\s+.*by\s+(\w+)\s*(desc|asc)?', re.I),
            
            # General patterns
            'show_all': re.compile(r'show\s+(all|everything|data)', re.I),
            'summary': re.compile(r'summar(y|ize)', re.I)
        }
    
    def parse(self, query: str) -> ParsedQuery:
        """Parse natural language query into structured operation"""
        query = query.strip()
        
        if not query:
            return ParsedQuery(
                operation="preview",
                args={},
                explanation="Please provide a query to analyze your data",
                confidence=1.0
            )
        
        # Top products this quarter (with optional year)
        if self.patterns['top_products'].search(query):
            match = self.patterns['top_products'].search(query)
            n = int(match.group(1)) if match.group(1) else 5
            year = int(match.group(2)) if match.group(2) else None
            if self.df is not None:
                latest_quarter = self.df['quarter'].max()
                filters = [{"column": "quarter", "value": latest_quarter}]
                if year:
                    filters.append({"column": "year", "value": year})
                return ParsedQuery(
                    operation="filter_and_group",
                    args={
                        "filters": filters,
                        "group_col": "product_name",
                        "agg_col": "net_revenue",
                        "agg_func": "sum",
                        "limit": n,
                        "sort": "desc"
                    },
                    explanation=f"Top {n} products by revenue in quarter {latest_quarter}" + (f" of {year}" if year else ""),
                    confidence=0.95
                )
        
        # Revenue by column
        if self.patterns['revenue_by'].search(query):
            match = self.patterns['revenue_by'].search(query)
            group_by = match.group(1).lower()
            if group_by in self.columns:
                return ParsedQuery(
                    operation="group_and_aggregate",
                    args={
                        "group_col": group_by,
                        "agg_col": "net_revenue",
                        "agg_func": "sum"
                    },
                    explanation=f"Revenue by {group_by.replace('_', ' ').title()}",
                    confidence=0.9
                )
        
        # Revenue by region (specific case)
        if self.patterns['revenue_by_region'].search(query):
            return ParsedQuery(
                operation="group_and_aggregate",
                args={
                    "group_col": "region",
                    "agg_col": "net_revenue",
                    "agg_func": "sum"
                },
                explanation="Revenue breakdown by region",
                confidence=0.9
            )
        
        # Seasonality analysis
        if self.patterns['seasonality'].search(query):
            match = self.patterns['seasonality'].search(query)
            group_by = match.group(2).lower() if match.group(2) else 'quarter'
            
            if group_by in ['region', 'regions']:
                return ParsedQuery(
                    operation="pivot_data",
                    args={
                        "index_col": "quarter",
                        "columns_col": "region",
                        "values_col": "net_revenue",
                        "agg_func": "sum"
                    },
                    explanation="Seasonal revenue patterns by region and quarter",
                    confidence=0.85
                )
            else:
                return ParsedQuery(
                    operation="group_and_aggregate",
                    args={
                        "group_col": "quarter",
                        "agg_col": "net_revenue",
                        "agg_func": "sum"
                    },
                    explanation="Seasonal revenue by quarter",
                    confidence=0.9
                )
        
        # Regional filtering
        region_match = self.patterns['region_filter'].search(query)
        if region_match:
            region = region_match.group(1).capitalize()
            return ParsedQuery(
                operation="filter_data",
                args={"column": "region", "value": region},
                explanation=f"Data filtered for {region} region",
                confidence=0.9
            )
        
        # Year filtering
        year_match = self.patterns['year_filter'].search(query)
        if year_match:
            year = int(year_match.group(1))
            return ParsedQuery(
                operation="filter_data",
                args={"column": "year", "value": year},
                explanation=f"Data filtered for year {year}",
                confidence=0.85
            )
        
        # Sort by column
        if self.patterns['sort_by'].search(query):
            match = self.patterns['sort_by'].search(query)
            column = match.group(1).lower()
            sort_order = match.group(2).lower() if match.group(2) else 'desc'
            if column in self.columns:
                return ParsedQuery(
                    operation="sort_data",
                    args={"column": column, "ascending": sort_order == 'asc'},
                    explanation=f"Sort by {column.replace('_', ' ').title()} {'ascending' if sort_order == 'asc' else 'descending'}",
                    confidence=0.9
                )
        
        # Performance analysis
        if self.patterns['regional_performance'].search(query):
            return ParsedQuery(
                operation="group_and_aggregate",
                args={
                    "group_col": "region",
                    "agg_col": "net_revenue",
                    "agg_func": "sum"
                },
                explanation="Performance comparison by region",
                confidence=0.8
            )
        
        # Default fallback
        return ParsedQuery(
            operation="preview",
            args={"limit": 100},
            explanation="Showing data overview - try asking about revenue, regions, or top products",
            confidence=0.5
        )

class LLMParser:
    """LLM-based parser (optional, falls back to rules if unavailable)"""
    
    def __init__(self):
        self.available = False
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        try:
            from transformers import pipeline
            import torch
            
            self.model = pipeline(
                "text2text-generation",
                model="google/flan-t5-base",
                device="cpu"
            )
            self.available = True
            logger.info("LLM parser initialized successfully")
        except Exception as e:
            logger.warning(f"LLM initialization failed: {e}. Falling back to rule-based parsing.")
            self.available = False
    
    def parse(self, query: str) -> Optional[ParsedQuery]:
        if not self.available:
            return None
            
        try:
            prompt = self._create_prompt(query)
            result = self.model(prompt, max_new_tokens=200, temperature=0.1)[0]['generated_text']
            return self._parse_llm_output(result)
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            return None
    
    def _create_prompt(self, query: str) -> str:
        return f"""
Convert this data analysis request into a JSON operation:
Available operations: group_and_aggregate, filter_data, sort_data, pivot_data, preview, filter_and_group
Available columns: date, year, quarter, region, product_name, net_revenue, units_sold
Query: "{query}"
Respond with JSON only:
{{"operation": "...", "args": {{}}, "explanation": "..."}}
"""
    
    def _parse_llm_output(self, output: str) -> ParsedQuery:
        try:
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
                return ParsedQuery(
                    operation=parsed.get("operation", "preview"),
                    args=parsed.get("args", {}),
                    explanation=parsed.get("explanation", "LLM generated operation"),
                    confidence=0.8,
                    source="llm"
                )
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
        
        return ParsedQuery(
            operation="preview",
            args={},
            explanation="Could not parse LLM response",
            confidence=0.1,
            source="llm_error"
        )

class QueryParser:
    """Main parser that combines rule-based and LLM approaches"""
    
    def __init__(self, columns: List[str], df=None):
        self.rule_parser = RuleBasedParser(columns, df)
        self.llm_parser = LLMParser()
    
    def parse(self, query: str, prefer_llm: bool = True) -> ParsedQuery:
        """Parse query with LLM first, fallback to rules"""
        if prefer_llm and self.llm_parser.available:
            llm_result = self.llm_parser.parse(query)
            if llm_result and llm_result.confidence > 0.6:
                return llm_result
        return self.rule_parser.parse(query)
"""
User Settings and Configuration System for MLB Analytics
Allows customization of stat weights, confidence parameters, and sheet layout.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd


@dataclass
class StatWeights:
    """Statistical weights for analysis calculations."""
    # Batting weights
    woba: float = 0.3
    war: float = 0.25
    babip: float = 0.15
    iso: float = 0.2
    k_rate: float = 0.1
    
    # Pitching weights
    fip: float = 0.35
    era: float = 0.2
    whip: float = 0.2
    k_per_9: float = 0.15
    hr_per_9: float = 0.1
    
    # Situational weights
    recent_form: float = 0.4
    head_to_head: float = 0.3
    park_factor: float = 0.2
    rest_days: float = 0.1


@dataclass
class ConfidenceSettings:
    """Confidence scoring parameters."""
    # Sample size thresholds
    min_at_bats: int = 20
    min_innings_pitched: float = 10.0
    min_head_to_head: int = 5
    
    # Confidence scoring weights
    sample_size_weight: float = 0.4
    consistency_weight: float = 0.3
    recency_weight: float = 0.3
    
    # Confidence thresholds
    high_confidence: float = 0.8
    medium_confidence: float = 0.6
    low_confidence: float = 0.4


@dataclass
class SheetLayout:
    """Google Sheets layout configuration."""
    # Worksheet names
    game_analyzer_sheet: str = "game_analyzer"
    historical_data_sheet: str = "historical_data"
    pitcher_batter_sheet: str = "pitcher_vs_batter"
    park_factors_sheet: str = "park_factors"
    ev_poisson_sheet: str = "ev_poisson"
    
    # Column configurations
    max_rows_per_sheet: int = 1000
    decimal_places: int = 3
    date_format: str = "%Y-%m-%d"
    
    # Formatting options
    highlight_high_confidence: bool = True
    color_code_edges: bool = True
    include_charts: bool = True


@dataclass
class AnalysisSettings:
    """Core analysis configuration."""
    # Poisson settings
    poisson_lookback_days: int = 30
    park_factor_adjustment: bool = True
    weather_adjustment: bool = False
    
    # Expected value settings
    ev_threshold: float = 0.05  # 5% edge minimum
    bankroll_percentage: float = 0.02  # 2% of bankroll per bet
    
    # Model settings
    model_recency_weight: float = 0.6
    injury_impact_multiplier: float = 0.8
    home_field_advantage: float = 0.54


class MLBUserSettings:
    """
    Comprehensive user settings management system.
    """
    
    def __init__(self, config_file: str = "user_settings.json"):
        self.config_file = Path(config_file)
        self.settings = self._load_settings()
        
        # Initialize setting components
        self.stat_weights = StatWeights(**self.settings.get("stat_weights", {}))
        self.confidence = ConfidenceSettings(**self.settings.get("confidence", {}))
        self.sheet_layout = SheetLayout(**self.settings.get("sheet_layout", {}))
        self.analysis = AnalysisSettings(**self.settings.get("analysis", {}))
    
    def _load_settings(self) -> Dict:
        """Load settings from file or create defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self._get_default_settings()
        else:
            default_settings = self._get_default_settings()
            self.save_settings()
            return default_settings
    
    def _get_default_settings(self) -> Dict:
        """Get default settings configuration."""
        return {
            "stat_weights": asdict(StatWeights()),
            "confidence": asdict(ConfidenceSettings()),
            "sheet_layout": asdict(SheetLayout()),
            "analysis": asdict(AnalysisSettings()),
            "user_preferences": {
                "notifications_enabled": True,
                "auto_update": True,
                "data_sources": ["fangraphs", "mlb_api"],
                "time_zone": "UTC",
                "currency": "USD"
            },
            "advanced_settings": {
                "cache_duration_minutes": 30,
                "max_concurrent_requests": 5,
                "request_timeout_seconds": 30,
                "debug_mode": False
            }
        }
    
    def save_settings(self):
        """Save current settings to file."""
        settings_dict = {
            "stat_weights": asdict(self.stat_weights),
            "confidence": asdict(self.confidence),
            "sheet_layout": asdict(self.sheet_layout),
            "analysis": asdict(self.analysis),
            "user_preferences": self.settings.get("user_preferences", {}),
            "advanced_settings": self.settings.get("advanced_settings", {}),
            "last_updated": datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            print("✅ Settings saved successfully!")
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
    
    def update_stat_weights(self, **kwargs):
        """Update statistical weights."""
        for key, value in kwargs.items():
            if hasattr(self.stat_weights, key):
                setattr(self.stat_weights, key, float(value))
        self.save_settings()
    
    def update_confidence_settings(self, **kwargs):
        """Update confidence parameters."""
        for key, value in kwargs.items():
            if hasattr(self.confidence, key):
                setattr(self.confidence, key, type(getattr(self.confidence, key))(value))
        self.save_settings()
    
    def update_sheet_layout(self, **kwargs):
        """Update sheet layout configuration."""
        for key, value in kwargs.items():
            if hasattr(self.sheet_layout, key):
                setattr(self.sheet_layout, key, type(getattr(self.sheet_layout, key))(value))
        self.save_settings()
    
    def update_analysis_settings(self, **kwargs):
        """Update analysis configuration."""
        for key, value in kwargs.items():
            if hasattr(self.analysis, key):
                setattr(self.analysis, key, type(getattr(self.analysis, key))(value))
        self.save_settings()
    
    def get_setting(self, category: str, setting: str) -> Any:
        """Get a specific setting value."""
        category_obj = getattr(self, category, None)
        if category_obj:
            return getattr(category_obj, setting, None)
        return None
    
    def export_settings(self, file_path: str):
        """Export settings to a file."""
        settings_dict = {
            "stat_weights": asdict(self.stat_weights),
            "confidence": asdict(self.confidence),
            "sheet_layout": asdict(self.sheet_layout),
            "analysis": asdict(self.analysis),
            "exported_at": datetime.now().isoformat()
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            print(f"✅ Settings exported to {file_path}")
        except Exception as e:
            print(f"❌ Error exporting settings: {e}")
    
    def import_settings(self, file_path: str):
        """Import settings from a file."""
        try:
            with open(file_path, 'r') as f:
                imported_settings = json.load(f)
            
            # Update settings
            if "stat_weights" in imported_settings:
                self.stat_weights = StatWeights(**imported_settings["stat_weights"])
            if "confidence" in imported_settings:
                self.confidence = ConfidenceSettings(**imported_settings["confidence"])
            if "sheet_layout" in imported_settings:
                self.sheet_layout = SheetLayout(**imported_settings["sheet_layout"])
            if "analysis" in imported_settings:
                self.analysis = AnalysisSettings(**imported_settings["analysis"])
            
            self.save_settings()
            print(f"✅ Settings imported from {file_path}")
            
        except Exception as e:
            print(f"❌ Error importing settings: {e}")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults."""
        self.stat_weights = StatWeights()
        self.confidence = ConfidenceSettings()
        self.sheet_layout = SheetLayout()
        self.analysis = AnalysisSettings()
        self.save_settings()
        print("✅ Settings reset to defaults")
    
    def validate_settings(self) -> List[str]:
        """Validate current settings and return any issues."""
        issues = []
        
        # Validate stat weights sum to reasonable values
        batting_total = (self.stat_weights.woba + self.stat_weights.war + 
                        self.stat_weights.babip + self.stat_weights.iso + 
                        self.stat_weights.k_rate)
        if abs(batting_total - 1.0) > 0.1:
            issues.append(f"Batting weights sum to {batting_total:.2f}, should be close to 1.0")
        
        pitching_total = (self.stat_weights.fip + self.stat_weights.era + 
                         self.stat_weights.whip + self.stat_weights.k_per_9 + 
                         self.stat_weights.hr_per_9)
        if abs(pitching_total - 1.0) > 0.1:
            issues.append(f"Pitching weights sum to {pitching_total:.2f}, should be close to 1.0")
        
        # Validate confidence thresholds
        if not (0 < self.confidence.low_confidence < self.confidence.medium_confidence < self.confidence.high_confidence < 1):
            issues.append("Confidence thresholds should be in ascending order between 0 and 1")
        
        # Validate sample size minimums
        if self.confidence.min_at_bats < 1:
            issues.append("Minimum at-bats should be at least 1")
        
        if self.confidence.min_innings_pitched < 0.1:
            issues.append("Minimum innings pitched should be at least 0.1")
        
        return issues


class SettingsGUI:
    """
    Graphical interface for managing user settings.
    """
    
    def __init__(self, settings: MLBUserSettings):
        self.settings = settings
        self.root = tk.Tk()
        self.root.title("MLB Analytics - User Settings")
        self.root.geometry("800x600")
        
        self.setup_gui()
    
    def setup_gui(self):
        """Setup the GUI components."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_stat_weights_tab(notebook)
        self.create_confidence_tab(notebook)
        self.create_sheet_layout_tab(notebook)
        self.create_analysis_tab(notebook)
        self.create_advanced_tab(notebook)
        
        # Add buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Reset to Defaults", command=self.reset_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Settings", command=self.export_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import Settings", command=self.import_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Validate", command=self.validate_settings).pack(side=tk.LEFT, padx=5)
    
    def create_stat_weights_tab(self, notebook):
        """Create statistical weights configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Stat Weights")
        
        # Batting weights
        batting_frame = ttk.LabelFrame(frame, text="Batting Weights")
        batting_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.batting_vars = {}
        batting_stats = ["woba", "war", "babip", "iso", "k_rate"]
        
        for i, stat in enumerate(batting_stats):
            ttk.Label(batting_frame, text=f"{stat.upper()}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.DoubleVar(value=getattr(self.settings.stat_weights, stat))
            self.batting_vars[stat] = var
            ttk.Scale(batting_frame, from_=0.0, to=1.0, variable=var, orient=tk.HORIZONTAL).grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            ttk.Label(batting_frame, textvariable=var).grid(row=i, column=2, padx=5, pady=2)
        
        batting_frame.columnconfigure(1, weight=1)
        
        # Pitching weights
        pitching_frame = ttk.LabelFrame(frame, text="Pitching Weights")
        pitching_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.pitching_vars = {}
        pitching_stats = ["fip", "era", "whip", "k_per_9", "hr_per_9"]
        
        for i, stat in enumerate(pitching_stats):
            ttk.Label(pitching_frame, text=f"{stat.upper()}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.DoubleVar(value=getattr(self.settings.stat_weights, stat))
            self.pitching_vars[stat] = var
            ttk.Scale(pitching_frame, from_=0.0, to=1.0, variable=var, orient=tk.HORIZONTAL).grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            ttk.Label(pitching_frame, textvariable=var).grid(row=i, column=2, padx=5, pady=2)
        
        pitching_frame.columnconfigure(1, weight=1)
    
    def create_confidence_tab(self, notebook):
        """Create confidence settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Confidence")
        
        # Sample size settings
        sample_frame = ttk.LabelFrame(frame, text="Sample Size Requirements")
        sample_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.confidence_vars = {}
        
        # Min at-bats
        ttk.Label(sample_frame, text="Min At-Bats:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.IntVar(value=self.settings.confidence.min_at_bats)
        self.confidence_vars["min_at_bats"] = var
        ttk.Spinbox(sample_frame, from_=1, to=100, textvariable=var).grid(row=0, column=1, padx=5, pady=2)
        
        # Min innings pitched
        ttk.Label(sample_frame, text="Min Innings Pitched:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.DoubleVar(value=self.settings.confidence.min_innings_pitched)
        self.confidence_vars["min_innings_pitched"] = var
        ttk.Spinbox(sample_frame, from_=0.1, to=50.0, increment=0.1, textvariable=var).grid(row=1, column=1, padx=5, pady=2)
        
        # Confidence thresholds
        thresh_frame = ttk.LabelFrame(frame, text="Confidence Thresholds")
        thresh_frame.pack(fill=tk.X, padx=10, pady=5)
        
        thresholds = ["low_confidence", "medium_confidence", "high_confidence"]
        for i, thresh in enumerate(thresholds):
            ttk.Label(thresh_frame, text=f"{thresh.replace('_', ' ').title()}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.DoubleVar(value=getattr(self.settings.confidence, thresh))
            self.confidence_vars[thresh] = var
            ttk.Scale(thresh_frame, from_=0.0, to=1.0, variable=var, orient=tk.HORIZONTAL).grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
            ttk.Label(thresh_frame, textvariable=var).grid(row=i, column=2, padx=5, pady=2)
        
        thresh_frame.columnconfigure(1, weight=1)
    
    def create_sheet_layout_tab(self, notebook):
        """Create sheet layout configuration tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Sheet Layout")
        
        # Worksheet names
        names_frame = ttk.LabelFrame(frame, text="Worksheet Names")
        names_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.sheet_vars = {}
        sheet_names = ["game_analyzer_sheet", "historical_data_sheet", "pitcher_batter_sheet", "park_factors_sheet", "ev_poisson_sheet"]
        
        for i, sheet_name in enumerate(sheet_names):
            ttk.Label(names_frame, text=f"{sheet_name.replace('_', ' ').title()}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            var = tk.StringVar(value=getattr(self.settings.sheet_layout, sheet_name))
            self.sheet_vars[sheet_name] = var
            ttk.Entry(names_frame, textvariable=var).grid(row=i, column=1, sticky=tk.EW, padx=5, pady=2)
        
        names_frame.columnconfigure(1, weight=1)
        
        # Layout options
        options_frame = ttk.LabelFrame(frame, text="Layout Options")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Max rows
        ttk.Label(options_frame, text="Max Rows per Sheet:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.IntVar(value=self.settings.sheet_layout.max_rows_per_sheet)
        self.sheet_vars["max_rows_per_sheet"] = var
        ttk.Spinbox(options_frame, from_=100, to=10000, increment=100, textvariable=var).grid(row=0, column=1, padx=5, pady=2)
        
        # Decimal places
        ttk.Label(options_frame, text="Decimal Places:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.IntVar(value=self.settings.sheet_layout.decimal_places)
        self.sheet_vars["decimal_places"] = var
        ttk.Spinbox(options_frame, from_=0, to=6, textvariable=var).grid(row=1, column=1, padx=5, pady=2)
    
    def create_analysis_tab(self, notebook):
        """Create analysis settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Analysis")
        
        # Analysis parameters
        analysis_frame = ttk.LabelFrame(frame, text="Analysis Parameters")
        analysis_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.analysis_vars = {}
        
        # Poisson lookback days
        ttk.Label(analysis_frame, text="Poisson Lookback Days:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.IntVar(value=self.settings.analysis.poisson_lookback_days)
        self.analysis_vars["poisson_lookback_days"] = var
        ttk.Spinbox(analysis_frame, from_=7, to=90, textvariable=var).grid(row=0, column=1, padx=5, pady=2)
        
        # EV threshold
        ttk.Label(analysis_frame, text="EV Threshold:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        var = tk.DoubleVar(value=self.settings.analysis.ev_threshold)
        self.analysis_vars["ev_threshold"] = var
        ttk.Scale(analysis_frame, from_=0.01, to=0.20, variable=var, orient=tk.HORIZONTAL).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(analysis_frame, textvariable=var).grid(row=1, column=2, padx=5, pady=2)
        
        analysis_frame.columnconfigure(1, weight=1)
    
    def create_advanced_tab(self, notebook):
        """Create advanced settings tab."""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Advanced")
        
        # Display current settings as text
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display current settings
        settings_text = json.dumps({
            "stat_weights": asdict(self.settings.stat_weights),
            "confidence": asdict(self.settings.confidence),
            "sheet_layout": asdict(self.settings.sheet_layout),
            "analysis": asdict(self.settings.analysis)
        }, indent=2)
        
        text_widget.insert(tk.END, settings_text)
        text_widget.config(state=tk.DISABLED)
    
    def save_settings(self):
        """Save all settings from GUI."""
        try:
            # Update stat weights
            for stat, var in self.batting_vars.items():
                setattr(self.settings.stat_weights, stat, var.get())
            for stat, var in self.pitching_vars.items():
                setattr(self.settings.stat_weights, stat, var.get())
            
            # Update confidence settings
            for setting, var in self.confidence_vars.items():
                setattr(self.settings.confidence, setting, var.get())
            
            # Update sheet layout
            for setting, var in self.sheet_vars.items():
                setattr(self.settings.sheet_layout, setting, var.get())
            
            # Update analysis settings
            for setting, var in self.analysis_vars.items():
                setattr(self.settings.analysis, setting, var.get())
            
            self.settings.save_settings()
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to defaults?"):
            self.settings.reset_to_defaults()
            messagebox.showinfo("Reset Complete", "Settings have been reset to defaults.")
            self.root.destroy()  # Close and reopen GUI
            SettingsGUI(self.settings).run()
    
    def export_settings(self):
        """Export settings to file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.settings.export_settings(file_path)
            messagebox.showinfo("Export Complete", f"Settings exported to {file_path}")
    
    def import_settings(self):
        """Import settings from file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.settings.import_settings(file_path)
            messagebox.showinfo("Import Complete", f"Settings imported from {file_path}")
            self.root.destroy()  # Close and reopen GUI
            SettingsGUI(self.settings).run()
    
    def validate_settings(self):
        """Validate current settings."""
        issues = self.settings.validate_settings()
        if issues:
            message = "Settings validation found the following issues:\n\n" + "\n".join(f"• {issue}" for issue in issues)
            messagebox.showwarning("Validation Issues", message)
        else:
            messagebox.showinfo("Validation Success", "All settings are valid!")
    
    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Main function for testing the settings system."""
    print("⚙️ MLB Analytics User Settings System")
    print("=" * 40)
    
    # Initialize settings
    settings = MLBUserSettings()
    
    print("1. Open Settings GUI")
    print("2. Display current settings")
    print("3. Test settings validation")
    print("4. Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        gui = SettingsGUI(settings)
        gui.run()
    
    elif choice == "2":
        print("\nCurrent Settings:")
        print("-" * 20)
        print(f"Stat Weights: {asdict(settings.stat_weights)}")
        print(f"Confidence: {asdict(settings.confidence)}")
        print(f"Sheet Layout: {asdict(settings.sheet_layout)}")
        print(f"Analysis: {asdict(settings.analysis)}")
    
    elif choice == "3":
        issues = settings.validate_settings()
        if issues:
            print("Validation Issues:")
            for issue in issues:
                print(f"• {issue}")
        else:
            print("✅ All settings are valid!")
    
    elif choice == "4":
        print("👋 Goodbye!")
    
    else:
        print("❌ Invalid option")


if __name__ == "__main__":
    main()

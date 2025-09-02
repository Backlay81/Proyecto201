"""
Sistema de tracking de consumo de API en tiempo real
Se resetea automáticamente cada día a las 00:00
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List

class APIUsageTracker:
    """Tracker para monitorear el consumo de API en tiempo real"""
    
    def __init__(self, data_file="api_usage_log.json"):
        self.data_file = os.path.join(os.path.dirname(__file__), data_file)
        self.daily_quota = 10000
        self.load_data()
        self.check_daily_reset()
    
    def load_data(self):
        """Cargar datos del archivo o crear estructura inicial"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                self.data = self.create_initial_structure()
                self.save_data()
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.data = self.create_initial_structure()
    
    def create_initial_structure(self):
        """Crear estructura inicial de datos"""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            "current_date": today,
            "daily_usage": {
                "youtube_units": 0,
                "trends_requests": 0,
                "total_requests": 0
            },
            "daily_log": [],
            "historical": {}
        }
    
    def check_daily_reset(self):
        """Verificar si necesitamos resetear por nuevo día"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        if self.data.get("current_date") != today:
            # Guardar datos del día anterior en histórico
            if self.data.get("current_date"):
                self.data["historical"][self.data["current_date"]] = {
                    "daily_usage": self.data["daily_usage"].copy(),
                    "total_requests": len(self.data["daily_log"])
                }
            
            # Resetear para el nuevo día
            self.data["current_date"] = today
            self.data["daily_usage"] = {
                "youtube_units": 0,
                "trends_requests": 0,
                "total_requests": 0
            }
            self.data["daily_log"] = []
            self.save_data()
            print(f"📅 Nuevo día detectado: {today} - Contadores reseteados")
    
    def log_youtube_request(self, operation: str, units: int, keyword: str = "", details: str = ""):
        """Registrar un request de YouTube API"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "api": "youtube",
            "operation": operation,
            "units": units,
            "keyword": keyword,
            "details": details
        }
        
        self.data["daily_log"].append(log_entry)
        self.data["daily_usage"]["youtube_units"] += units
        self.data["daily_usage"]["total_requests"] += 1
        
        self.save_data()
        
        # Mostrar información en tiempo real
        remaining = self.daily_quota - self.data["daily_usage"]["youtube_units"]
        percentage = (self.data["daily_usage"]["youtube_units"] / self.daily_quota) * 100
        
        print(f"📊 YouTube API: +{units} unidades | Total: {self.data['daily_usage']['youtube_units']}/{self.daily_quota} ({percentage:.1f}%) | Restantes: {remaining}")
        
        if percentage > 80:
            print("🚨 ALERTA: Has superado el 80% de tu cuota diaria")
        elif percentage > 60:
            print("⚠️  CUIDADO: Has superado el 60% de tu cuota diaria")
    
    def log_trends_request(self, keyword: str = "", details: str = ""):
        """Registrar un request de Google Trends (gratis)"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "api": "trends",
            "operation": "trend_query",
            "units": 0,  # Trends es gratis
            "keyword": keyword,
            "details": details
        }
        
        self.data["daily_log"].append(log_entry)
        self.data["daily_usage"]["trends_requests"] += 1
        self.data["daily_usage"]["total_requests"] += 1
        
        self.save_data()
        print(f"📈 Trends API: {keyword} (GRATIS) | Total requests: {self.data['daily_usage']['trends_requests']}")
    
    def get_current_status(self):
        """Obtener estado actual del consumo"""
        usage = self.data["daily_usage"]
        remaining = self.daily_quota - usage["youtube_units"]
        percentage = (usage["youtube_units"] / self.daily_quota) * 100
        
        return {
            "date": self.data["current_date"],
            "youtube_units_used": usage["youtube_units"],
            "youtube_units_remaining": remaining,
            "percentage_used": percentage,
            "trends_requests": usage["trends_requests"],
            "total_requests": usage["total_requests"],
            "daily_quota": self.daily_quota
        }
    
    def show_status(self):
        """Mostrar estado actual detallado"""
        status = self.get_current_status()
        
        print(f"\n🎯 ESTADO ACTUAL - {status['date']}")
        print("=" * 50)
        print(f"📊 YouTube API:")
        print(f"   • Usado: {status['youtube_units_used']:,}/{status['daily_quota']:,} unidades")
        print(f"   • Porcentaje: {status['percentage_used']:.2f}%")
        print(f"   • Restante: {status['youtube_units_remaining']:,} unidades")
        print(f"📈 Trends API: {status['trends_requests']} requests (GRATIS)")
        print(f"📱 Total requests: {status['total_requests']}")
        
        # Estimación de análisis restantes
        if len(self.data["daily_log"]) > 0:
            recent_analyses = self.estimate_recent_analyses()
            if recent_analyses > 0:
                avg_per_analysis = status['youtube_units_used'] / recent_analyses
                remaining_analyses = status['youtube_units_remaining'] / avg_per_analysis
                print(f"🔮 Análisis restantes estimados: {int(remaining_analyses)}")
    
    def estimate_recent_analyses(self):
        """Estimar cuántos análisis completos se han hecho"""
        # Buscar patrones de análisis completos en los logs
        analysis_count = 0
        current_analysis = set()
        
        for log in self.data["daily_log"]:
            if log["api"] == "youtube" and log["operation"] == "search":
                if log["keyword"] not in current_analysis:
                    current_analysis.add(log["keyword"])
                    if len(current_analysis) % 3 == 0:  # Cada 3 keywords = 1 análisis
                        analysis_count += 1
        
        return max(1, analysis_count)  # Mínimo 1
    
    def show_recent_activity(self, last_n=10):
        """Mostrar actividad reciente"""
        print(f"\n📋 ÚLTIMOS {last_n} REQUESTS:")
        print("-" * 60)
        
        recent_logs = self.data["daily_log"][-last_n:]
        
        for log in recent_logs:
            time_str = datetime.fromisoformat(log["timestamp"]).strftime("%H:%M:%S")
            api_icon = "📊" if log["api"] == "youtube" else "📈"
            units_str = f"{log['units']} units" if log['units'] > 0 else "GRATIS"
            keyword_str = f" - {log['keyword']}" if log.get('keyword') else ""
            
            print(f"{time_str} {api_icon} {log['operation']}: {units_str}{keyword_str}")
    
    def save_data(self):
        """Guardar datos en archivo"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando datos: {e}")

# Instancia global del tracker
tracker = APIUsageTracker()

def track_youtube_search(keyword: str):
    """Wrapper para trackear búsquedas de YouTube"""
    tracker.log_youtube_request("search", 100, keyword, "YouTube search.list()")

def track_youtube_videos(keyword: str, video_count: int = 1):
    """Wrapper para trackear consultas de videos"""
    # videos.list() tiene coste por REQUEST, no por número de ids: contabilizamos 1 unidad por llamada
    tracker.log_youtube_request("videos", 1, keyword, f"YouTube videos.list() - {video_count} videos")

def track_trends_query(keyword: str):
    """Wrapper para trackear consultas de Trends"""
    tracker.log_trends_request(keyword, "Google Trends query")

def show_current_usage():
    """Función rápida para mostrar el uso actual"""
    tracker.show_status()
    tracker.show_recent_activity()

if __name__ == "__main__":
    # Test del sistema
    print("🧪 TESTING SISTEMA DE TRACKING")
    show_current_usage()

#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge, Counter
import time
from mcstatus import JavaServer
import os
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Метрики Prometheus
MINECRAFT_PLAYERS_ONLINE = Gauge('minecraft_players_online', 'Number of players online')
MINECRAFT_PLAYERS_MAX = Gauge('minecraft_players_max', 'Maximum number of players')
MINECRAFT_SERVER_UP = Gauge('minecraft_server_up', 'Server status (1 = up, 0 = down)')
MINECRAFT_LATENCY = Gauge('minecraft_latency_ms', 'Server latency in milliseconds')
MINECRAFT_SCRAPE_COUNT = Counter('minecraft_scrape_count', 'Number of scrapes')
MINECRAFT_SCRAPE_ERRORS = Counter('minecraft_scrape_errors', 'Number of scrape errors')

class MinecraftExporter:
    def __init__(self, host='localhost', port=25565, scrape_interval=30):
        self.host = host
        self.port = port
        self.scrape_interval = scrape_interval
        self.server = JavaServer.lookup(f"{host}:{port}")

    def scrape_metrics(self):
        try:
            # Получаем статус сервера
            status = self.server.status()
            
            # Устанавливаем метрики
            MINECRAFT_PLAYERS_ONLINE.set(status.players.online)
            MINECRAFT_PLAYERS_MAX.set(status.players.max)
            MINECRAFT_LATENCY.set(status.latency)
            MINECRAFT_SERVER_UP.set(1)
            
            logger.info(f"Scrape successful: {status.players.online} players online")
            
        except Exception as e:
            MINECRAFT_SERVER_UP.set(0)
            MINECRAFT_SCRAPE_ERRORS.inc()
            logger.error(f"Error scraping metrics: {e}")
        
        MINECRAFT_SCRAPE_COUNT.inc()

    def run(self):
        logger.info(f"Starting Minecraft exporter for {self.host}:{self.port}")
        logger.info(f"Scrape interval: {self.scrape_interval} seconds")
        
        start_http_server(8000)
        logger.info("HTTP server started on port 8000")
        
        while True:
            self.scrape_metrics()
            time.sleep(self.scrape_interval)

if __name__ == '__main__':
    host = os.getenv('MINECRAFT_HOST', 'localhost')
    port = int(os.getenv('MINECRAFT_PORT', 25565))
    scrape_interval = int(os.getenv('SCRAPE_INTERVAL', 30))
    
    exporter = MinecraftExporter(host, port, scrape_interval)
    exporter.run()
import asyncio
from datetime import date, datetime
from typing import Any , Dict , Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.infrastructure.victoria_client import VictoriaMetricsClient
from app.schemas.request import MetricsAnalysisRequest
from app.domain.models import TestRun
import httpx


class AnalysisService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.vic_client = VictoriaMetricsClient()

    async def resolve_time_range(self, req: MetricsAnalysisRequest) -> Tuple[datetime,datetime]:
        """ take the test round time range from database"""

        if req.selection_mode == "test_round":
            test_run = await self.db.get(TestRun, req.test_round_id)
            if not test_run or not test_run.end_time:
                raise ValueError("Valid complete test Round not found in database")
            start , end = test_run.start_time, test_run.end_time

        elif req.selection_mode == "manual":
            start , end = req.manual_start, req.manual_end
        try:
            final_start = start if isinstance(start, datetime) else datetime.fromisoformat(str(start))
            final_end = end if isinstance(end, datetime) else datetime.fromisoformat(str(end))
            return final_start, final_end
        except (ValueError, TypeError) as e:
            raise ValueError(f"Could not convert time range to datetime objects: {e}")

    async def get_time_offset(self) -> float:
        """calculate how many seconds victoria metrics is ahead/behind.
        Formula : (VM_now) - (Local_now)
        """

        endpoint = f"{settings.VICTORIA_URL}/api/v1/query?query=up"
        async with httpx.AsyncClient() as client:
            resp = await client.get(endpoint)
            vm_now = float(resp.json()["data"]["result"][0]["value"][0])
            local_now = datetime.now().timestamp()

            offset = vm_now - local_now
            print(f"--- TIME CALIBRATION: Host is {offset/86400:.2f} days ahead ---")
            return offset



    async def execute_analysis(self , req: MetricsAnalysisRequest) -> Dict[str, Any]:
        start , end = await self.resolve_time_range(req)
        offset_seconds = await self.get_time_offset()

        db_start = datetime.fromtimestamp(start.timestamp() + offset_seconds)
        db_end = datetime.fromtimestamp(end.timestamp() + offset_seconds)


        win = req.lookback_window

        queries = {
            "latency_p95": f'quantile_over_time(0.95, probe_duration_seconds{{job="{req.blackbox_probe_name}"}}[{win}])',
            "latency_std": f'stddev_over_time(probe_duration_seconds{{job="{req.blackbox_probe_name}"}}[{win}])',
            "error_rate": f'1 - avg_over_time(probe_success{{job="{req.blackbox_probe_name}"}}[{win}])',

        
            "cpu_usage_rate": f'rate(container_cpu_usage_seconds_total{{container_label_com_docker_compose_service="{req.container_name}"}}[{win}])',
            "memory_usage": f'avg_over_time(container_memory_usage_bytes{{container_label_com_docker_compose_service="{req.container_name}"}}[{win}])',
            "net_throughput": (
                f'rate(container_network_receive_bytes_total{{container_label_com_docker_compose_service="{req.container_name}"}}[{win}]) + '
                f'rate(container_network_transmit_bytes_total{{container_label_com_docker_compose_service="{req.container_name}"}}[{win}])'
            ),

            
            "disk_io_rate": f'rate(node_disk_io_time_seconds_total[{win}])',
            "node_cpu_total": f'rate(node_cpu_seconds_total[{win}])',

            "container_memory_usage_bytes": f'container_memory_usage_bytes{{container_label_com_docker_compose_service="{req.container_name}"}}',
            "container_start_time_seconds" : f'container_start_time_seconds{{container_label_com_docker_compose_service="{req.container_name}"}}',
            "probe_success": f'probe_success{{job="{req.blackbox_probe_name}"}}',
            "node_memory_MemAvailable_bytes":'node_memory_MemAvailable_bytes'

        }

        keys = list(queries.keys())
        tasks = [self.vic_client.get_metrics_range(query=queries[k], start_time=db_start, end_time=db_end , step = "30s") for k in keys]

        results_list = await asyncio.gather(*tasks)

        return {
            "calibration":{"offset_seconds":offset_seconds},
            "data":dict(zip(keys,results_list))
        }
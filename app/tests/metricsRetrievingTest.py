import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from app.domain.services.dataRetrieving import AnalysisService
from app.schemas.request import MetricsAnalysisRequest
from app.core.config import settings

# 1. Setup a temporary DB connection for the test
engine = create_async_engine(str(settings.DATABASE_URL))
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def test_analysis_logic():
    async with async_session() as db:
        service = AnalysisService(db)
        
        mock_req = MetricsAnalysisRequest(
            application_id=1,
            blackbox_probe_name="blackbox-app",
            container_name="backend",
            lookback_window="5m",
            selection_mode="manual",
            manual_start=datetime(2026, 3, 27, 10, 0),
            manual_end=datetime(2026, 3, 27, 11, 0)
        )

        print("--- Phase 1: Testing Time Calibration ---")
        offset = await service.get_time_offset()
        print(f"Detected Offset: {offset} seconds")

        print("\n--- Phase 2: Executing Full Multi-Query Analysis ---")
        try:
            report = await service.execute_analysis(mock_req)
            
            # 3. Check the results
            metrics_received = list(report['data'].keys())
            print(f"Successfully fetched: {metrics_received}")
            
            # Check if one specific metric has data
            if report['data']['cpu_usage_rate']:
                print("✅ CPU Data Points found!")
                print(f"Sample: {report['data']['cpu_usage_rate'][0]['values'][:2]}")
                for key, data in report["data"].items():
                    if not data:
                        print(f"⚠️ {key}: Fetched successfully, but returned NO data points.")
                    else:
                        print(f"✅ {key}: Found {len(data[0]['values'])} data points.")
            else:
                print("⚠️ Query successful but result was empty (Check labels).")

        except Exception as e:
            print(f"❌ Analysis Failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_analysis_logic())
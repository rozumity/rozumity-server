import asyncio
import logging

logger = logging.getLogger(__name__)

def run_background_calculation(instance):
    """
    Schedules the calculation in the background without blocking the response.
    """
    task = asyncio.create_task(instance.calculate_scores(save=True))
    
    # Добавляем callback для обработки ошибок в фоне
    def handle_result(t):
        try:
            t.result()
        except Exception as e:
            logger.error(f"Background calculation failed for Response {instance.id}: {e}")

    task.add_done_callback(handle_result)

#async def update(self, request, *args, **kwargs):
#    response = await super().update(request, *args, **kwargs)
#    instance = await self.get_object()
#    if request.data.get('is_filled') is True:
#        run_background_calculation(instance)
#    return response

"""Celery async tasks for background processing."""
from services.celery_app import celery_app
from services.image_service import apply_adjustments, ai_auto_enhance, remove_background
from services.audio_service import noise_reduction, trim_silence, analyze_audio
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="tasks.process_image")
def process_image_task(self, project_id: str, input_path: str, output_path: str, settings: dict):
    try:
        self.update_state(state="PROGRESS", meta={"step": "Applying adjustments"})
        if settings.get("mode") == "ai":
            result = ai_auto_enhance(input_path, output_path)
        else:
            result = apply_adjustments(input_path, output_path, settings)
        return {"status": "done", "output": output_path, "ai_results": result if isinstance(result, dict) else {}}
    except Exception as e:
        logger.error(f"Image task failed: {e}")
        raise self.retry(exc=e, countdown=5, max_retries=2)

@celery_app.task(bind=True, name="tasks.process_audio")
def process_audio_task(self, project_id: str, input_path: str, output_path: str, settings: dict):
    try:
        self.update_state(state="PROGRESS", meta={"step": "Analyzing audio"})
        analysis = analyze_audio(input_path)
        if settings.get("noise_reduction"):
            self.update_state(state="PROGRESS", meta={"step": "Reducing noise"})
            noise_reduction(input_path, output_path, strength=settings.get("noise_strength", 0.75))
        if settings.get("trim_silence"):
            trim_silence(output_path or input_path, output_path)
        return {"status": "done", "output": output_path, "analysis": analysis}
    except Exception as e:
        logger.error(f"Audio task failed: {e}")
        raise self.retry(exc=e, countdown=5, max_retries=2)

@celery_app.task(name="tasks.remove_bg")
def remove_bg_task(project_id: str, input_path: str, output_path: str):
    try:
        result_path = remove_background(input_path, output_path)
        return {"status": "done", "output": result_path}
    except Exception as e:
        logger.error(f"BG removal failed: {e}")
        return {"status": "failed", "error": str(e)}

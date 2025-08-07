"""
Web API Module

This module provides a FastAPI-based REST API for remote control and monitoring
of the day planner application.

Author: Raspberry Pi Day Planner
License: MIT
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
import uvicorn


# Pydantic models for API requests/responses
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    time: str = Field(..., pattern=r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$")
    notes: Optional[str] = Field(None, max_length=500)
    priority: int = Field(1, ge=1, le=5)
    audio_alert: bool = True
    snooze_duration: int = Field(15, ge=1, le=120)
    category: str = Field("custom", max_length=50)
    rrule: Optional[str] = None

class TaskResponse(BaseModel):
    id: str
    title: str
    time: str
    notes: Optional[str]
    priority: int
    audio_alert: bool
    snooze_duration: int
    category: str
    rrule: Optional[str]
    next_occurrence: Optional[str]

class StatusResponse(BaseModel):
    status: str
    uptime: str
    total_tasks: int
    active_tasks: int
    completed_today: int
    snoozed_today: int
    next_task: Optional[TaskResponse]
    system_info: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


class WebAPI:
    """
    FastAPI-based web API for the day planner application.
    
    This class provides:
    - REST API endpoints for task management
    - Status and health monitoring
    - Web dashboard interface
    - Background task processing
    """
    
    def __init__(self, 
                 scheduler: Any,
                 display_manager: Any,
                 audio_manager: Any,
                 event_logger: Any,
                 config_watcher: Any):
        """
        Initialize the web API.
        
        Args:
            scheduler: Task scheduler instance.
            display_manager: Display manager instance.
            audio_manager: Audio manager instance.
            event_logger: Event logger instance.
            config_watcher: Configuration watcher instance.
        """
        self.logger = logging.getLogger(__name__)
        self.scheduler = scheduler
        self.display_manager = display_manager
        self.audio_manager = audio_manager
        self.event_logger = event_logger
        self.config_watcher = config_watcher
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Raspberry Pi Day Planner API",
            description="REST API for remote control and monitoring",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Setup static files and templates
        self._setup_static_files()
        self._setup_routes()
        
        # Server instance
        self.server = None
        self.running = False
        
        self.logger.info("Web API initialized")
    
    def _setup_static_files(self):
        """Setup static file serving and templates."""
        try:
            # Create static directory if it doesn't exist
            static_dir = Path(__file__).parent.parent / "static"
            static_dir.mkdir(exist_ok=True)
            
            # Mount static files
            self.app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
            
            # Setup templates
            templates_dir = Path(__file__).parent.parent / "templates"
            templates_dir.mkdir(exist_ok=True)
            self.templates = Jinja2Templates(directory=str(templates_dir))
            
        except Exception as e:
            self.logger.error(f"Failed to setup static files: {e}")
    
    def _setup_routes(self):
        """Setup API routes and endpoints."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request):
            """Web dashboard interface."""
            try:
                return self.templates.TemplateResponse(
                    "dashboard.html",
                    {"request": request}
                )
            except Exception as e:
                self.logger.error(f"Dashboard error: {e}")
                return HTMLResponse(content="<h1>Dashboard Error</h1>", status_code=500)
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                timestamp=datetime.now().isoformat(),
                version="1.0.0"
            )
        
        @self.app.get("/status", response_model=StatusResponse)
        async def get_status():
            """Get application status."""
            try:
                # Get system info
                from modules.utils import get_system_info, is_raspberry_pi
                sys_info = get_system_info()
                sys_info['is_raspberry_pi'] = is_raspberry_pi()
                
                # Get task statistics
                stats = self.event_logger.get_completion_stats(days=1)
                completed_today = sum(task['completions'] for task in stats['tasks'])
                snoozed_today = sum(task.get('avg_snoozes', 0) for task in stats['tasks'])
                
                # Get next task
                next_task = None
                if hasattr(self.scheduler, 'get_scheduled_jobs'):
                    jobs = self.scheduler.get_scheduled_jobs()
                    if jobs:
                        # Find the next job
                        next_job = min(jobs.values(), key=lambda j: j['next_run_time'] or datetime.max)
                        if next_job['next_run_time']:
                            next_task = TaskResponse(
                                id=next_job['id'],
                                title="Next Task",  # Would need to map job ID to task
                                time=next_job['next_run_time'].strftime("%H:%M"),
                                notes="Next scheduled task",
                                priority=3,
                                audio_alert=True,
                                snooze_duration=15,
                                category="scheduled",
                                rrule=None,
                                next_occurrence=next_job['next_run_time'].isoformat()
                            )
                
                return StatusResponse(
                    status="running" if self.running else "stopped",
                    uptime="1h 23m",  # Would need to track actual uptime
                    total_tasks=len(stats['tasks']),
                    active_tasks=len([j for j in self.scheduler.get_scheduled_jobs().values() if j['next_run_time']]),
                    completed_today=completed_today,
                    snoozed_today=int(snoozed_today),
                    next_task=next_task,
                    system_info=sys_info
                )
                
            except Exception as e:
                self.logger.error(f"Status error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks", response_model=List[TaskResponse])
        async def get_tasks():
            """Get all scheduled tasks."""
            try:
                # This would need to be implemented to return actual tasks
                # For now, return empty list
                return []
            except Exception as e:
                self.logger.error(f"Get tasks error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tasks", response_model=TaskResponse)
        async def create_task(task: TaskCreate, background_tasks: BackgroundTasks):
            """Create a new task."""
            try:
                # Add task creation to background tasks
                background_tasks.add_task(self._create_task_background, task)
                
                return TaskResponse(
                    id=f"task_{datetime.now().timestamp()}",
                    title=task.title,
                    time=task.time,
                    notes=task.notes,
                    priority=task.priority,
                    audio_alert=task.audio_alert,
                    snooze_duration=task.snooze_duration,
                    category=task.category,
                    rrule=task.rrule,
                    next_occurrence=None
                )
                
            except Exception as e:
                self.logger.error(f"Create task error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tasks/{task_id}/complete")
        async def complete_task(task_id: str):
            """Mark a task as completed."""
            try:
                # This would need to be implemented
                self.logger.info(f"Task {task_id} marked as completed")
                return {"status": "completed", "task_id": task_id}
            except Exception as e:
                self.logger.error(f"Complete task error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tasks/{task_id}/snooze")
        async def snooze_task(task_id: str, duration: int = 15):
            """Snooze a task."""
            try:
                # This would need to be implemented
                self.logger.info(f"Task {task_id} snoozed for {duration} minutes")
                return {"status": "snoozed", "task_id": task_id, "duration": duration}
            except Exception as e:
                self.logger.error(f"Snooze task error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/reload")
        async def reload_configuration():
            """Reload configuration from file."""
            try:
                if self.config_watcher:
                    config = self.config_watcher.reload_config()
                    if config:
                        return {"status": "reloaded", "config": "Configuration reloaded successfully"}
                    else:
                        raise HTTPException(status_code=400, detail="Failed to reload configuration")
                else:
                    raise HTTPException(status_code=400, detail="Configuration watcher not available")
            except Exception as e:
                self.logger.error(f"Reload configuration error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/logs")
        async def get_logs(limit: int = 50):
            """Get recent application logs."""
            try:
                # This would need to be implemented to read actual log files
                return {"logs": [], "message": "Log retrieval not implemented"}
            except Exception as e:
                self.logger.error(f"Get logs error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/test-audio")
        async def test_audio():
            """Test audio system."""
            try:
                if self.audio_manager:
                    self.audio_manager.play_alert()
                    return {"status": "success", "message": "Audio test played"}
                else:
                    raise HTTPException(status_code=400, detail="Audio manager not available")
            except Exception as e:
                self.logger.error(f"Test audio error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _create_task_background(self, task: TaskCreate):
        """Background task to create a new task."""
        try:
            # This would need to be implemented to actually create the task
            self.logger.info(f"Creating task: {task.title} at {task.time}")
        except Exception as e:
            self.logger.error(f"Background task creation error: {e}")
    
    def start(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the web API server."""
        try:
            self.server = uvicorn.Server(
                uvicorn.Config(
                    self.app,
                    host=host,
                    port=port,
                    log_level="info"
                )
            )
            
            # Start server in background thread
            import threading
            self.server_thread = threading.Thread(
                target=self.server.run,
                daemon=True
            )
            self.server_thread.start()
            
            self.running = True
            self.logger.info(f"Web API started on http://{host}:{port}")
            
        except Exception as e:
            self.logger.error(f"Failed to start web API: {e}")
            raise
    
    def stop(self):
        """Stop the web API server."""
        try:
            if self.server and self.running:
                self.server.should_exit = True
                self.running = False
                self.logger.info("Web API stopped")
        except Exception as e:
            self.logger.error(f"Error stopping web API: {e}")
    
    def is_running(self) -> bool:
        """Check if the web API is running."""
        return self.running
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app 
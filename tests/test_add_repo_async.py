import unittest
from unittest.mock import AsyncMock, patch
import sys
import types


class _DummyFastAPI:
    def __init__(self, *args, **kwargs):
        pass

    def post(self, *args, **kwargs):
        return lambda fn: fn

    def get(self, *args, **kwargs):
        return lambda fn: fn


class _DummyScheduler:
    def remove_all_jobs(self):
        pass

    def add_job(self, *args, **kwargs):
        pass

    def start(self):
        pass


def _install_test_stubs():
    fastapi_module = types.ModuleType("fastapi")
    fastapi_module.FastAPI = _DummyFastAPI
    fastapi_module.Request = object
    fastapi_module.Form = lambda *args, **kwargs: None
    sys.modules["fastapi"] = fastapi_module

    templating_module = types.ModuleType("fastapi.templating")
    templating_module.Jinja2Templates = lambda *args, **kwargs: types.SimpleNamespace(TemplateResponse=lambda *a, **k: {})
    sys.modules["fastapi.templating"] = templating_module

    responses_module = types.ModuleType("fastapi.responses")
    responses_module.FileResponse = object
    responses_module.RedirectResponse = object
    sys.modules["fastapi.responses"] = responses_module

    scheduler_module = types.ModuleType("apscheduler.schedulers.background")
    scheduler_module.BackgroundScheduler = _DummyScheduler
    sys.modules["apscheduler.schedulers.background"] = scheduler_module

    cron_module = types.ModuleType("apscheduler.triggers.cron")
    cron_module.CronTrigger = types.SimpleNamespace(from_crontab=lambda expr: expr)
    sys.modules["apscheduler.triggers.cron"] = cron_module

    yaml_module = types.ModuleType("yaml")
    yaml_module.safe_load = lambda *_args, **_kwargs: {}
    yaml_module.dump = lambda *_args, **_kwargs: None
    sys.modules["yaml"] = yaml_module

    git_module = types.ModuleType("git")
    git_module.Repo = types.SimpleNamespace(clone_from=lambda *args, **kwargs: None)
    sys.modules["git"] = git_module


_install_test_stubs()

import main


class AddRepoAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_add_repo_schedules_background_mirror_for_new_repo(self):
        repo_url = "https://github.com/example/project.git"
        config = {"repositories": []}

        with patch.object(main, "load_config", return_value=config), patch.object(main, "save_config") as save_config, patch.object(main, "start_background_mirror", new_callable=AsyncMock) as background_mirror:
            response = await main.add_repo(repo_url=repo_url)

        self.assertEqual(response, {"status": "success"})
        self.assertIn(repo_url, config["repositories"])
        save_config.assert_called_once_with(config)
        background_mirror.assert_awaited_once_with(repo_url)

    async def test_add_repo_does_not_schedule_for_existing_repo(self):
        repo_url = "https://github.com/example/project.git"
        config = {"repositories": [repo_url]}

        with patch.object(main, "load_config", return_value=config), patch.object(main, "save_config") as save_config, patch.object(main, "start_background_mirror", new_callable=AsyncMock) as background_mirror:
            response = await main.add_repo(repo_url=repo_url)

        self.assertEqual(response, {"status": "success"})
        save_config.assert_not_called()
        background_mirror.assert_not_called()


if __name__ == "__main__":
    unittest.main()

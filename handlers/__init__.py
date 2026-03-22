from aiogram import Router
from . import commands, quiz, settings

# This collects all sub-routers into one main router
router = Router()
router.include_routers(
    commands.router,
    quiz.router,
    settings.router
)
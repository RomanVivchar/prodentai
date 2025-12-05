"""
Reminder scheduler for Telegram Bot
Sends reminders to users at scheduled times
"""

import asyncio
import logging
from datetime import datetime, time

import httpx
from config import Config

logger = logging.getLogger(__name__)


async def reminder_scheduler(bot):
    """Background task to send reminders to users"""
    logger.info("Reminder scheduler started")
    
    while True:
        try:
            # Get current time
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            
            # Get all active reminders for current time
            async with httpx.AsyncClient() as client:
                try:
                    api_endpoints = Config.get_api_endpoints()
                    # Get all users with reminders
                    users_response = await client.get(f"{api_endpoints['users']}/all-telegram-users")
                    
                    if users_response.status_code == 200:
                        users = users_response.json()
                        
                        for user in users:
                            user_id = user.get("id")
                            telegram_id = user.get("telegram_id")
                            
                            if not telegram_id:
                                continue
                            
                            # Get user's reminders
                            reminders_response = await client.get(
                                f"{api_endpoints['reminders']}/user/{user_id}"
                            )
                            
                            if reminders_response.status_code == 200:
                                reminders = reminders_response.json()
                                
                                for reminder in reminders:
                                    if not reminder.get("is_active"):
                                        continue
                                    
                                    reminder_time = reminder.get("time", "")
                                    reminder_date = reminder.get("date")
                                    
                                    # Check if time matches
                                    if reminder_time == current_time:
                                        # Check date if specified (for dental_visit)
                                        if reminder_date:
                                            reminder_date_obj = datetime.strptime(reminder_date, "%Y-%m-%d")
                                            if reminder_date_obj.date() != now.date():
                                                continue
                                        
                                        # Send reminder
                                        message = reminder.get("message", "Напоминание о гигиене")
                                        try:
                                            await bot.send_message(
                                                chat_id=telegram_id,
                                                text=message
                                            )
                                            logger.info(
                                                f"Sent reminder to user {telegram_id} (user_id: {user_id})"
                                            )
                                        except Exception as e:
                                            logger.error(
                                                f"Error sending reminder to {telegram_id}: {e}"
                                            )
                
                except Exception as e:
                    logger.error(f"Error in reminder scheduler: {e}")
            
            # Wait 60 seconds before next check
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in reminder scheduler loop: {e}")
            await asyncio.sleep(60)


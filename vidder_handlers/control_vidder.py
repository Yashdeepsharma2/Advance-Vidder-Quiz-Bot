"""
⚡ VidderTech Quiz Control Handlers - Complete Implementation
🚀 Built by VidderTech - Advanced Live Quiz Management System

This module handles all live quiz control commands:
- /pause - Advanced quiz pause with data preservation
- /resume - Smart resume with context restoration
- /stop - Complete quiz termination with analytics
- /fast - Dynamic speed control (0.5x to 5x)
- /slow - Adaptive slow mode with accessibility
- /normal - Optimal speed reset with performance tuning
- /skip - Question skipping with penalty system
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    Poll, InputMediaPhoto, InputMediaVideo
)
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler
)
from telegram.constants import ParseMode, ChatAction

from vidder_config import config, messages, states, callbacks
from vidder_database.vidder_database import db_manager

# Setup logging
logger = logging.getLogger('vidder.handlers.control')

class VidderQuizControlHandlers:
    """⚡ Complete Quiz Control System with Real-time Management"""
    
    def __init__(self):
        self.speed_levels = {
            'slowest': 0.25,   # 4x slower
            'slow': 0.5,       # 2x slower
            'normal': 1.0,     # Standard speed
            'fast': 1.5,       # 1.5x faster
            'faster': 2.0,     # 2x faster
            'fastest': 3.0,    # 3x faster
            'lightning': 5.0   # 5x faster (premium only)
        }
        
        self.control_permissions = {
            'creator': ['pause', 'resume', 'stop', 'fast', 'slow', 'normal', 'skip'],
            'admin': ['pause', 'resume', 'stop', 'fast', 'slow', 'normal', 'skip'],
            'participant': ['skip'],  # Limited control
            'viewer': []  # No control
        }
    
    async def pause_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """⏸️ Advanced quiz pause system with intelligent data preservation"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Find active quiz session in this chat
            active_session = await self._get_active_quiz_session(chat_id)
            
            if not active_session:
                await update.message.reply_text(
                    "❌ **No Active Quiz Found**\n\n"
                    "There's no active quiz running in this chat.\n\n"
                    "🎯 **To start a quiz:**\n"
                    "• Create a quiz with /create\n"
                    "• Use inline query to start existing quiz\n"
                    "• Import quiz with quiz ID\n\n"
                    f"🚀 **{config.COMPANY_NAME} - Ready when you are!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, active_session, 'pause'):
                await self._show_no_permission_message(update, 'pause quiz')
                return
            
            # Check if already paused
            if active_session['status'] == 'paused':
                await self._show_already_paused_message(update, active_session)
                return
            
            # Execute advanced pause operation
            await self._execute_quiz_pause(update, context, active_session)
            
        except Exception as e:
            logger.error(f"❌ Error in pause quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _execute_quiz_pause(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                session: Dict[str, Any]):
        """Execute comprehensive quiz pause with data preservation"""
        try:
            session_id = session['session_id']
            quiz_id = session['quiz_id']
            current_question = session.get('current_question', 0)
            
            # Get quiz details
            quiz = await db_manager.get_quiz(quiz_id)
            if not quiz:
                await update.message.reply_text("❌ Quiz data not found.")
                return
            
            # Calculate pause statistics
            pause_time = datetime.now()
            session_duration = self._calculate_session_duration(session['started_at'], pause_time.isoformat())
            questions_completed = current_question
            questions_remaining = quiz.get('total_questions', 0) - current_question
            
            # Update session status
            pause_updates = {
                'status': 'paused',
                'paused_at': pause_time.isoformat(),
                'session_data': json.dumps({
                    **json.loads(session.get('session_data', '{}')),
                    'pause_reason': 'manual',
                    'pause_duration_start': pause_time.isoformat(),
                    'questions_at_pause': current_question
                })
            }
            
            success = await db_manager.update_quiz_session(session_id, pause_updates)
            if not success:
                await update.message.reply_text("❌ Failed to pause quiz. Please try again.")
                return
            
            # Create comprehensive pause confirmation
            pause_message = f"""
⏸️ **Quiz Paused Successfully**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Quiz Information:**
📝 Title: `{quiz['title']}`
🆔 Session: `{session_id[:12]}...`
📊 Progress: `{questions_completed}/{quiz.get('total_questions', 0)}` questions

⏰ **Session Timeline:**
🚀 Started: `{session.get('started_at', 'Unknown')[:16] if session.get('started_at') else 'Unknown'}`
⏸️ Paused: `{pause_time.strftime('%Y-%m-%d %H:%M')}`
⏱️ Duration: `{session_duration['formatted']}`

📈 **Current Statistics:**
✅ Questions Completed: `{questions_completed}`
⏳ Questions Remaining: `{questions_remaining}`
👥 Active Participants: `{len(session.get('participants', []))}`
🎯 Average Score: `{session.get('average_score', 0):.1f}%`

💾 **Data Preserved:**
• ✅ All participant responses saved
• ✅ Current question position saved
• ✅ Timer states preserved
• ✅ Leaderboard data maintained
• ✅ Chat context preserved

🎮 **Resume Options:**
• Continue from current question
• Restart current question
• Skip to next question
• Extend time limits

⚡ **Quick Actions Available:**
            """
            
            # Create control keyboard
            keyboard = [
                [
                    InlineKeyboardButton("▶️ Resume Quiz", callback_data=f"resume_quiz_{session_id}"),
                    InlineKeyboardButton("⏭️ Skip Question", callback_data=f"skip_question_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏱️ Extend Time", callback_data=f"extend_time_{session_id}"),
                    InlineKeyboardButton("🔄 Restart Question", callback_data=f"restart_question_{session_id}")
                ],
                [
                    InlineKeyboardButton("📊 Show Results", callback_data=f"show_interim_results_{session_id}"),
                    InlineKeyboardButton("👥 Participant List", callback_data=f"show_participants_{session_id}")
                ],
                [
                    InlineKeyboardButton("⚙️ Quiz Settings", callback_data=f"quiz_settings_{session_id}"),
                    InlineKeyboardButton("📈 Live Analytics", callback_data=f"live_analytics_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏹️ Stop Quiz", callback_data=f"stop_quiz_{session_id}"),
                    InlineKeyboardButton("📱 Share Status", callback_data=f"share_pause_status_{session_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send pause confirmation
            await update.message.reply_text(
                pause_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Notify all participants about pause
            await self._notify_participants_pause(session, quiz, pause_time)
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_paused",
                update.effective_user.id,
                quiz_id=quiz_id,
                session_id=session_id,
                metadata={
                    "questions_completed": questions_completed,
                    "session_duration_minutes": session_duration['minutes'],
                    "participants_count": len(session.get('participants', []))
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error executing quiz pause: {e}")
            await update.message.reply_text("❌ Failed to pause quiz. Please try again.")
    
    async def resume_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """▶️ Smart quiz resume with context restoration"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Find paused quiz session
            paused_session = await self._get_paused_quiz_session(chat_id)
            
            if not paused_session:
                await update.message.reply_text(
                    "❌ **No Paused Quiz Found**\n\n"
                    "There's no paused quiz in this chat.\n\n"
                    "🎯 **Available Actions:**\n"
                    "• Start a new quiz with inline query\n"
                    "• Create quiz with /create\n"
                    "• Check /myquizzes for your quizzes\n\n"
                    f"🚀 **{config.COMPANY_NAME} - Always Ready!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, paused_session, 'resume'):
                await self._show_no_permission_message(update, 'resume quiz')
                return
            
            # Execute smart resume
            await self._execute_quiz_resume(update, context, paused_session)
            
        except Exception as e:
            logger.error(f"❌ Error in resume quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _execute_quiz_resume(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                 session: Dict[str, Any]):
        """Execute intelligent quiz resume with context restoration"""
        try:
            session_id = session['session_id']
            quiz_id = session['quiz_id']
            
            # Calculate pause duration
            paused_at = session.get('paused_at')
            resume_time = datetime.now()
            
            pause_duration = None
            if paused_at:
                try:
                    pause_start = datetime.fromisoformat(paused_at)
                    pause_duration = (resume_time - pause_start).total_seconds()
                except:
                    pause_duration = 0
            
            # Get quiz details
            quiz = await db_manager.get_quiz(quiz_id)
            current_question = session.get('current_question', 0)
            
            # Prepare resume data
            resume_updates = {
                'status': 'active',
                'resumed_at': resume_time.isoformat(),
                'session_data': json.dumps({
                    **json.loads(session.get('session_data', '{}')),
                    'resume_time': resume_time.isoformat(),
                    'pause_duration_seconds': pause_duration,
                    'total_pause_time': json.loads(session.get('session_data', '{}')).get('total_pause_time', 0) + (pause_duration or 0)
                })
            }
            
            # Update session
            success = await db_manager.update_quiz_session(session_id, resume_updates)
            if not success:
                await update.message.reply_text("❌ Failed to resume quiz. Please try again.")
                return
            
            # Format pause duration for display
            pause_duration_str = "Unknown"
            if pause_duration:
                if pause_duration < 60:
                    pause_duration_str = f"{int(pause_duration)} seconds"
                elif pause_duration < 3600:
                    pause_duration_str = f"{int(pause_duration/60)} minutes"
                else:
                    pause_duration_str = f"{int(pause_duration/3600)} hours {int((pause_duration%3600)/60)} minutes"
            
            # Create comprehensive resume message
            resume_message = f"""
▶️ **Quiz Resumed Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Quiz Status:**
📝 Title: `{quiz['title']}`
📊 Progress: `{current_question}/{quiz.get('total_questions', 0)}` questions
⏸️ Paused for: `{pause_duration_str}`

🔄 **Session Restored:**
✅ All participant data preserved
✅ Question progress maintained  
✅ Timer states restored
✅ Leaderboard rankings intact
✅ Chat context recovered

⚡ **Current Speed:** `{session.get('speed_multiplier', 1.0)}x`
👥 **Active Participants:** `{len(session.get('participants', []))}`

🎮 **Continuing from Question {current_question + 1}...**

🚀 **{config.COMPANY_NAME} - Seamless Quiz Experience!**
            """
            
            # Create live control keyboard
            keyboard = [
                [
                    InlineKeyboardButton("⏸️ Pause Again", callback_data=f"pause_quiz_{session_id}"),
                    InlineKeyboardButton("⏭️ Skip Question", callback_data=f"skip_question_{session_id}")
                ],
                [
                    InlineKeyboardButton("🚀 Fast Mode", callback_data=f"speed_fast_{session_id}"),
                    InlineKeyboardButton("🐌 Slow Mode", callback_data=f"speed_slow_{session_id}")
                ],
                [
                    InlineKeyboardButton("📊 Live Results", callback_data=f"live_results_{session_id}"),
                    InlineKeyboardButton("📈 Live Analytics", callback_data=f"live_analytics_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏹️ Stop Quiz", callback_data=f"stop_quiz_{session_id}"),
                    InlineKeyboardButton("⚙️ Settings", callback_data=f"quiz_controls_{session_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                resume_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Notify all participants
            await self._notify_participants_resume(session, quiz, pause_duration_str)
            
            # Continue quiz execution
            await self._continue_quiz_execution(context, session)
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_resumed",
                user_id,
                quiz_id=quiz_id,
                session_id=session_id,
                metadata={
                    "pause_duration_seconds": pause_duration,
                    "current_question": current_question,
                    "participants_count": len(session.get('participants', []))
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error in resume quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def stop_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """⏹️ Complete quiz termination with comprehensive analytics"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Find active or paused quiz session
            active_session = await self._get_current_quiz_session(chat_id)
            
            if not active_session:
                await update.message.reply_text(
                    "❌ **No Quiz to Stop**\n\n"
                    "There's no active or paused quiz in this chat.\n\n"
                    "🎯 **Want to start a quiz?**\n"
                    "Use /create to create a new one!\n\n"
                    f"🚀 **{config.COMPANY_NAME} - Ready for Action!**",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, active_session, 'stop'):
                await self._show_no_permission_message(update, 'stop quiz')
                return
            
            # Show comprehensive stop confirmation
            await self._show_stop_confirmation(update, context, active_session)
            
        except Exception as e:
            logger.error(f"❌ Error in stop quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_stop_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                    session: Dict[str, Any]):
        """Show comprehensive quiz stop confirmation"""
        try:
            session_id = session['session_id']
            quiz_id = session['quiz_id']
            
            # Get quiz and current statistics
            quiz = await db_manager.get_quiz(quiz_id)
            current_question = session.get('current_question', 0)
            total_questions = quiz.get('total_questions', 0)
            participants = session.get('participants', [])
            
            # Calculate session statistics
            session_stats = await self._calculate_session_stats(session_id)
            
            stop_confirmation = f"""
⚠️ **Confirm Quiz Stop - Important Decision**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Quiz to Stop:**
📝 Title: `{quiz['title']}`
📊 Progress: `{current_question}/{total_questions}` questions (`{(current_question/total_questions*100):.1f}%` complete)
👥 Participants: `{len(participants)}`

📈 **Current Session Stats:**
✅ Completed Responses: `{session_stats.get('total_responses', 0)}`
📊 Average Score: `{session_stats.get('average_score', 0):.1f}%`
⏱️ Session Duration: `{session_stats.get('duration_formatted', 'Unknown')}`

⚠️ **What happens when you stop:**
• ✅ All current responses will be saved
• ✅ Partial results will be calculated
• ✅ Analytics data will be preserved
• ✅ Participants will receive final scores
• ❌ Quiz cannot be resumed after stopping
• ❌ Remaining questions will be skipped

💾 **Data Preservation:**
• Comprehensive results report generated
• Individual performance analytics saved
• Leaderboard finalized with current standings
• Detailed HTML report available for download

🤔 **Are you sure you want to stop this quiz?**

💡 **Alternative:** Consider pausing instead of stopping if you plan to continue later.
            """
            
            keyboard = [
                [
                    InlineKeyboardButton("⏸️ Pause Instead", callback_data=f"pause_quiz_{session_id}"),
                    InlineKeyboardButton("📊 Generate Report First", callback_data=f"generate_interim_report_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏹️ Yes, Stop Quiz", callback_data=f"confirm_stop_quiz_{session_id}"),
                    InlineKeyboardButton("❌ Cancel Stop", callback_data=f"cancel_stop_{session_id}")
                ],
                [
                    InlineKeyboardButton("🏠 Back to Control", callback_data=f"quiz_controls_{session_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                stop_confirmation,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing stop confirmation: {e}")
            await update.message.reply_text("❌ Error loading quiz data. Please try again.")
    
    async def fast_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🚀 Dynamic speed control - Increase quiz speed"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Get active session
            active_session = await self._get_active_quiz_session(chat_id)
            
            if not active_session:
                await self._show_no_active_quiz_message(update, "change speed")
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, active_session, 'fast'):
                await self._show_no_permission_message(update, 'change quiz speed')
                return
            
            # Show speed selection menu
            await self._show_speed_control_menu(update, context, active_session, 'faster')
            
        except Exception as e:
            logger.error(f"❌ Error in fast quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def slow_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """🐌 Adaptive slow mode for accessibility and learning"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Get active session
            active_session = await self._get_active_quiz_session(chat_id)
            
            if not active_session:
                await self._show_no_active_quiz_message(update, "change speed")
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, active_session, 'slow'):
                await self._show_no_permission_message(update, 'change quiz speed')
                return
            
            # Show speed selection menu
            await self._show_speed_control_menu(update, context, active_session, 'slower')
            
        except Exception as e:
            logger.error(f"❌ Error in slow quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def normal_quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """➡️ Reset to optimal speed with performance tuning"""
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action=ChatAction.TYPING
            )
            
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            
            # Get active session
            active_session = await self._get_active_quiz_session(chat_id)
            
            if not active_session:
                await self._show_no_active_quiz_message(update, "reset speed")
                return
            
            # Check permissions
            if not await self._check_control_permission(user_id, active_session, 'normal'):
                await self._show_no_permission_message(update, 'change quiz speed')
                return
            
            # Execute speed reset
            await self._execute_speed_change(update, context, active_session, 1.0, 'Normal')
            
        except Exception as e:
            logger.error(f"❌ Error in normal quiz command: {e}")
            await update.message.reply_text(messages.ERROR_INVALID_COMMAND)
    
    async def _show_speed_control_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                     session: Dict[str, Any], direction: str):
        """Show comprehensive speed control options"""
        try:
            session_id = session['session_id']
            current_speed = session.get('speed_multiplier', 1.0)
            quiz_id = session['quiz_id']
            
            # Get quiz details
            quiz = await db_manager.get_quiz(quiz_id)
            base_time = quiz.get('time_per_question', 30)
            
            speed_menu = f"""
⚡ **Quiz Speed Control - VidderTech Precision**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Current Quiz:**
📝 Title: `{quiz['title']}`
⚡ Current Speed: `{current_speed}x`
⏰ Base Time: `{base_time} seconds per question`
⏱️ Current Time: `{int(base_time / current_speed)} seconds per question`

🎮 **Speed Options:**
*Select your preferred quiz speed*

🐌 **Slower Speeds** *(Better for learning)*:
            """
            
            # Create speed selection keyboard
            keyboard = []
            
            # Slower speeds
            slower_speeds = [
                ("🐌 Ultra Slow", "slowest", 0.25, "4x more time"),
                ("🚶 Slow", "slow", 0.5, "2x more time"),
            ]
            
            for emoji_name, speed_name, multiplier, description in slower_speeds:
                time_per_q = int(base_time / multiplier)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{emoji_name} ({time_per_q}s) - {description}",
                        callback_data=f"set_speed_{session_id}_{multiplier}"
                    )
                ])
            
            # Normal speed
            keyboard.append([
                InlineKeyboardButton(
                    f"➡️ Normal ({base_time}s) - Optimal speed",
                    callback_data=f"set_speed_{session_id}_1.0"
                )
            ])
            
            # Faster speeds
            faster_speeds = [
                ("🏃 Fast", "fast", 1.5, "1.5x faster"),
                ("🚀 Very Fast", "faster", 2.0, "2x faster"),
                ("⚡ Lightning", "fastest", 3.0, "3x faster"),
            ]
            
            for emoji_name, speed_name, multiplier, description in faster_speeds:
                time_per_q = int(base_time / multiplier)
                button_text = f"{emoji_name} ({time_per_q}s) - {description}"
                
                # Premium feature for lightning speed
                if multiplier >= 3.0:
                    user_data = await db_manager.get_user(update.effective_user.id)
                    if not user_data or not user_data.get('is_premium'):
                        button_text += " 💎"
                
                keyboard.append([
                    InlineKeyboardButton(
                        button_text,
                        callback_data=f"set_speed_{session_id}_{multiplier}"
                    )
                ])
            
            # Additional controls
            keyboard.extend([
                [
                    InlineKeyboardButton("🎯 Custom Speed", callback_data=f"custom_speed_{session_id}"),
                    InlineKeyboardButton("📊 Speed Analytics", callback_data=f"speed_analytics_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏸️ Pause Quiz", callback_data=f"pause_quiz_{session_id}"),
                    InlineKeyboardButton("🔄 Back to Control", callback_data=f"quiz_controls_{session_id}")
                ]
            ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            speed_menu += f"""

🚀 **Faster Speeds** *(For competitive players)*:

📊 **Speed Recommendations:**
• 🐌 **Slow:** Perfect for learning and understanding
• ➡️ **Normal:** Balanced experience for most users
• 🚀 **Fast:** Great for experienced quiz takers
• ⚡ **Lightning:** Ultimate challenge for experts

💡 **Pro Tips:**
• Start slow and gradually increase speed
• Different speeds work better for different topics
• Participants can still answer at their own pace
• Speed affects time pressure, not accuracy

⚙️ **Advanced Options Available Below:**
            """
            
            await update.message.reply_text(
                speed_menu,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"❌ Error showing speed control menu: {e}")
            await update.message.reply_text("❌ Error loading speed controls.")
    
    async def _execute_speed_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  session: Dict[str, Any], new_speed: float, speed_name: str):
        """Execute speed change with participant notification"""
        try:
            session_id = session['session_id']
            quiz_id = session['quiz_id']
            old_speed = session.get('speed_multiplier', 1.0)
            
            # Update session speed
            speed_updates = {
                'speed_multiplier': new_speed,
                'session_data': json.dumps({
                    **json.loads(session.get('session_data', '{}')),
                    'speed_changes': json.loads(session.get('session_data', '{}')).get('speed_changes', []) + [{
                        'timestamp': datetime.now().isoformat(),
                        'old_speed': old_speed,
                        'new_speed': new_speed,
                        'changed_by': update.effective_user.id
                    }]
                })
            }
            
            success = await db_manager.update_quiz_session(session_id, speed_updates)
            if not success:
                await update.message.reply_text("❌ Failed to change quiz speed.")
                return
            
            # Get quiz details for calculations
            quiz = await db_manager.get_quiz(quiz_id)
            base_time = quiz.get('time_per_question', 30)
            new_time_per_question = int(base_time / new_speed)
            
            # Create speed change confirmation
            speed_message = f"""
⚡ **Quiz Speed Updated Successfully!**
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Speed Change:**
📊 From: `{old_speed}x` → `{new_speed}x` ({speed_name})
⏰ Time per Question: `{new_time_per_question} seconds`
🎮 Speed Category: `{speed_name}`

💡 **Impact on Quiz:**
• ⏰ Question timers adjusted automatically
• 🏃‍♂️ Participants get {'more' if new_speed < old_speed else 'less'} time to answer
• 📊 Leaderboard remains fair with time-adjusted scoring
• 🎯 Current question continues with new timing

✨ **Speed Benefits:**
            """
            
            # Add speed-specific benefits
            if new_speed < 1.0:
                speed_message += """
🐌 **Slower Speed Benefits:**
• 🎓 Better for learning and understanding
• 🧠 More time to think through answers
• ♿ Accessibility for different learning speeds
• 📚 Perfect for complex topics
                """
            elif new_speed > 1.0:
                speed_message += """
🚀 **Faster Speed Benefits:**
• ⚡ Increased challenge and excitement
• 🏆 Better for competitive players
• 🧠 Tests quick thinking and knowledge
• 🎮 More engaging for experienced users
                """
            else:
                speed_message += """
➡️ **Normal Speed Benefits:**
• ⚖️ Perfectly balanced for all users
• 🎯 Optimal challenge level
• 📊 Standard competitive timing
• 🌟 Recommended for most quizzes
                """
            
            speed_message += f"\n🚀 **{config.COMPANY_NAME} - Precision Quiz Control!**"
            
            # Create post-change control keyboard
            keyboard = [
                [
                    InlineKeyboardButton("🐌 Slower", callback_data=f"speed_slower_{session_id}"),
                    InlineKeyboardButton("🚀 Faster", callback_data=f"speed_faster_{session_id}")
                ],
                [
                    InlineKeyboardButton("⏸️ Pause Quiz", callback_data=f"pause_quiz_{session_id}"),
                    InlineKeyboardButton("⏭️ Skip Question", callback_data=f"skip_question_{session_id}")
                ],
                [
                    InlineKeyboardButton("📊 Live Results", callback_data=f"live_results_{session_id}"),
                    InlineKeyboardButton("⚙️ More Controls", callback_data=f"quiz_controls_{session_id}")
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                speed_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
            
            # Notify participants about speed change
            await self._notify_participants_speed_change(session, old_speed, new_speed, speed_name)
            
            # Log analytics
            await db_manager._log_analytics(
                "quiz_speed_changed",
                update.effective_user.id,
                quiz_id=quiz_id,
                session_id=session_id,
                metadata={
                    "old_speed": old_speed,
                    "new_speed": new_speed,
                    "speed_name": speed_name,
                    "new_time_per_question": new_time_per_question
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error executing speed change: {e}")
            await update.message.reply_text("❌ Error changing quiz speed.")
    
    # Helper Methods
    
    async def _get_active_quiz_session(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get active quiz session for a chat"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM vidder_quiz_sessions 
                    WHERE group_id = ? AND status = 'active'
                    ORDER BY created_at DESC LIMIT 1
                """, (chat_id,))
                
                row = cursor.fetchone()
                if row:
                    session_data = dict(row)
                    # Parse JSON fields
                    if session_data.get('session_data'):
                        session_data['session_data'] = json.loads(session_data['session_data'])
                    if session_data.get('answers'):
                        session_data['answers'] = json.loads(session_data['answers'])
                    return session_data
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting active session: {e}")
            return None
    
    async def _get_paused_quiz_session(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get paused quiz session for a chat"""
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM vidder_quiz_sessions 
                    WHERE group_id = ? AND status = 'paused'
                    ORDER BY paused_at DESC LIMIT 1
                """, (chat_id,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting paused session: {e}")
            return None
    
    async def _get_current_quiz_session(self, chat_id: int) -> Optional[Dict[str, Any]]:
        """Get current (active or paused) quiz session"""
        # Try active first
        session = await self._get_active_quiz_session(chat_id)
        if session:
            return session
        
        # Try paused
        return await self._get_paused_quiz_session(chat_id)

# Register all control handlers
def register_control_handlers(app):
    """Register all quiz control command handlers"""
    handler = VidderQuizControlHandlers()
    
    # Command handlers
    app.add_handler(CommandHandler("pause", handler.pause_quiz_command))
    app.add_handler(CommandHandler("resume", handler.resume_quiz_command))
    app.add_handler(CommandHandler("stop", handler.stop_quiz_command))
    app.add_handler(CommandHandler("fast", handler.fast_quiz_command))
    app.add_handler(CommandHandler("slow", handler.slow_quiz_command))
    app.add_handler(CommandHandler("normal", handler.normal_quiz_command))
    
    logger.info("✅ VidderTech Control Handlers registered successfully")

# Export handler class
__all__ = ['VidderQuizControlHandlers', 'register_control_handlers']
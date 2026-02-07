// Timer State
const TimerState = {
    IDLE: 'idle',
    RUNNING: 'running',
    PAUSED: 'paused'
};

const SessionType = {
    WORK: 'work',
    SHORT_BREAK: 'short_break',
    LONG_BREAK: 'long_break'
};

// Timer Configuration (in minutes)
const TIMER_CONFIG = {
    work: 25,
    shortBreak: 5,
    longBreak: 15,
    longBreakInterval: 4
};

// Timer Class
class PomodoroTimer {
    constructor() {
        // State
        this.state = TimerState.IDLE;
        this.currentSession = SessionType.WORK;
        this.timeRemaining = TIMER_CONFIG.work * 60; // in seconds
        this.totalTime = TIMER_CONFIG.work * 60;
        this.completedSessions = 0;
        this.currentCycle = 1;
        
        // Interval reference
        this.interval = null;
        
        // DOM Elements
        this.timerDisplay = document.getElementById('timer');
        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.resetBtn = document.getElementById('reset-btn');
        this.sessionLabel = document.getElementById('session-label');
        this.sessionCount = document.getElementById('session-count');
        this.totalTimeDisplay = document.getElementById('total-time');
        this.cycleCount = document.getElementById('cycle-count');
        this.progressBar = document.getElementById('progress-bar');
        this.notificationSound = document.getElementById('notification-sound');
        
        // Session indicators
        this.workIndicator = document.getElementById('work-indicator');
        this.shortBreakIndicator = document.getElementById('short-break-indicator');
        this.longBreakIndicator = document.getElementById('long-break-indicator');
        
        // Bind event listeners
        this.bindEvents();
        
        // Initialize display
        this.updateDisplay();
        this.updateSessionIndicators();
    }
    
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.start());
        this.pauseBtn.addEventListener('click', () => this.pause());
        this.resetBtn.addEventListener('click', () => this.reset());
    }
    
    start() {
        if (this.state === TimerState.RUNNING) return;
        
        this.state = TimerState.RUNNING;
        this.startBtn.style.display = 'none';
        this.pauseBtn.style.display = 'inline-block';
        
        this.interval = setInterval(() => {
            this.tick();
        }, 1000);
        
        this.updateSessionLabel();
    }
    
    pause() {
        if (this.state !== TimerState.RUNNING) return;
        
        this.state = TimerState.PAUSED;
        this.pauseBtn.style.display = 'none';
        this.startBtn.style.display = 'inline-block';
        
        clearInterval(this.interval);
        this.interval = null;
    }
    
    reset() {
        this.pause();
        
        // Reset to work session
        this.currentSession = SessionType.WORK;
        this.timeRemaining = TIMER_CONFIG.work * 60;
        this.totalTime = TIMER_CONFIG.work * 60;
        this.state = TimerState.IDLE;
        
        this.updateDisplay();
        this.updateSessionLabel();
        this.updateSessionIndicators();
        this.updateProgress();
        
        // Show start button
        this.startBtn.style.display = 'inline-block';
        this.pauseBtn.style.display = 'none';
    }
    
    tick() {
        this.timeRemaining--;
        
        if (this.timeRemaining <= 0) {
            this.completeSession();
        }
        
        this.updateDisplay();
        this.updateProgress();
    }
    
    completeSession() {
        // Stop timer
        this.pause();
        
        // Play notification sound
        this.playNotification();
        
        // Update session count if it was a work session
        if (this.currentSession === SessionType.WORK) {
            this.completedSessions++;
            this.sessionCount.textContent = this.completedSessions;
            this.updateTotalTime();
            
            // Save session to server if user is logged in
            this.saveSession();
        }
        
        // Determine next session type
        this.moveToNextSession();
    }
    
    moveToNextSession() {
        if (this.currentSession === SessionType.WORK) {
            // After work, decide break type
            if (this.completedSessions % TIMER_CONFIG.longBreakInterval === 0) {
                // Long break after every 4 pomodoros
                this.currentSession = SessionType.LONG_BREAK;
                this.timeRemaining = TIMER_CONFIG.longBreak * 60;
                this.totalTime = TIMER_CONFIG.longBreak * 60;
                this.currentCycle = 1; // Reset cycle
            } else {
                // Short break
                this.currentSession = SessionType.SHORT_BREAK;
                this.timeRemaining = TIMER_CONFIG.shortBreak * 60;
                this.totalTime = TIMER_CONFIG.shortBreak * 60;
                this.currentCycle++;
            }
        } else {
            // After break, go back to work
            this.currentSession = SessionType.WORK;
            this.timeRemaining = TIMER_CONFIG.work * 60;
            this.totalTime = TIMER_CONFIG.work * 60;
        }
        
        this.updateDisplay();
        this.updateSessionLabel();
        this.updateSessionIndicators();
        this.updateProgress();
        this.updateCycleDisplay();
        
        // Auto-start can be implemented here if needed
        // this.start();
    }
    
    updateDisplay() {
        const minutes = Math.floor(this.timeRemaining / 60);
        const seconds = this.timeRemaining % 60;
        
        this.timerDisplay.textContent = 
            `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }
    
    updateSessionLabel() {
        let label = '';
        
        if (this.state === TimerState.RUNNING) {
            switch (this.currentSession) {
                case SessionType.WORK:
                    label = 'Focus Time 🎯';
                    break;
                case SessionType.SHORT_BREAK:
                    label = 'Short Break ☕';
                    break;
                case SessionType.LONG_BREAK:
                    label = 'Long Break 🌟';
                    break;
            }
        } else if (this.state === TimerState.PAUSED) {
            label = 'Paused ⏸️';
        } else {
            label = 'Ready to focus';
        }
        
        this.sessionLabel.textContent = label;
    }
    
    updateSessionIndicators() {
        // Reset all
        this.workIndicator.classList.remove('active');
        this.shortBreakIndicator.classList.remove('active');
        this.longBreakIndicator.classList.remove('active');
        
        // Activate current
        switch (this.currentSession) {
            case SessionType.WORK:
                this.workIndicator.classList.add('active');
                break;
            case SessionType.SHORT_BREAK:
                this.shortBreakIndicator.classList.add('active');
                break;
            case SessionType.LONG_BREAK:
                this.longBreakIndicator.classList.add('active');
                break;
        }
    }
    
    updateProgress() {
        const percentage = ((this.totalTime - this.timeRemaining) / this.totalTime) * 100;
        this.progressBar.style.width = `${percentage}%`;
        this.progressBar.setAttribute('aria-valuenow', percentage);
    }
    
    updateTotalTime() {
        const totalMinutes = this.completedSessions * TIMER_CONFIG.work;
        const hours = Math.floor(totalMinutes / 60);
        const minutes = totalMinutes % 60;
        
        if (hours > 0) {
            this.totalTimeDisplay.textContent = `${hours}h ${minutes}m`;
        } else {
            this.totalTimeDisplay.textContent = `${minutes}m`;
        }
    }
    
    updateCycleDisplay() {
        const cyclePosition = this.currentCycle;
        this.cycleCount.textContent = `${cyclePosition}/4`;
    }
    
    playNotification() {
        try {
            this.notificationSound.play();
        } catch (error) {
            console.log('Could not play notification sound:', error);
        }
        
        // Browser notification
        if ('Notification' in window && Notification.permission === 'granted') {
            let message = '';
            
            if (this.currentSession === SessionType.WORK) {
                message = 'Great job! Time for a break.';
            } else {
                message = 'Break is over. Ready to focus?';
            }
            
            new Notification('Pomodoro Timer', {
                body: message,
                icon: '/static/images/logo.png'
            });
        }
    }
    
    saveSession() {
        // Only save if user is authenticated
        // This would make an AJAX call to your backend
        fetch('/api/session/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                duration: TIMER_CONFIG.work,
                session_type: SessionType.WORK,
                completed: true
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Session saved:', data);
        })
        .catch(error => {
            console.error('Error saving session:', error);
        });
    }
}

// Initialize timer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const timer = new PomodoroTimer();
    
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});
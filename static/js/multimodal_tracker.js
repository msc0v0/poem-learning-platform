/**
 * 多模态数据收集 SDK
 * 负责前端数据埋点、事件追踪和批量上报
 */

class MultimodalTracker {
    constructor(config = {}) {
        this.config = {
            batchSize: config.batchSize || 10,           // 批量上报大小
            flushInterval: config.flushInterval || 5000,  // 上报间隔(ms)
            endpoint: config.endpoint || '/api/tracking/multimodal',
            debug: config.debug || false
        };
        
        this.sessionId = this.generateSessionId();
        this.userId = null;
        this.poemId = null;
        this.eventQueue = [];
        this.sessionData = {
            startTime: new Date().toISOString(),
            deviceInfo: this.collectDeviceInfo(),
            textInteractions: [],
            videoEngagement: {},
            audioData: {},
            attentionTracking: {
                mouseMovements: [],
                clicks: [],
                scrolls: [],
                hoverAreas: {}
            },
            exerciseData: {},
            behaviorTrajectory: []
        };
        
        this.initTracking();
        this.startAutoFlush();
    }
    
    // 生成会话ID
    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
    
    // 收集设备信息
    collectDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            viewportWidth: window.innerWidth,
            viewportHeight: window.innerHeight,
            colorDepth: window.screen.colorDepth,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timestamp: new Date().toISOString()
        };
    }
    
    // 设置用户和诗歌ID
    setContext(userId, poemId) {
        this.userId = userId;
        this.poemId = poemId;
        this.log('Context set:', { userId, poemId });
    }
    
    // 初始化追踪
    initTracking() {
        this.trackMouseMovements();
        this.trackClicks();
        this.trackScrolls();
        this.trackPageVisibility();
        this.trackWindowFocus();
        this.log('Tracking initialized');
    }
    
    // 追踪鼠标移动（采样）
    trackMouseMovements() {
        let lastSample = 0;
        const sampleInterval = 500; // 每500ms采样一次
        
        document.addEventListener('mousemove', (e) => {
            const now = Date.now();
            if (now - lastSample > sampleInterval) {
                this.sessionData.attentionTracking.mouseMovements.push({
                    x: e.clientX,
                    y: e.clientY,
                    timestamp: now,
                    target: this.getElementIdentifier(e.target)
                });
                lastSample = now;
                
                // 限制数组大小
                if (this.sessionData.attentionTracking.mouseMovements.length > 200) {
                    this.sessionData.attentionTracking.mouseMovements.shift();
                }
            }
        });
    }
    
    // 追踪点击事件
    trackClicks() {
        document.addEventListener('click', (e) => {
            const clickData = {
                x: e.clientX,
                y: e.clientY,
                timestamp: Date.now(),
                target: this.getElementIdentifier(e.target),
                targetText: e.target.textContent?.substring(0, 50) || ''
            };
            
            this.sessionData.attentionTracking.clicks.push(clickData);
            this.addEvent('click', clickData);
        });
    }
    
    // 追踪滚动事件
    trackScrolls() {
        let scrollTimeout;
        document.addEventListener('scroll', (e) => {
            clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrollData = {
                    scrollY: window.scrollY,
                    scrollX: window.scrollX,
                    timestamp: Date.now(),
                    scrollHeight: document.documentElement.scrollHeight,
                    viewportHeight: window.innerHeight
                };
                
                this.sessionData.attentionTracking.scrolls.push(scrollData);
                this.addEvent('scroll', scrollData);
            }, 200);
        });
    }
    
    // 追踪页面可见性
    trackPageVisibility() {
        document.addEventListener('visibilitychange', () => {
            this.addEvent('visibility_change', {
                hidden: document.hidden,
                timestamp: Date.now()
            });
        });
    }
    
    // 追踪窗口焦点
    trackWindowFocus() {
        window.addEventListener('blur', () => {
            this.addEvent('window_blur', { timestamp: Date.now() });
        });
        
        window.addEventListener('focus', () => {
            this.addEvent('window_focus', { timestamp: Date.now() });
        });
    }
    
    // 获取元素标识符
    getElementIdentifier(element) {
        if (!element) return 'unknown';
        
        if (element.id) return `#${element.id}`;
        if (element.className) return `.${element.className.split(' ')[0]}`;
        return element.tagName.toLowerCase();
    }
    
    // 追踪视频观看
    trackVideoEngagement(videoElement, videoType = 'normal') {
        if (!videoElement) return;
        
        const videoData = {
            videoType: videoType,
            videoSrc: videoElement.src || videoElement.querySelector('source')?.src,
            totalDuration: 0,
            watchDuration: 0,
            completionRate: 0,
            playEvents: [],
            pauseEvents: [],
            seekEvents: [],
            replayCount: 0,
            startTime: null,
            endTime: null
        };
        
        let playStartTime = null;
        
        videoElement.addEventListener('loadedmetadata', () => {
            videoData.totalDuration = videoElement.duration;
        });
        
        videoElement.addEventListener('play', () => {
            playStartTime = Date.now();
            videoData.playEvents.push({
                timestamp: playStartTime,
                position: videoElement.currentTime
            });
            
            if (!videoData.startTime) {
                videoData.startTime = new Date().toISOString();
            }
            
            this.addEvent('video_play', {
                videoType,
                position: videoElement.currentTime,
                timestamp: playStartTime
            });
        });
        
        videoElement.addEventListener('pause', () => {
            if (playStartTime) {
                const watchTime = (Date.now() - playStartTime) / 1000;
                videoData.watchDuration += watchTime;
                playStartTime = null;
            }
            
            videoData.pauseEvents.push({
                timestamp: Date.now(),
                position: videoElement.currentTime
            });
            
            this.addEvent('video_pause', {
                videoType,
                position: videoElement.currentTime,
                watchDuration: videoData.watchDuration
            });
        });
        
        videoElement.addEventListener('seeked', () => {
            videoData.seekEvents.push({
                timestamp: Date.now(),
                position: videoElement.currentTime
            });
            
            this.addEvent('video_seek', {
                videoType,
                position: videoElement.currentTime
            });
        });
        
        videoElement.addEventListener('ended', () => {
            if (playStartTime) {
                const watchTime = (Date.now() - playStartTime) / 1000;
                videoData.watchDuration += watchTime;
                playStartTime = null;
            }
            
            videoData.endTime = new Date().toISOString();
            videoData.completionRate = videoData.totalDuration > 0 
                ? videoData.watchDuration / videoData.totalDuration 
                : 0;
            
            this.addEvent('video_ended', {
                videoType,
                watchDuration: videoData.watchDuration,
                completionRate: videoData.completionRate
            });
        });
        
        this.sessionData.videoEngagement[videoType] = videoData;
        this.log('Video tracking enabled:', videoType);
    }
    
    // 追踪音频播放
    trackAudioEngagement(audioElement, audioType = 'tts') {
        if (!audioElement) return;
        
        if (!this.sessionData.audioData[audioType]) {
            this.sessionData.audioData[audioType] = {
                playCount: 0,
                totalDuration: 0,
                playEvents: []
            };
        }
        
        audioElement.addEventListener('play', () => {
            this.sessionData.audioData[audioType].playCount++;
            this.sessionData.audioData[audioType].playEvents.push({
                timestamp: Date.now(),
                position: audioElement.currentTime
            });
            
            this.addEvent('audio_play', {
                audioType,
                position: audioElement.currentTime
            });
        });
        
        audioElement.addEventListener('ended', () => {
            this.sessionData.audioData[audioType].totalDuration += audioElement.duration;
            
            this.addEvent('audio_ended', {
                audioType,
                duration: audioElement.duration
            });
        });
        
        this.log('Audio tracking enabled:', audioType);
    }
    
    // 追踪AI问答
    trackAIQuestion(question, answer, responseTime, metadata = {}) {
        const interaction = {
            timestamp: new Date().toISOString(),
            question: question,
            answer: answer,
            responseTime: responseTime,
            questionType: metadata.questionType || 'general',
            userRating: metadata.userRating || null
        };
        
        this.sessionData.textInteractions.push(interaction);
        
        this.addEvent('ai_question', {
            questionLength: question.length,
            answerLength: answer.length,
            responseTime: responseTime,
            questionType: metadata.questionType
        });
        
        this.log('AI question tracked:', question.substring(0, 30));
    }
    
    // 追踪练习答题
    trackExercise(exerciseId, questionType, userAnswer, isCorrect, timeSpent) {
        if (!this.sessionData.exerciseData.answers) {
            this.sessionData.exerciseData.answers = [];
            this.sessionData.exerciseData.totalScore = 0;
            this.sessionData.exerciseData.completedCount = 0;
        }
        
        const exerciseRecord = {
            exerciseId,
            questionType,
            userAnswer,
            isCorrect,
            timeSpent,
            timestamp: new Date().toISOString()
        };
        
        this.sessionData.exerciseData.answers.push(exerciseRecord);
        this.sessionData.exerciseData.completedCount++;
        if (isCorrect) {
            this.sessionData.exerciseData.totalScore += 1;
        }
        
        this.addEvent('exercise_submit', exerciseRecord);
        this.log('Exercise tracked:', exerciseId);
    }
    
    // 追踪发音练习
    trackPronunciation(scores, recordingDuration, metadata = {}) {
        if (!this.sessionData.audioData.pronunciationPractice) {
            this.sessionData.audioData.pronunciationPractice = [];
        }
        
        const practiceRecord = {
            timestamp: new Date().toISOString(),
            recordingDuration: recordingDuration,
            overallScore: scores.overall || 0,
            accuracyScore: scores.accuracy || 0,
            fluencyScore: scores.fluency || 0,
            intonationScore: scores.intonation || 0,
            wordScores: scores.words || [],
            metadata: metadata
        };
        
        this.sessionData.audioData.pronunciationPractice.push(practiceRecord);
        
        this.addEvent('pronunciation_practice', {
            overallScore: scores.overall,
            duration: recordingDuration
        });
        
        this.log('Pronunciation tracked:', scores.overall);
    }
    
    // 追踪区域停留时间
    trackAreaHover(areaName, duration) {
        if (!this.sessionData.attentionTracking.hoverAreas[areaName]) {
            this.sessionData.attentionTracking.hoverAreas[areaName] = 0;
        }
        this.sessionData.attentionTracking.hoverAreas[areaName] += duration;
    }
    
    // 添加通用事件
    addEvent(eventType, eventData) {
        const event = {
            type: eventType,
            data: eventData,
            timestamp: Date.now()
        };
        
        this.sessionData.behaviorTrajectory.push(event);
        this.eventQueue.push(event);
        
        // 如果队列满了，立即上报
        if (this.eventQueue.length >= this.config.batchSize) {
            this.flush();
        }
    }
    
    // 自动定时上报
    startAutoFlush() {
        setInterval(() => {
            if (this.eventQueue.length > 0) {
                this.flush();
            }
        }, this.config.flushInterval);
        
        // 页面卸载时上报
        window.addEventListener('beforeunload', () => {
            this.endSession();
        });
    }
    
    // 上报数据
    async flush() {
        if (this.eventQueue.length === 0) return;
        
        const events = [...this.eventQueue];
        this.eventQueue = [];
        
        try {
            const response = await fetch(`${this.config.endpoint}/events`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken') || localStorage.getItem('token') || ''}`
                },
                body: JSON.stringify({
                    sessionId: this.sessionId,
                    userId: this.userId,
                    poemId: this.poemId,
                    events: events,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                this.log('Events flushed:', events.length);
            } else {
                this.log('Flush failed:', response.status);
                // 失败时重新加入队列
                this.eventQueue.unshift(...events);
            }
        } catch (error) {
            this.log('Flush error:', error);
            // 网络错误时重新加入队列
            this.eventQueue.unshift(...events);
        }
    }
    
    // 结束会话并上报完整数据
    endSession() {
        this.sessionData.endTime = new Date().toISOString();
        this.sessionData.durationSeconds = Math.floor(
            (new Date(this.sessionData.endTime) - new Date(this.sessionData.startTime)) / 1000
        );
        
        // 计算参与度指标
        this.sessionData.engagementMetrics = this.calculateEngagementMetrics();
        
        const payload = JSON.stringify({
            sessionId: this.sessionId,
            userId: this.userId,
            poemId: this.poemId,
            sessionData: this.sessionData,
            timestamp: new Date().toISOString()
        });
        
        // 使用 sendBeacon API，确保页面卸载时也能发送
        const token = localStorage.getItem('authToken') || localStorage.getItem('token') || '';
        const blob = new Blob([payload], { type: 'application/json' });
        
        // 创建带 Authorization 头的请求（sendBeacon 不支持自定义头，所以添加到 URL）
        const url = `${this.config.endpoint}/session?token=${encodeURIComponent(token)}`;
        
        if (navigator.sendBeacon) {
            const sent = navigator.sendBeacon(url, blob);
            this.log('Session ended and uploaded via sendBeacon:', this.sessionId, 'Success:', sent);
        } else {
            // 降级到同步 XMLHttpRequest
            try {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', `${this.config.endpoint}/session`, false); // 同步请求
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('Authorization', `Bearer ${token}`);
                xhr.send(payload);
                this.log('Session ended and uploaded via XHR:', this.sessionId);
            } catch (error) {
                this.log('Session upload error:', error);
            }
        }
    }
    
    // 计算参与度指标
    calculateEngagementMetrics() {
        const metrics = {
            totalInteractions: this.sessionData.behaviorTrajectory.length,
            videoCompletionRate: 0,
            aiInteractions: this.sessionData.textInteractions.length,
            exerciseAccuracy: 0,
            timeDistribution: this.sessionData.attentionTracking.hoverAreas
        };
        
        // 计算视频完成率
        const videoEngagements = Object.values(this.sessionData.videoEngagement);
        if (videoEngagements.length > 0) {
            metrics.videoCompletionRate = videoEngagements.reduce((sum, v) => 
                sum + (v.completionRate || 0), 0) / videoEngagements.length;
        }
        
        // 计算练习准确率
        if (this.sessionData.exerciseData.completedCount > 0) {
            metrics.exerciseAccuracy = this.sessionData.exerciseData.totalScore / 
                this.sessionData.exerciseData.completedCount;
        }
        
        return metrics;
    }
    
    // 日志输出
    log(...args) {
        if (this.config.debug) {
            console.log('[MultimodalTracker]', ...args);
        }
    }
    
    // 获取当前会话数据（用于调试）
    getSessionData() {
        return {
            sessionId: this.sessionId,
            userId: this.userId,
            poemId: this.poemId,
            sessionData: this.sessionData,
            queueLength: this.eventQueue.length
        };
    }
}

// 导出为全局变量
window.MultimodalTracker = MultimodalTracker;

/**
 * Advanced Analytics Tracker
 * Similar to Microsoft Clarity - tracks user behavior, heatmaps, and performance
 */

(function() {
    'use strict';
    
    // Generate unique IDs
    const generateId = () => Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
    
    // Get or create visitor ID (persists across sessions)
    const getVisitorId = () => {
        let visitorId = localStorage.getItem('visitor_id');
        if (!visitorId) {
            visitorId = generateId();
            localStorage.setItem('visitor_id', visitorId);
        }
        return visitorId;
    };
    
    // Get or create session ID (unique per session)
    const getSessionId = () => {
        let sessionId = sessionStorage.getItem('session_id');
        if (!sessionId) {
            sessionId = generateId();
            sessionStorage.setItem('session_id', sessionId);
        }
        return sessionId;
    };
    
    // Analytics Tracker Class
    class AnalyticsTracker {
        constructor(config = {}) {
            this.config = {
                endpoint: config.endpoint || '/api/analytics/track',
                batchSize: config.batchSize || 10,
                flushInterval: config.flushInterval || 5000, // 5 seconds
                trackClicks: config.trackClicks !== false,
                trackScroll: config.trackScroll !== false,
                trackMouse: config.trackMouse !== false,
                trackPerformance: config.trackPerformance !== false,
                ...config
            };
            
            this.visitorId = getVisitorId();
            this.sessionId = getSessionId();
            this.pageLoadTime = Date.now();
            this.eventQueue = [];
            this.scrollDepth = 0;
            this.maxScrollDepth = 0;
            this.clickCount = 0;
            this.lastClickTime = 0;
            this.lastClickPosition = null;
            this.rageClickThreshold = 3; // Number of clicks to consider rage click
            this.rageClickTimeout = 1000; // ms
            this.scrollEvents = [];
            
            this.init();
        }
        
        init() {
            // Track page view
            this.trackPageView();
            
            // Set up event listeners
            if (this.config.trackClicks) this.setupClickTracking();
            if (this.config.trackScroll) this.setupScrollTracking();
            if (this.config.trackMouse) this.setupMouseTracking();
            if (this.config.trackPerformance) this.trackPerformanceMetrics();
            
            // Track page leave
            window.addEventListener('beforeunload', () => this.handlePageLeave());
            
            // Start batch flush interval
            this.flushInterval = setInterval(() => this.flush(), this.config.flushInterval);
            
            // Track visibility changes
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.flush();
                }
            });
        }
        
        trackPageView() {
            const data = {
                type: 'pageview',
                session_id: this.sessionId,
                visitor_id: this.visitorId,
                page_url: window.location.pathname,
                page_title: document.title,
                referrer: document.referrer,
                timestamp: new Date().toISOString(),
                user_agent: navigator.userAgent,
                screen_resolution: `${screen.width}x${screen.height}`,
                viewport_size: `${window.innerWidth}x${window.innerHeight}`,
                device_type: this.getDeviceType(),
                browser: this.getBrowser(),
                os: this.getOS()
            };
            
            this.queueEvent(data);
            this.sendImmediately(data); // Send pageview immediately
        }
        
        setupClickTracking() {
            document.addEventListener('click', (e) => {
                const now = Date.now();
                const position = { x: e.clientX, y: e.clientY };
                
                // Detect rage clicks
                if (this.lastClickPosition && 
                    Math.abs(position.x - this.lastClickPosition.x) < 20 &&
                    Math.abs(position.y - this.lastClickPosition.y) < 20 &&
                    now - this.lastClickTime < this.rageClickTimeout) {
                    this.clickCount++;
                    
                    if (this.clickCount >= this.rageClickThreshold) {
                        this.trackRageClick(e, position);
                    }
                } else {
                    this.clickCount = 1;
                }
                
                this.lastClickTime = now;
                this.lastClickPosition = position;
                
                // Track regular click
                this.trackClick(e, position);
            }, true);
        }
        
        trackClick(e, position) {
            const element = e.target;
            const data = {
                type: 'click',
                session_id: this.sessionId,
                page_url: window.location.pathname,
                x_position: position.x,
                y_position: position.y,
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                element_tag: element.tagName.toLowerCase(),
                element_id: element.id || '',
                element_class: element.className || '',
                element_text: element.innerText?.substring(0, 200) || '',
                timestamp: new Date().toISOString(),
                device_type: this.getDeviceType()
            };
            
            this.queueEvent(data);
        }
        
        trackRageClick(e, position) {
            const element = e.target;
            const data = {
                type: 'rage_click',
                session_id: this.sessionId,
                page_url: window.location.pathname,
                x_position: position.x,
                y_position: position.y,
                click_count: this.clickCount,
                element_selector: this.getElementSelector(element),
                timestamp: new Date().toISOString()
            };
            
            this.queueEvent(data);
            this.sendImmediately(data); // Send rage clicks immediately
        }
        
        setupScrollTracking() {
            let scrollTimeout;
            window.addEventListener('scroll', () => {
                clearTimeout(scrollTimeout);
                scrollTimeout = setTimeout(() => {
                    const scrollDepth = this.calculateScrollDepth();
                    this.scrollDepth = scrollDepth;
                    
                    if (scrollDepth > this.maxScrollDepth) {
                        this.maxScrollDepth = scrollDepth;
                        
                        const data = {
                            type: 'scroll',
                            session_id: this.sessionId,
                            page_url: window.location.pathname,
                            scroll_depth: scrollDepth,
                            timestamp: new Date().toISOString()
                        };
                        
                        this.scrollEvents.push({
                            depth: scrollDepth,
                            timestamp: new Date().toISOString()
                        });
                        
                        this.queueEvent(data);
                    }
                }, 150);
            });
        }
        
        calculateScrollDepth() {
            const windowHeight = window.innerHeight;
            const documentHeight = document.documentElement.scrollHeight;
            const scrollTop = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
            const trackLength = documentHeight - windowHeight;
            const percentage = Math.floor((scrollTop / trackLength) * 100);
            return Math.min(100, Math.max(0, percentage));
        }
        
        setupMouseTracking() {
            // Track dead clicks (clicks on non-interactive elements)
            document.addEventListener('click', (e) => {
                const element = e.target;
                const isInteractive = element.tagName.match(/A|BUTTON|INPUT|SELECT|TEXTAREA/) ||
                                     element.onclick || 
                                     element.hasAttribute('onclick') ||
                                     window.getComputedStyle(element).cursor === 'pointer';
                
                if (!isInteractive) {
                    const data = {
                        type: 'dead_click',
                        session_id: this.sessionId,
                        page_url: window.location.pathname,
                        x_position: e.clientX,
                        y_position: e.clientY,
                        element_selector: this.getElementSelector(element),
                        timestamp: new Date().toISOString()
                    };
                    
                    this.queueEvent(data);
                }
            }, true);
        }
        
        trackPerformanceMetrics() {
            // Wait for page to fully load
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = this.getPerformanceData();
                    if (perfData) {
                        const data = {
                            type: 'performance',
                            session_id: this.sessionId,
                            page_url: window.location.pathname,
                            ...perfData,
                            timestamp: new Date().toISOString()
                        };
                        
                        this.queueEvent(data);
                        this.sendImmediately(data);
                    }
                }, 100);
            });
        }
        
        getPerformanceData() {
            if (!window.performance || !window.performance.timing) return null;
            
            const timing = performance.timing;
            const navigation = performance.navigation;
            
            const data = {
                dom_load_time: timing.domContentLoadedEventEnd - timing.domContentLoadedEventStart,
                page_load_time: timing.loadEventEnd - timing.navigationStart,
                resource_load_time: timing.loadEventEnd - timing.responseEnd,
                connection_type: navigator.connection?.effectiveType || 'unknown',
                effective_bandwidth: navigator.connection?.downlink || null
            };
            
            // Try to get Web Vitals if available
            if (window.PerformanceObserver) {
                try {
                    // FCP
                    const paintEntries = performance.getEntriesByType('paint');
                    const fcpEntry = paintEntries.find(entry => entry.name === 'first-contentful-paint');
                    if (fcpEntry) data.first_contentful_paint = fcpEntry.startTime;
                    
                    // LCP
                    const lcpObserver = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        const lastEntry = entries[entries.length - 1];
                        data.largest_contentful_paint = lastEntry.renderTime || lastEntry.loadTime;
                    });
                    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
                    
                    // FID
                    const fidObserver = new PerformanceObserver((list) => {
                        const entries = list.getEntries();
                        entries.forEach((entry) => {
                            data.first_input_delay = entry.processingStart - entry.startTime;
                        });
                    });
                    fidObserver.observe({ entryTypes: ['first-input'] });
                    
                    // CLS
                    let cls = 0;
                    const clsObserver = new PerformanceObserver((list) => {
                        for (const entry of list.getEntries()) {
                            if (!entry.hadRecentInput) {
                                cls += entry.value;
                            }
                        }
                        data.cumulative_layout_shift = cls;
                    });
                    clsObserver.observe({ entryTypes: ['layout-shift'] });
                    
                } catch (e) {
                    console.warn('Web Vitals observation failed:', e);
                }
            }
            
            return data;
        }
        
        handlePageLeave() {
            const timeOnPage = (Date.now() - this.pageLoadTime) / 1000;
            
            const data = {
                type: 'page_leave',
                session_id: this.sessionId,
                visitor_id: this.visitorId,
                page_url: window.location.pathname,
                time_on_page: timeOnPage,
                scroll_depth: this.maxScrollDepth,
                scroll_events: this.scrollEvents,
                click_count: this.clickCount,
                timestamp: new Date().toISOString()
            };
            
            // Use sendBeacon for reliable delivery on page unload
            this.sendBeacon(data);
        }
        
        queueEvent(data) {
            this.eventQueue.push(data);
            
            if (this.eventQueue.length >= this.config.batchSize) {
                this.flush();
            }
        }
        
        flush() {
            if (this.eventQueue.length === 0) return;
            
            const events = [...this.eventQueue];
            this.eventQueue = [];
            
            this.send(events);
        }
        
        send(events) {
            fetch(this.config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ events }),
                keepalive: true
            }).catch(err => {
                console.warn('Analytics tracking failed:', err);
                // Re-queue failed events
                this.eventQueue.unshift(...events);
            });
        }
        
        sendImmediately(data) {
            fetch(this.config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({ events: [data] }),
                keepalive: true
            }).catch(err => {
                console.warn('Analytics tracking failed:', err);
            });
        }
        
        sendBeacon(data) {
            const blob = new Blob([JSON.stringify({ events: [data] })], { type: 'application/json' });
            navigator.sendBeacon(this.config.endpoint, blob);
        }
        
        getCSRFToken() {
            const name = 'csrftoken';
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        
        getDeviceType() {
            const ua = navigator.userAgent;
            if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
                return 'tablet';
            }
            if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
                return 'mobile';
            }
            return 'desktop';
        }
        
        getBrowser() {
            const ua = navigator.userAgent;
            if (ua.includes('Firefox')) return 'Firefox';
            if (ua.includes('Chrome')) return 'Chrome';
            if (ua.includes('Safari')) return 'Safari';
            if (ua.includes('Edge')) return 'Edge';
            if (ua.includes('Opera') || ua.includes('OPR')) return 'Opera';
            return 'Unknown';
        }
        
        getOS() {
            const ua = navigator.userAgent;
            if (ua.includes('Win')) return 'Windows';
            if (ua.includes('Mac')) return 'MacOS';
            if (ua.includes('Linux')) return 'Linux';
            if (ua.includes('Android')) return 'Android';
            if (ua.includes('iOS')) return 'iOS';
            return 'Unknown';
        }
        
        getElementSelector(element) {
            if (element.id) return `#${element.id}`;
            if (element.className) return `.${element.className.split(' ')[0]}`;
            return element.tagName.toLowerCase();
        }
        
        destroy() {
            if (this.flushInterval) {
                clearInterval(this.flushInterval);
            }
            this.flush();
        }
    }
    
    // Initialize tracker automatically
    window.AnalyticsTracker = AnalyticsTracker;
    
    // Auto-initialize if URL monitoring is detected
    if (document.querySelector('[data-url-monitor]')) {
        window.analyticsTracker = new AnalyticsTracker({
            endpoint: '/api/analytics/track'
        });
    }
})();

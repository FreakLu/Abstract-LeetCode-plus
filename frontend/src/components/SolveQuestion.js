import React, { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { solveQuestion, downloadExcel } from "../services/api";
import "./SolveQuestion.css";

const SolveQuestion = () => {
    const [question, setQuestion] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [history, setHistory] = useState([]);
    const [activeId, setActiveId] = useState(null);
    
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const [placeholderText, setPlaceholderText] = useState("");
    const [isDeleting, setIsDeleting] = useState(false);
    const [loopNum, setLoopNum] = useState(0);

    const [isFocused, setIsFocused] = useState(false);

    useEffect(() => {
        if (isFocused || activeId || isSidebarOpen) {
            setPlaceholderText("");
            return;
        }

        const examples = [
            "Leetcode 20: Valid Parentheses",
            "Leetcode 20:",
            "20"
        ];
        
        const currentExample = examples[loopNum % examples.length];
        const isFull = placeholderText === currentExample;
        const isEmpty = placeholderText === "";

        let typingSpeed = isDeleting ? 40 : 200; 

        if (!isDeleting && isFull) {
            typingSpeed = 3000; 
            setIsDeleting(true);
        } else if (isDeleting && isEmpty) {
            setIsDeleting(false);
            setLoopNum(prev => prev + 1); 
            typingSpeed = 500; 
        }

        const timeout = setTimeout(() => {
            setPlaceholderText(
                currentExample.substring(0, placeholderText.length + (isDeleting ? -1 : 1))
            );
        }, typingSpeed);

        return () => clearTimeout(timeout); 
    }, [placeholderText, isDeleting, loopNum, activeId, isSidebarOpen, isFocused]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const currentQuestion = question.trim(); 
        if (!currentQuestion) return;

        const match = currentQuestion.match(/\d+/); 
        const displayTitle = match ? `Leetcode ${match[0]}` : currentQuestion; 

        setLoading(true);
        setError("");
        setQuestion(""); 

        // 1. 查重逻辑：寻找是否已经搜过这个相同的词（忽略大小写）
        const existingRecord = history.find(item => item.title.toLowerCase() === currentQuestion.toLowerCase());
        let targetId;

        if (existingRecord) {
            targetId = existingRecord.id;
            // 如果存在，将它标记为加载中，清空旧内容，并把它“提取”到数组最顶部
            setHistory(prev => {
                const filtered = prev.filter(item => item.id !== targetId);
                return [{ ...existingRecord, isLoading: true, content: "" }, ...filtered];
            });
        } else {
            // 如果不存在，走原来的新建逻辑
            targetId = Date.now().toString();
            const tempRecord = {
                id: targetId,
                title: displayTitle,
                content: "", 
                isLoading: true 
            };
            setHistory(prev => [tempRecord, ...prev]);
        }

        // 2. 强行切入目标记录，触发 UI 裂变
        setActiveId(targetId);
        setIsSidebarOpen(true);

        // 3. 开始网络请求
        const result = await solveQuestion(currentQuestion, (streamedText) => {
            // 每收到几个字，就立刻更新到屏幕上
            setHistory(prev => prev.map(item => 
                item.id === targetId 
                    ? { ...item, content: streamedText, isLoading: false }
                    : item
            ));
        });

        if (result.error) {
            setError(result.error);
            // 报错时：如果是新建的，直接删掉；如果是原有的，恢复它的旧状态（这里为简便，我们统一剔除当前加载中的占位）
            setHistory(prev => prev.filter(item => item.id !== targetId));
            if (activeId === targetId) setActiveId(null);
        } else {
            // 4. 请求成功！填入数据，关闭加载状态
            setHistory(prev => prev.map(item => 
                item.id === targetId 
                    ? { ...item, content: result.response, isLoading: false }
                    : item
            ));
        }

        setLoading(false);
    };

    // 4. 替换 return 里面的所有内容
    return (
        <div className={`app-wrapper ${activeId ? 'ide-mode' : 'center-mode'}`}>
            
            {/* 侧边栏：只有在 ide-mode 才显示 */}
            {isSidebarOpen && (
                <aside className="sidebar">
                    {/* 标题变为返回主页的按钮 */}
                    <h2 className="sidebar-title" onClick={() => setActiveId(null)}>
                        Abstract LeetCode Plus +
                    </h2>
                    <div className="history-list">
                        {history.map(item => (
                            <div 
                                key={item.id} 
                                className={`history-item ${item.id === activeId ? 'active' : ''}`}
                                onClick={() => {
                                    setActiveId(item.id);
                                }}
                            >
                                {item.title}
                            </div>
                        ))}
                    </div>
                </aside>
            )}

            {/* 右侧/中间主内容区 */}
            <main className="main-content">
    
                {/* 只有在 center-mode 才显示大标题 */}
                
                {!activeId && (
                <h2 className={`main-title ${isSidebarOpen ? 'hidden' : ''}`}>
                    Abstract LeetCode Plus +
                </h2>
                )}

                {/* 答案显示区 */}
                {activeId && (
                    <div className="response-container">
                        {/* 根据当前记录的 isLoading 状态决定渲染什么 */}
                        {history.find(item => item.id === activeId)?.isLoading ? (
                            <div className="loading-cursor-container">
                                <div className="loading-cursor"></div>
                                <span>thinking...</span>
                            </div>
                        ) : (
                            <div className="response-text">
                                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                    {history.find(item => item.id === activeId)?.content || ""}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>
                )}

                {/* 只有在主页才显示的虚拟解析区 */}
                {!activeId && (
                    <div className="virtual-response-preview">
                        <div className="fake-line" style={{ width: '80%' }}></div>
                        <div className="fake-line" style={{ width: '100%' }}></div>
                        <div className="fake-line" style={{ width: '60%' }}></div>
                    </div>
                )}

                {/* 底部输入区 */}
                <form onSubmit={handleSubmit} className="question-form">
                    <div className="input-container">
                        <button 
                        type="button" 
                        className={`sidebar-toggle-btn ${isSidebarOpen ? 'open' : ''}`} 
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        title="Toggle Sidebar"
                        >
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                        </button>
                        <div className="input-container">
                            <input
                                type="text"
                                placeholder={isFocused ? "" : placeholderText}
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                onFocus={() => {
                                    setIsFocused(true);
                                    setPlaceholderText("");
                                }}
                                onBlur={() => {
                                    setIsFocused(false);
                                    setLoopNum(0);
                                }}
                                required
                                className="question-input"
                                disabled={loading}
                            />
                        </div>
                        <button type="submit" disabled={loading} className="submit-button">
                            {loading ? "Solving..." : "Solve"}
                        </button>
                        <button type="button" className="download-button" onClick={downloadExcel} disabled={loading}>
                            {loading ? "Preparing..." : "Download Excel"}
                        </button>
                    </div>
                    {error && <p className="error">{error}</p>}
                </form>
            </main>
        </div>
    );
};

export default SolveQuestion;

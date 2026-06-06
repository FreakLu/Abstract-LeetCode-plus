import React, { useEffect, useState } from "react";
import { downloadExcel, solveQuestion } from "../services/api";
import AnswerView from "./AnswerView";
import QuestionBar from "./QuestionBar";
import ReviewGallery from "./ReviewGallery";
import "./StudyWorkspace.css";

const detectLanguage = () => {
    const savedLanguage = window.localStorage.getItem("abstractLanguage");
    if (savedLanguage === "zh" || savedLanguage === "en") return savedLanguage;

    const browserLanguage = navigator.language || navigator.userLanguage || "";
    return browserLanguage.toLowerCase().startsWith("zh") ? "zh" : "en";
};

const UI_TEXT = {
    zh: {
        thinking: "思考中...",
        solving: "解析中...",
        solve: "解析",
        preparing: "准备中...",
        download: "下载 Excel",
        review: "复习卡片",
        toggleSidebar: "切换侧边栏",
        languageLabel: "语言",
        chinese: "中文",
        english: "EN",
    },
    en: {
        thinking: "Thinking...",
        solving: "Solving...",
        solve: "Solve",
        preparing: "Preparing...",
        download: "Download Excel",
        review: "Review Cards",
        toggleSidebar: "Toggle Sidebar",
        languageLabel: "Language",
        chinese: "中文",
        english: "EN",
    },
};

const StudyWorkspace = () => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [language, setLanguage] = useState(detectLanguage);
    const [history, setHistory] = useState([]);
    const [activeId, setActiveId] = useState(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [isReviewOpen, setIsReviewOpen] = useState(false);

    const activeRecord = history.find((item) => item.id === activeId);
    const isAnswerView = Boolean(activeRecord);
    const text = UI_TEXT[language];

    useEffect(() => {
        window.localStorage.setItem("abstractLanguage", language);
        document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    }, [language]);

    const handleSubmit = async (currentQuestion) => {
        const match = currentQuestion.match(/\d+/);
        const displayTitle = match ? `Leetcode ${match[0]}` : currentQuestion;
        const existingRecord = history.find(
            (item) => item.title.toLowerCase() === displayTitle.toLowerCase()
        );
        const targetId = existingRecord?.id || Date.now().toString();

        setLoading(true);
        setError("");
        setIsReviewOpen(false);
        setActiveId(targetId);
        setIsSidebarOpen(true);

        if (existingRecord) {
            setHistory((previous) => [
                { ...existingRecord, isLoading: true, content: "" },
                ...previous.filter((item) => item.id !== targetId),
            ]);
        } else {
            setHistory((previous) => [
                { id: targetId, title: displayTitle, content: "", isLoading: true },
                ...previous,
            ]);
        }

        const result = await solveQuestion(currentQuestion, language, (streamedText) => {
            setHistory((previous) => previous.map((item) => (
                item.id === targetId
                    ? { ...item, content: streamedText, isLoading: false }
                    : item
            )));
        });

        if (result.error) {
            setError(result.error);
            setHistory((previous) => previous.filter((item) => item.id !== targetId));
            setActiveId((currentId) => currentId === targetId ? null : currentId);
        } else {
            setHistory((previous) => previous.map((item) => (
                item.id === targetId
                    ? { ...item, content: result.response, isLoading: false }
                    : item
            )));
        }

        setLoading(false);
    };

    const handleToggleReview = () => {
        setIsReviewOpen((isOpen) => {
            if (!isOpen) {
                setActiveId(null);
                setIsSidebarOpen(false);
            }
            return !isOpen;
        });
    };

    const modeClass = isReviewOpen
        ? "review-mode"
        : isAnswerView
            ? "ide-mode"
            : "center-mode";

    return (
        <div className={`app-wrapper ${modeClass}`}>
            {!isReviewOpen && (
                <div className="top-actions" aria-label={text.languageLabel}>
                    <div className="language-switch" role="group" aria-label={text.languageLabel}>
                        <button
                            type="button"
                            className={language === "zh" ? "active" : ""}
                            onClick={() => setLanguage("zh")}
                            disabled={loading}
                        >
                            {text.chinese}
                        </button>
                        <button
                            type="button"
                            className={language === "en" ? "active" : ""}
                            onClick={() => setLanguage("en")}
                            disabled={loading}
                        >
                            {text.english}
                        </button>
                    </div>
                </div>
            )}

            {isSidebarOpen && !isReviewOpen && (
                <aside className="sidebar">
                    {isAnswerView && (
                        <h2 className="sidebar-title" onClick={() => setActiveId(null)}>
                            Abstract LeetCode Plus +
                        </h2>
                    )}
                    <div className="history-list">
                        {history.map((item) => (
                            <div
                                key={item.id}
                                className={`history-item ${item.id === activeId ? "active" : ""}`}
                                onClick={() => setActiveId(item.id)}
                            >
                                {item.title}
                            </div>
                        ))}
                    </div>
                </aside>
            )}

            <main className="main-content">
                {!isAnswerView && !isReviewOpen && (
                    <h2 className="main-title">Abstract LeetCode Plus +</h2>
                )}

                {isAnswerView && !isReviewOpen && (
                    <AnswerView
                        content={activeRecord.content}
                        isLoading={activeRecord.isLoading}
                        thinkingText={text.thinking}
                    />
                )}

                {!isAnswerView && !isReviewOpen && (
                    <div className="virtual-response-preview">
                        <div className="fake-line" style={{ width: "80%" }}></div>
                        <div className="fake-line" style={{ width: "100%" }}></div>
                        <div className="fake-line" style={{ width: "60%" }}></div>
                    </div>
                )}

                {isReviewOpen && (
                    <ReviewGallery onClose={() => setIsReviewOpen(false)} />
                )}

                {!isReviewOpen && (
                    <QuestionBar
                        language={language}
                        loading={loading}
                        isAnswerView={isAnswerView}
                        isSidebarOpen={isSidebarOpen}
                        isReviewOpen={isReviewOpen}
                        text={text}
                        error={error}
                        onSubmit={handleSubmit}
                        onToggleSidebar={() => setIsSidebarOpen((isOpen) => !isOpen)}
                        onDownload={downloadExcel}
                        onToggleReview={handleToggleReview}
                    />
                )}
            </main>
        </div>
    );
};

export default StudyWorkspace;

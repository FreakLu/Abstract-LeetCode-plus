import React, { useEffect, useState } from "react";

const PLACEHOLDER_EXAMPLES = {
    zh: ["帮我讲一下 Leetcode 20 题", "帮我讲一下 30 题", "第 20 题", "20"],
    en: ["Explain Leetcode 20", "Leetcode 20: Valid Parentheses", "Problem 30", "20"],
};

const QuestionBar = ({
    language,
    loading,
    isAnswerView,
    isSidebarOpen,
    isReviewOpen,
    text,
    error,
    onSubmit,
    onToggleSidebar,
    onToggleReview,
}) => {
    const [question, setQuestion] = useState("");
    const [placeholderText, setPlaceholderText] = useState("");
    const [isDeleting, setIsDeleting] = useState(false);
    const [loopNum, setLoopNum] = useState(0);
    const [isFocused, setIsFocused] = useState(false);

    useEffect(() => {
        if (isFocused || isAnswerView || isReviewOpen) {
            setPlaceholderText("");
            return;
        }

        const examples = PLACEHOLDER_EXAMPLES[language];
        const currentExample = examples[loopNum % examples.length];
        const isFull = placeholderText === currentExample;
        const isEmpty = placeholderText === "";
        let typingSpeed = isDeleting ? 40 : 200;

        if (!isDeleting && isFull) {
            const timeout = setTimeout(() => setIsDeleting(true), 2400);
            return () => clearTimeout(timeout);
        }

        if (isDeleting && isEmpty) {
            setIsDeleting(false);
            setLoopNum((previous) => previous + 1);
            typingSpeed = 500;
        }

        const timeout = setTimeout(() => {
            setPlaceholderText(
                currentExample.substring(0, placeholderText.length + (isDeleting ? -1 : 1))
            );
        }, typingSpeed);

        return () => clearTimeout(timeout);
    }, [placeholderText, isDeleting, loopNum, isAnswerView, isFocused, isReviewOpen, language]);

    const handleSubmit = (event) => {
        event.preventDefault();
        const currentQuestion = question.trim();
        if (!currentQuestion) return;

        setQuestion("");
        onSubmit(currentQuestion);
    };

    return (
        <form onSubmit={handleSubmit} className="question-form">
            <div className="input-container">
                <button
                    type="button"
                    className={`sidebar-toggle-btn ${isSidebarOpen ? "open" : ""}`}
                    onClick={onToggleSidebar}
                    title={text.toggleSidebar}
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                </button>

                <div className="input-field-wrapper">
                    {!question && !isFocused && !loading && (
                        <div className="animated-placeholder" aria-hidden="true">
                            <span>{placeholderText}</span>
                            <span className="placeholder-cursor"></span>
                        </div>
                    )}
                    <input
                        type="text"
                        value={question}
                        onChange={(event) => setQuestion(event.target.value)}
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
                    {loading ? text.solving : text.solve}
                </button>
                <button
                    type="button"
                    className={`review-button ${isReviewOpen ? "active" : ""}`}
                    onClick={onToggleReview}
                    disabled={loading}
                >
                    {text.review}
                </button>
            </div>
            {error && <p className="error">{error}</p>}
        </form>
    );
};

export default QuestionBar;

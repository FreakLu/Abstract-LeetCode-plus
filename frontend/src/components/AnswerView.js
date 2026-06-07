import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const cleanDisplayBreaks = (text, replacement = " ") => (
    text.replace(/<br\s*\/?>/gi, replacement)
);

const formatTableCellBreaks = (text) => (
    cleanDisplayBreaks(text, "\u2028")
        .replace(/(\*\*[^*]+:\*\*)/g, "\u2028$1")
        .replace(/\s+(\d+\.\s+)/g, "\u2028$1")
        .replace(/\u2028+/g, "\u2028")
        .trim()
);

const cleanDisplayTags = (text) => {
    const trimmed = text.trim();
    const unwrapped = trimmed.startsWith("{") && trimmed.endsWith("}")
        ? trimmed.slice(1, -1).trim()
        : trimmed;

    return unwrapped
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean)
        .join("\u2028");
};

const formatScenarioCell = (text) => (
    formatTableCellBreaks(text)
        .replace(/(?:^|\s+)(\d+\.\s+)/g, "\u2028$1")
        .replace(/\u2028+/g, "\u2028")
        .trim()
);

const formatDisplayMarkdown = (markdown = "") => (
    markdown.split("\n").map((line) => {
        if (!line.trim().startsWith("|")) {
            return cleanDisplayBreaks(line, "\n");
        }

        const parts = line.split("|");
        if (parts.length < 8) {
            return cleanDisplayBreaks(line, " ");
        }

        const cells = parts.slice(1, -1).map((cell) => formatTableCellBreaks(cell));
        if (cells.length >= 6) {
            cells[3] = cleanDisplayTags(cells[3]);
            cells[5] = formatScenarioCell(cells[5]);
        }

        return `|${cells.join("|")}|`;
    }).join("\n")
);

const AnswerView = ({ content, isLoading, thinkingText }) => (
    <div className="response-container">
        {isLoading ? (
            <div className="loading-cursor-container">
                <div className="loading-cursor"></div>
                <span>{thinkingText}</span>
            </div>
        ) : (
            <div className="response-text">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {formatDisplayMarkdown(content)}
                </ReactMarkdown>
            </div>
        )}
    </div>
);

export default AnswerView;

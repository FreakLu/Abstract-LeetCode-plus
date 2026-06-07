import React, { useEffect, useRef, useState } from "react";
import { pinyin } from "pinyin-pro";
import { getReviewItems, updateReviewMastery } from "../services/api";
import "./ReviewGallery.css";

const normalizeSearchText = (text = "") => (
    String(text)
        .toLowerCase()
        .replace(/[\s_-]+/g, "")
);

const getTagSearchForms = (tag) => ([
    normalizeSearchText(tag),
    normalizeSearchText(pinyin(tag, { toneType: "none" })),
    normalizeSearchText(pinyin(tag, { pattern: "first", toneType: "none" })),
]);

const ReviewGallery = ({ onClose, onDownload }) => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedItem, setSelectedItem] = useState(null);
    const [detailTab, setDetailTab] = useState("solution");
    const [detailRect, setDetailRect] = useState(null);
    const [detailPhase, setDetailPhase] = useState("closed");
    const [revealedSections, setRevealedSections] = useState({
        solution: false,
        useCases: false,
    });
    const [masteryPromptActive, setMasteryPromptActive] = useState(false);
    const [masterySaving, setMasterySaving] = useState(false);
    const [masteryError, setMasteryError] = useState("");
    const [tagQuery, setTagQuery] = useState("");
    const [isTagSearchFocused, setIsTagSearchFocused] = useState(false);
    const [sortMode, setSortMode] = useState("number-asc");
    const closeTimerRef = useRef(null);
    const promptTimerRef = useRef(null);

    useEffect(() => {
        const loadReviewItems = async () => {
            try {
                setItems(await getReviewItems());
            } catch (requestError) {
                setError(requestError.message);
            } finally {
                setLoading(false);
            }
        };

        loadReviewItems();

        return () => {
            window.clearTimeout(closeTimerRef.current);
            window.clearTimeout(promptTimerRef.current);
        };
    }, []);

    const getDetailRect = () => {
        const pagePadding = window.innerWidth <= 720 ? 16 : 40;
        const width = Math.min(860, window.innerWidth - pagePadding * 2);
        const height = Math.min(720, window.innerHeight * 0.9);

        return {
            top: (window.innerHeight - height) / 2,
            left: (window.innerWidth - width) / 2,
            width,
            height,
        };
    };

    const openDetail = (item, event) => {
        const originRect = event.currentTarget.getBoundingClientRect();

        setSelectedItem(item);
        setDetailTab("solution");
        setRevealedSections({ solution: false, useCases: false });
        setMasteryPromptActive(false);
        setMasteryError("");
        setDetailRect({
            top: originRect.top,
            left: originRect.left,
            width: originRect.width,
            height: originRect.height,
        });
        setDetailPhase("opening");

        window.requestAnimationFrame(() => {
            window.requestAnimationFrame(() => {
                setDetailRect(getDetailRect());
                setDetailPhase("open");
            });
        });
    };

    const closeDetail = () => {
        const originCard = document.querySelector(
            `[data-review-number="${selectedItem.problem_number}"]`
        );
        const originRect = originCard?.getBoundingClientRect();

        if (!originRect) {
            setSelectedItem(null);
            setDetailPhase("closed");
            return;
        }

        setDetailPhase("closing");
        setDetailRect({
            top: originRect.top,
            left: originRect.left,
            width: originRect.width,
            height: originRect.height,
        });

        closeTimerRef.current = window.setTimeout(() => {
            setSelectedItem(null);
            setDetailRect(null);
            setDetailPhase("closed");
        }, 340);
    };

    const requestCloseDetail = () => {
        const hasRevealedContent = (
            revealedSections.solution || revealedSections.useCases
        );

        if (!hasRevealedContent) {
            closeDetail();
            return;
        }

        setMasteryPromptActive(false);
        window.clearTimeout(promptTimerRef.current);

        window.requestAnimationFrame(() => {
            setMasteryPromptActive(true);
            promptTimerRef.current = window.setTimeout(() => {
                setMasteryPromptActive(false);
            }, 650);
        });
    };

    const saveMasteryLevel = async (masteryLevel) => {
        setMasterySaving(true);
        setMasteryError("");

        try {
            const updatedItem = await updateReviewMastery(
                selectedItem.problem_number,
                masteryLevel
            );
            setItems((currentItems) => currentItems.map((item) => (
                item.problem_number === updatedItem.problem_number ? updatedItem : item
            )));
            setSelectedItem(updatedItem);
            closeDetail();
        } catch (requestError) {
            setMasteryError(requestError.message);
        } finally {
            setMasterySaving(false);
        }
    };

    const normalizedTagQuery = normalizeSearchText(tagQuery);
    const availableTags = [...new Set(
        items.flatMap((item) => item.tags || [])
    )];
    const suggestedTags = normalizedTagQuery
        ? availableTags
            .filter((tag) => getTagSearchForms(tag).some((form) => (
                form.includes(normalizedTagQuery)
            )))
            .slice(0, 6)
        : [];

    const visibleItems = items
        .filter((item) => {
            if (!normalizedTagQuery) return true;

            return item.tags?.some((tag) => (
                getTagSearchForms(tag).some((form) => (
                    form.includes(normalizedTagQuery)
                ))
            ));
        })
        .sort((firstItem, secondItem) => {
            if (sortMode === "number-desc") {
                return Number(secondItem.problem_number) - Number(firstItem.problem_number);
            }

            if (sortMode === "mastery-asc") {
                return firstItem.mastery_level - secondItem.mastery_level;
            }

            if (sortMode === "mastery-desc") {
                return secondItem.mastery_level - firstItem.mastery_level;
            }

            if (sortMode === "updated-desc") {
                return String(secondItem.updated_at).localeCompare(String(firstItem.updated_at));
            }

            return Number(firstItem.problem_number) - Number(secondItem.problem_number);
        });

    return (
        <section className="review-gallery">
            <div className="review-gallery-actions">
                <button type="button" className="review-gallery-close" onClick={onClose}>
                    <span aria-hidden="true">←</span>
                    返回主页
                </button>
                <button
                    type="button"
                    className="review-gallery-download"
                    onClick={onDownload}
                    aria-label="下载 Excel"
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3v12"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <path d="M5 21h14"></path>
                    </svg>
                    <span>下载 Excel</span>
                </button>
            </div>

            <div className="review-gallery-header">
                <div className="review-gallery-title">
                    <h2>复习卡片</h2>
                    <p>Review Gallery</p>
                </div>
                <div className="review-gallery-tools">
                    <div className="review-tag-search">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                            <circle cx="11" cy="11" r="7"></circle>
                            <path d="m20 20-4-4"></path>
                        </svg>
                        <input
                            type="search"
                            value={tagQuery}
                            onChange={(event) => setTagQuery(event.target.value)}
                            onFocus={() => setIsTagSearchFocused(true)}
                            onBlur={() => setIsTagSearchFocused(false)}
                            placeholder="标签 / 拼音"
                            aria-label="筛选标签"
                        />
                        {isTagSearchFocused && suggestedTags.length > 0 && (
                            <div className="review-tag-suggestions">
                                {suggestedTags.map((tag) => (
                                    <button
                                        type="button"
                                        key={tag}
                                        onMouseDown={(event) => event.preventDefault()}
                                        onClick={() => setTagQuery(tag)}
                                    >
                                        {tag}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <select
                        className="review-sort-select"
                        value={sortMode}
                        onChange={(event) => setSortMode(event.target.value)}
                        aria-label="卡片排序方式"
                    >
                        <option value="number-asc">题号升序</option>
                        <option value="number-desc">题号降序</option>
                        <option value="mastery-asc">遗忘优先</option>
                        <option value="mastery-desc">熟悉优先</option>
                        <option value="updated-desc">最近更新</option>
                    </select>
                    <span className="review-gallery-count">
                        {tagQuery ? `${visibleItems.length} / ${items.length}` : `共 ${items.length} 道题目`}
                    </span>
                </div>
            </div>

            {loading ? (
                <div className="review-gallery-message">正在加载复习卡片...</div>
            ) : error ? (
                <div className="review-gallery-message error">{error}</div>
            ) : items.length === 0 ? (
                <div className="review-gallery-message">还没有保存复习记录。</div>
            ) : visibleItems.length === 0 ? (
                <div className="review-gallery-message">未找到包含该标签的卡片。</div>
            ) : (
                <div className="review-card-grid">
                    {visibleItems.map((item) => (
                        <button
                            type="button"
                            key={item.problem_number}
                            data-review-number={item.problem_number}
                            className={`review-card mastery-level-${item.mastery_level || 0} ${
                                selectedItem?.problem_number === item.problem_number ? "selected" : ""
                            }`}
                            onClick={(event) => openDetail(item, event)}
                        >
                            <span className="review-card-number">
                                LeetCode {item.problem_number}
                            </span>
                            <h3>{item.problem_title}</h3>
                            <div className="review-card-tags">
                                {item.tags?.slice(0, 2).map((tag) => (
                                    <span key={tag}>{tag}</span>
                                ))}
                                {item.tags?.length > 2 && (
                                    <span className="review-card-tag-more">
                                        +{item.tags.length - 2}
                                    </span>
                                )}
                            </div>
                        </button>
                    ))}
                </div>
            )}

            {selectedItem && (
                <div
                    className={`review-detail-backdrop detail-${detailPhase}`}
                    onClick={requestCloseDetail}
                >
                    <article
                        className={`review-detail-card mastery-level-${selectedItem.mastery_level || 0} detail-${detailPhase}`}
                        style={{
                            top: detailRect?.top,
                            left: detailRect?.left,
                            width: detailRect?.width,
                            height: detailRect?.height,
                        }}
                        onClick={(event) => event.stopPropagation()}
                    >
                        <button
                            type="button"
                            className="review-detail-close"
                            onClick={requestCloseDetail}
                            aria-label="关闭详情"
                        >
                            ×
                        </button>

                        <header className="review-detail-header">
                            <span>LeetCode {selectedItem.problem_number}</span>
                            <h3>{selectedItem.problem_title}</h3>
                        </header>

                        <div className="review-detail-tabs" role="tablist">
                            <button
                                type="button"
                                className={detailTab === "solution" ? "active" : ""}
                                onClick={() => setDetailTab("solution")}
                            >
                                解答思路
                            </button>
                            <button
                                type="button"
                                className={detailTab === "useCases" ? "active" : ""}
                                onClick={() => setDetailTab("useCases")}
                            >
                                场景扩展
                            </button>
                        </div>

                        <div className="review-detail-content">
                            {detailTab === "solution" ? (
                                revealedSections.solution ? (
                                    <>
                                        <section>
                                            <h4>题目模式</h4>
                                            <p>{selectedItem.pattern || "暂无题目模式。"}</p>
                                        </section>
                                        <section>
                                            <h4>解题思路</h4>
                                            <p>{selectedItem.solution_approach || "暂无解题思路。"}</p>
                                        </section>
                                    </>
                                ) : (
                                    <button
                                        type="button"
                                        className="review-reveal-button"
                                        onClick={() => setRevealedSections((current) => ({
                                            ...current,
                                            solution: true,
                                        }))}
                                    >
                                        点击显示解答思路
                                    </button>
                                )
                            ) : revealedSections.useCases ? (
                                <section>
                                    <h4>适用场景与扩展</h4>
                                    {selectedItem.use_cases?.length ? (
                                        <ol>
                                            {selectedItem.use_cases.map((useCase, index) => (
                                                <li key={`${selectedItem.problem_number}-${index}`}>
                                                    {useCase}
                                                </li>
                                            ))}
                                        </ol>
                                    ) : (
                                        <p>暂无适用场景。</p>
                                    )}
                                </section>
                            ) : (
                                <button
                                    type="button"
                                    className="review-reveal-button"
                                    onClick={() => setRevealedSections((current) => ({
                                        ...current,
                                        useCases: true,
                                    }))}
                                >
                                    点击显示场景扩展
                                </button>
                            )}
                        </div>

                        <footer className="review-detail-footer">
                            <div className="review-detail-meta">
                                <span>上次复习：{selectedItem.last_viewed || "暂无记录"}</span>
                                <div className="review-detail-tags">
                                    {selectedItem.tags?.map((tag) => (
                                        <span key={tag}>{tag}</span>
                                    ))}
                                </div>
                            </div>

                            <div className={`review-mastery-area ${masteryPromptActive ? "prompt-active" : ""}`}>
                                <span className="review-mastery-label">
                                    {masteryError || "请选择本次复习状态后返回"}
                                </span>
                                <div className="review-mastery-buttons">
                                    <button
                                        type="button"
                                        className="forgotten"
                                        onClick={() => saveMasteryLevel(1)}
                                        disabled={masterySaving}
                                    >
                                        遗忘了
                                    </button>
                                    <button
                                        type="button"
                                        className="vague"
                                        onClick={() => saveMasteryLevel(2)}
                                        disabled={masterySaving}
                                    >
                                        模糊
                                    </button>
                                    <button
                                        type="button"
                                        className="familiar"
                                        onClick={() => saveMasteryLevel(3)}
                                        disabled={masterySaving}
                                    >
                                        熟悉
                                    </button>
                                </div>
                            </div>
                        </footer>
                    </article>
                </div>
            )}
        </section>
    );
};

export default ReviewGallery;
